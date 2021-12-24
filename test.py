import tkinter as tk
from tkinter import font


class ExampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        t = SimpleTable(self, 10, 7, self._fill_cell)
        t.grid(row=0, column=0, sticky="news")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # t.set(0, 0, "Hello, world")

    @staticmethod
    def _fill_cell(master, row=0, column=0):
        f = font.nametofont('TkDefaultFont')
        a = f.actual()
        bold = f"\"{a['family']}\" {a['size']} bold"

        up = tk.Label(master, text=f'{row}')
        down = tk.Label(master, text=f'{column}', font=bold)
        up.grid(row=0, column=0)
        down.grid(row=1, column=0)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(0, weight=1)


class SimpleTable(tk.Frame):
    def __init__(self, parent, rows=10, columns=7, fill_cell=None):
        # use black background so it "peeks through" to 
        # form grid lines
        tk.Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                cell = tk.Frame(self)  # , relief='groove', borderwidth=3)
                cell.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                fill_cell(cell, row, column)
                current_row.append(cell)
            self._widgets.append(current_row)

            self.grid_rowconfigure(row, weight=1)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)


if __name__ == "__main__":
    app = ExampleApp()
    app.mainloop()