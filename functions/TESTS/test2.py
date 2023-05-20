import tkinter as tk
from tkinter import Tk, ttk


class Main(Tk):
    def __init__(self):
        super().__init__()

        self.geometry('450x350')

        self.main_frame = ttk.Frame(self)
        self.main_frame.configure(padding=(9, 9, 0, 9))
        self.main_frame.pack(fill='both', expand=1)

        canvas = tk.Canvas(self.main_frame, width=150, height=150)
        canvas.create_oval(10, 10, 20, 20, fill="red")
        canvas.create_oval(200, 200, 220, 220, fill="blue")
        canvas.pack(fill='both')

        scroll_x = tk.Scrollbar(self.main_frame, orient="horizontal", command=canvas.xview)
        scroll_x.pack(side='bottom')

        scroll_y = tk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scroll_y.pack(side='right')

        canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        canvas.configure(scrollregion=canvas.bbox("all"))


if __name__ == '__main__':
    root = Main()
    root.mainloop()
