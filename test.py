import tkinter as tk


class ExampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        t = SimpleTable(self, 10, 7, self._fill_cell)
        t.pack(side="top", fill="x")
        t.set(0, 0, "Hello, world")

    def _fill_cell(self, master, row=0, column=0):
        label = tk.Label(self, text="%s/%s" % (row, column),
                         borderwidth=0, width=10)
        up = tk.Label()

class SimpleTable(tk.Frame):
    def __init__(self, parent, rows=10, columns=7, fill_cell= None):
        # use black background so it "peeks through" to 
        # form grid lines
        tk.Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                cell = tk.Frame(self)
                cell.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                fill_cell(self)
                current_row.append(cell)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)


if __name__ == "__main__":
    app = ExampleApp()
    app.mainloop()