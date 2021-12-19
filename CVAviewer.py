import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import ctypes
import string
from MyWidgets_FileTree import FileTree
from MyWidgets_MatplotTk import MatplotTk
from process import ProcessFile


class App(tk.Frame):

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


    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        #self.attributes('-fullscreen', True)
        #self.columnconfigure(0, weight=1)
        #self.rowconfigure(0, weight=1)

        self.file = None
        self.mass = 1
        width = int(.8 * self.winfo_screenwidth())  # get your Windows width size
        height = int(.8 * self.winfo_screenheight())  # get your Windows height size
        parent.geometry("%dx%d" % (width, height))

        fexplorer = FileTree(parent, self.plot)
        fexplorer.grid(row=0, column=0, sticky='news')
        # fexplorer.grid_columnconfigure(0, weight=1)

        self.canvas = MatplotTk(parent)
        self.canvas.grid(row=0, column=1, sticky='news')
        self.ax = None

        rightFrame = tk.Frame(parent)                   # , bg='red')
        rightFrame.grid(row=0, column=2, sticky='news')

        self._mass = tk.DoubleVar()
        m_label = tk.Label(rightFrame, text="Масса, г:")
        m_entry = tk.Entry(rightFrame, textvariable=self._mass)
        self._mass.set(1)
        m_reculc = tk.Button(rightFrame, text="Пересчитать", command=self.reculc, padx=10, pady=3)

        m_label.grid(row=0, column=0, sticky='ew')
        m_entry.grid(row=0, column=1, sticky='ew')
        m_reculc.grid(row=1, column=0, columnspan=2, sticky='ew')

        # self.text = ScrolledText(rightFrame, width=40, wrap=tk.NONE)
        textFrame = tk.Frame(rightFrame)
        textFrame.grid(row=2, column=0, columnspan=2, sticky='news')

        xscrollbar = tk.Scrollbar(textFrame, orient=tk.HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky='we')

        yscrollbar = tk.Scrollbar(textFrame)
        yscrollbar.grid(row=0, column=1, sticky='ns')

        self.text = tk.Text(textFrame, wrap=tk.NONE,
                            width=40,
                    xscrollcommand=xscrollbar.set,
                    yscrollcommand=yscrollbar.set)
        self.text.grid(row=0, column=0, sticky='news')
        textFrame.grid_rowconfigure(0, weight=1)
        textFrame.grid_columnconfigure(0, weight=1)

        xscrollbar.config(command=self.text.xview)
        yscrollbar.config(command=self.text.yview)

        rightFrame.grid_rowconfigure(2, weight=1)
        rightFrame.grid_columnconfigure(0, weight=1)
        rightFrame.grid_columnconfigure(1, weight=1)

        parent.grid_columnconfigure(0, weight=2)
        parent.grid_columnconfigure(1, weight=10)
        parent.grid_columnconfigure(2, weight=1)

        parent.grid_rowconfigure(0, weight=1)

        #sg = ttk.Sizegrip(self)
        #sg.grid(row=1, column=2, sticky=tk.SE)

        #self.grid_propagate(0)

    def plot(self, file):
        self.file = file

        if not self.ax:
            self.ax = self.canvas.figure.add_subplot(111)

        self.ax.clear()
        self.text.delete(1.0, tk.END)

        try:
            d = str(ProcessFile(file, self.mass, 0, self.ax))
            self.text.insert(1.0, d)
        except:
            self.text.insert(1.0, 'Неизвестный тип файла')

        #self.canvas.plot(list(map(lambda i: i*cnt, y)), list(map(lambda i: i*cnt, x)))
        self.ax.legend()
        self.canvas.figure.tight_layout()
        self.canvas.canvas.draw()



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
