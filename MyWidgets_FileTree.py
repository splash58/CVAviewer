import os
import tkinter as tk
import tkinter.ttk as ttk
import ctypes


class FileTree(tk.Frame):


    class FileExplorer(ttk.Treeview):

        dir_img = """
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAABGdB
        TUEAALGPC/xhBQAAAAlwSFlzAAAScgAAEnIBXmVb4wAAAihJREFU
        OE990vtv0kAcAPDh4wd/8w/yp5n4i4kkmizoBMKcRIfG7YepWSSZ
        MSTGSXQao8wtjIw5ZkJEJ4+O0CGvoWhSCmw0sFJaHoU+GEJbyDax
        EwMjQS+Xy30v97m7791JOF4Y+FMOBEJsj508PXD8lERyoj3Yp4ig
        XclNRSlyg0F0TFxLRbXFyAMqaarkQrXabmfO4eqdoBRWtgQnujGM
        +DRVbIYnTU3Wvrf7hcubGRToTOsFvK3V/JZyy6KeCXL7CZc3CEVj
        k7bTO85/A+FDgwr6rKNIQEtu6XnC0Ch/+j+wCSXXulke994vxh/X
        sNkGaaXTfXfYVLbEIwk2gbQBpstxz0QOmq6mdXxxmUr1A8Wg4i8o
        rLoWh2C3hvhxr5KcqhMLVMrRJ4eCX97irL/qFh6fdxkvQoAaj4yz
        iTv17KsyYu8D8t7hg+q7fXahjr50GaWQawT7OkbDN3/u6JIflQxb
        qXN8zzsQniv7tGGv9Czx/tz64gXIqcTCagoaqWxpcO/dKBzL4oTI
        uu+QBYaaBX2DeBgyDoJmKQzIMyEVE5Wz8HXMO7W29tnnD8TiiS5A
        HbIGPi1kJn3zZzdWLh2CoIKGZHRUlXJPzs29XVoy40SuC6p0lgyo
        +PS4e/aM8835GHALDWvY2LVybAxcVs881XtAUEyjC8SEGPx7bfu2
        4/mgzfwiEgSz4dcJixRxjq5YVtEM1r6oHiDGuP9RwHS1TOaP/tCj
        /d+VL1STn8NNZQAAAABJRU5ErkJggg==
        """

        def __init__(self, master, callback, startpath=None, **kwargs):
            super().__init__(master,  **kwargs)  # show="tree",
            self.callback = callback
            self.column("#0", minwidth=10,  stretch=True)
            self.load(startpath)
            self.bind('<<TreeviewOpen>>', self.open_node)
            self.bind("<<TreeviewSelect>>", self.print_selection)

        def load(self, startpath=None):
            for i in self.get_children():
                self.delete(i)

            self.dir_image = tk.PhotoImage(data=self.dir_img)

            drives = self._GetLogicalDriveStringsA()
            self.nodes = dict()
            for drive in drives:
                abspath = drive.upper()
                self.insert_node('', abspath, abspath)

            if startpath:
                path = os.path.realpath(startpath)
                folders = []
                while 1:
                    path, folder = os.path.split(path)

                    if folder != "":
                        folders.append(folder)
                    elif path != "":
                        folders.append(path)
                        break
                folders = list(reversed(folders))
                point = None

                for d in folders:
                    children = self.get_children(point)
                    for i in children:
                        if self.item(i)['text'] == d:
                            self.focus(i)
                            self.open_node()
                            self.item(i, open=True)
                            point = i
                            self.selection_set(i)
                            self.see(children[-1])
                            self.see(i)
                            break
                    else:
                        break

        def insert_node(self, parent, text, abspath):
            if os.path.isdir(abspath):
                node = self.insert(parent, 'end', text=text, open=False, image=self.dir_image)
                self.nodes[node] = abspath
                self.insert(node, 'end')
            else:
                if text.endswith('.txt'):
                    self.insert(parent, 'end', text=text, open=False)

        def open_node(self, event=None):
            directory = self.focus()
            level = 0
            parent = directory
            while parent:
                level += 1
                parent = self.parent(parent)

            abspath = self.nodes.pop(directory, None)
            if abspath:
                self.delete(self.get_children(directory))
                listdir = list(os.listdir(abspath))
                listdir.sort(key=lambda x: (-os.path.isdir(os.path.join(abspath, x)), x))
                maxEntry = 10
                for entry in listdir:
                    maxEntry = max(maxEntry, len(entry))
                    self.insert_node(directory, entry, os.path.join(abspath, entry))
                self.column("#0", minwidth=int(6*maxEntry + 22*level), stretch=True)

        def path_to(self, selection):
            path = [self.item(selection)['text']]
            parent = self.parent(selection)
            while parent:
                path.append(self.item(parent)['text'])
                parent = self.parent(parent)
            return os.path.join(*reversed(path))

        def print_selection(self, event):
            selection = self.selection()[0]
            a = self.get_children(selection)
            if self.get_children(selection):
                return
            path = self.path_to(selection)
            if not os.path.isdir(path):
                self.callback(path)

        def _GetLogicalDriveStringsA(self):

            def RaiseIfZero(result, func=None, arguments=()):
                """
                Error checking for most Win32 API calls.
                The function is assumed to return an integer, which is C{0} on error.
                In that case the C{WindowsError} exception is raised.
                """
                if not result:
                    raise ctypes.WinError()
                return result

            DWORD = ctypes.c_uint32
            LPSTR = ctypes.c_char_p

            _GetLogicalDriveStringsA = ctypes.windll.kernel32.GetLogicalDriveStringsA
            _GetLogicalDriveStringsA.argtypes = [DWORD, LPSTR]
            _GetLogicalDriveStringsA.restype = DWORD
            _GetLogicalDriveStringsA.errcheck = RaiseIfZero

            nBufferLength = (4 * 26) + 1  # "X:\\\0" from A to Z plus empty string
            lpBuffer = ctypes.create_string_buffer(nBufferLength)
            _GetLogicalDriveStringsA(nBufferLength, lpBuffer)
            drive_strings = list()
            string_p = ctypes.addressof(lpBuffer)
            sizeof_char = ctypes.sizeof(ctypes.c_char)
            while True:
                string_v = ctypes.string_at(string_p)
                if string_v == b'':
                    break
                drive_strings.append(string_v.decode("utf-8"))
                string_p += len(string_v) * sizeof_char + sizeof_char
            return drive_strings

    def __init__(self, frame, callback, startpath="", **kwargs):
        super().__init__(frame, **kwargs)

        self.config(height=40, width=40)
        tree = self.FileExplorer(self, callback, startpath, selectmode="browse")
        self.tree = tree
        ysb = ttk.Scrollbar(self, orient='vertical', command=tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=tree.xview)

        tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        tree.heading('#0', text='<перегрузить>',  anchor='w', command=self.reload)

        ysb.pack(side='right', fill='y')
        xsb.pack(side='bottom', fill='x')
        tree.pack(fill="both", expand=True)

    def reload(self):
        path = self.tree.selection()
        if path:
            path = self.tree.path_to(path[0])
            self.tree.load(path)
        else:
            self.tree.load()

    def selected_dir(self):
        path = self.tree.selection()
        if path:
            path = self.tree.path_to(path[0])
            if not os.path.isdir(path):
                path, _ = os.path.split(path)
            return path



if __name__ == "__main__":
    def f(x):
        pass
    app = tk.Tk()
    m = FileTree(app, f)  #  r'c:\Work\preview'
    m.grid()

    app.mainloop()
