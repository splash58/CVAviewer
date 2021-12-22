import os
import tkinter as tk
import tkinter.ttk as ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
matplotlib.use('TkAgg')


class MatplotTk(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.widget = None
        self.createWidgets()

    def __getattr__(self, attribute):
        return getattr(self.widget, attribute)

    def createWidgets(self):
        self.figure = Figure(figsize=(5, 5), dpi=100)
        # fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(fill="both", expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        toolbar.children['!button2'].pack_forget()
        toolbar.children['!button3'].pack_forget()
        # self.canvas.draw()

    def plot(self, y, x=None):
        ax = self.figure.add_subplot(111)
        ax.clear()         # clear axes from previous plot
        if x:
            ax.plot(x, y, 'o-')
        else:
            ax.plot(y, 'o-')
        self.canvas.draw()


if __name__ == "__main__":
    pass
