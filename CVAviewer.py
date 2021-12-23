import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.filedialog
import ctypes
import string
from MyWidgets_FileTree import FileTree
from MyWidgets_MatplotTk import MatplotTk
from process import ProcessFile
import pandas as pd


class ButtonWithCheck(tk.Button):

    def __cmd(self):
        self.__command(self.__onesheet.get())

    def __init__(self, master, **kwargs):
        self.__command = kwargs.get('command')

        kwargs['command'] = self.__cmd
        kwargs['text'] = "Сохранить"
        kwargs['anchor'] = "w"
        kwargs['padx'] = 10
        kwargs['pady'] = 3
        kwargs['height'] = 2
        super().__init__(master, **kwargs)
        self.__onesheet = tk.BooleanVar()
        self.__onesheet.set(1)
        tc = tk.Checkbutton(self, text="на один лист", variable=self.__onesheet, onvalue=1, offvalue=0, padx=10, pady=3)
        tc.pack(side=tk.RIGHT)


class TextWithScroll(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        xscrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky='we')

        yscrollbar = tk.Scrollbar(self)
        yscrollbar.grid(row=0, column=1, sticky='ns')

        self.text = tk.Text(self, wrap=tk.NONE,
                            width=40,
                            xscrollcommand=xscrollbar.set,
                            yscrollcommand=yscrollbar.set)
        self.text.grid(row=0, column=0, sticky='news')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        xscrollbar.config(command=self.text.xview)
        yscrollbar.config(command=self.text.yview)


class App(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.attributes('-fullscreen', True)
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)

        self.file = None
        self.output = dict()
        self.mass = 1
        width = int(.8 * self.winfo_screenwidth())  # get your Windows width size
        height = int(.8 * self.winfo_screenheight())  # get your Windows height size
        parent.geometry("%dx%d" % (width, height))

        fexplorer = FileTree(parent, self.plot)
        fexplorer.grid(row=0, column=0, sticky='news')
        self.fexplorer = fexplorer
        # fexplorer.grid_columnconfigure(0, weight=1)

        self.canvas = MatplotTk(parent)
        self.canvas.grid(row=0, column=1, sticky='news')
        self.ax = None

        rightFrame = tk.Frame(parent)                   # , bg='red')
        rightFrame.grid(row=0, column=2, sticky='news')

        self._mass = tk.DoubleVar()
        m_label = tk.Label(rightFrame, text="Масса, г:", anchor="e", padx=10)
        m_entry = ttk.Entry(rightFrame, textvariable=self._mass)
        self._mass.set(1)
        m_reculc = tk.Button(rightFrame, text="Пересчитать", command=self.reculc, padx=10, pady=3)
        all_dir = tk.Button(rightFrame, text="Всю папку", command=self.allDir, padx=10, pady=3)

        m_label.grid(row=0, column=0, sticky='ew')
        m_entry.grid(row=0, column=1, sticky='ew')
        m_reculc.grid(row=1, column=0, columnspan=2, sticky='ew')
        all_dir.grid(row=2, column=0, columnspan=2, sticky='ew')

        textFrame = TextWithScroll(rightFrame)
        self.text = textFrame.text
        textFrame.grid(row=3, column=0,columnspan=2, sticky='news')

        save_result = ButtonWithCheck(rightFrame, command=self.save)
        save_result.grid(row=4, column=0, columnspan=2, sticky='ew')

        rightFrame.grid_rowconfigure(3, weight=1)
        rightFrame.grid_columnconfigure(0, weight=1)
        rightFrame.grid_columnconfigure(1, weight=1)

        parent.grid_columnconfigure(0, weight=2)
        parent.grid_columnconfigure(1, weight=10)
        parent.grid_columnconfigure(2, weight=1)

        parent.grid_rowconfigure(0, weight=1)

    def allDir(self):
        path = self.fexplorer.selected_dir()
        if not path:
            return
        self.text.delete(1.0, tk.END)
        self.output = {}
        listdir = list(os.listdir(path))
        for file in listdir:
            if file.endswith('.txt'):
                self.plot(os.path.join(path, file), False)

    def reculc(self):
        if self.file is None:
            return
        try:
            m = float(self._mass.get())
        except:
            messagebox.showwarning(title='Неверно указана масса',
                                   message='Поле масса должно содержать число с десятичной точкой')
            return

        self.mass = m
        self.plot(self.file)

    def plot(self, file, clear=True):
        self.file = file

        if not self.ax:
            self.ax = self.canvas.figure.add_subplot(111)

        self.ax.clear()
        if clear:
            self.text.delete(1.0, tk.END)
            self.output = {}
            at = 1.0
        else:
            at = tk.END

        try:
            process = ProcessFile(file, self.mass, 0, self.ax)
            constant = process.constant
            title = f'{file}, масса = {self.mass} g{constant}'
            self.text.insert(at, f'{title}\n{process}\n')
            self.output[title] = process.resFile
        except:
            self.text.insert(at, 'Неизвестный тип файла')

        self.ax.legend()
        self.canvas.show()

    def save(self, onesheet):
        if not (hasattr(self, 'output') and self.output):
            return

        file_name = tkinter.filedialog.asksaveasfilename(
            defaultextension=(("excell files", "*.xlsx"),),
            initialfile="Result.xlsx",
            title="Выберите файл",
        )
        if not file_name:
            return
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter', mode='w')
        if onesheet:
            #worksheet = writer.book.add_worksheet('results')
            row = 0
            for sheet, dataframe in self.output.items():
                _, file = os.path.split(sheet.split(',')[0])
                dataframe.set_index('cycle').to_excel(writer, sheet_name='results', startrow=row+2, startcol=0)
                writer.sheets['results'].write(row, 0, sheet)
                row += len(dataframe) + 5
        else:
            for sheet, dataframe in self.output.items():
                _, file = os.path.split(sheet.split(',')[0])
                dataframe.set_index('cycle').to_excel(writer, sheet_name=file, startrow=2, startcol=0)
                writer.sheets[file].write(0, 0, sheet)
        writer.save()


if __name__ == '__main__':

    def resource_path(relative_path):
        # Получаем абсолютный путь к ресурсам.
        try:
            # PyInstaller создает временную папку в _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    root = tk.Tk()
    App(root).grid()
    # root.resizable(False, False)
    root.title('Cyclic Voltammetry Viewer .8.1')

    image = resource_path(r'CVAviewer.png')
    root.iconphoto(False, tk.PhotoImage(file=image))

    root.mainloop()
