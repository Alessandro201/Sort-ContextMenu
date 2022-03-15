from tkinter import ttk, Tk
import tkinter as tk
from threading import Thread
from multiprocessing import Queue
from time import sleep


class AskExtensions(Tk):
    def __init__(self, queue):
        super().__init__()

        # Used to handle the information inserted by the user
        self.queue = queue

        self.geometry('450x350')

        self.main_frame = ttk.Frame(self)
        self.main_frame.configure(padding=(9, 9, 0, 9))
        self.main_frame.pack(fill='both', expand=1)

        self.description_label = ttk.Label(self.main_frame)
        self.description_label.configure(text='Here you can decide which extensions will be extracted from the \n'
                                              'main directory. The name you insert here will be added to the \n'
                                              'name of the main directory.')
        self.description_label.pack(side='top', fill='both')

        self.folders_frame = ScrollableFrame(self.main_frame)
        self.folders_frame.pack(side='top', expand=True, fill='both')
        self.folder_inside_frame = self.folders_frame.get_frame_inside()
        self.folder_inside_frame.pack(fill='x')

        self.all_folders = dict()
        self.number_of_folders = 0
        self.add_folder()

        self.buttons_folder = ttk.Frame(self.main_frame)
        self.buttons_folder.pack(side='bottom')

        self.new_folder_button = ttk.Button(self.buttons_folder)
        self.new_folder_button.configure(text='Add new folder', command=self.add_folder)
        self.new_folder_button.pack(side='left')

        self.new_folder_button = ttk.Button(self.buttons_folder)
        self.new_folder_button.configure(text='Okay', command=self.done)
        self.new_folder_button.pack(side='right')

    def add_folder(self):
        folder_number = self.number_of_folders

        single_folder_frame = ttk.Frame(self.folder_inside_frame)
        single_folder_frame.pack(fill='x', expand=True)

        delete_button = ttk.Button(single_folder_frame)
        delete_button.configure(text='-', command=lambda: self.delete_folder(folder_number))
        delete_button.configure(width=2)
        delete_button.grid(row=self.number_of_folders, column=0)

        folder_label = ttk.Label(single_folder_frame)
        folder_label.configure(text='Name:', padding=(7, 1, 1, 1))
        folder_label.grid(row=self.number_of_folders, column=1)

        folder_name_entry = ttk.Entry(single_folder_frame)
        folder_name_entry.grid(row=self.number_of_folders, column=2, sticky='we')

        folder_extensions_label = ttk.Label(single_folder_frame)
        folder_extensions_label.configure(text='Extensions:', padding=(7, 1, 1, 1))
        folder_extensions_label.grid(row=self.number_of_folders, column=3)

        folder_extensions_entry = ttk.Entry(single_folder_frame)
        folder_extensions_entry.grid(row=self.number_of_folders, column=4, sticky='we')

        single_folder_frame.columnconfigure(2, weight=1)
        single_folder_frame.columnconfigure(4, weight=1)

        self.all_folders[self.number_of_folders] = [single_folder_frame,
                                                    delete_button,
                                                    folder_label,
                                                    folder_name_entry,
                                                    folder_extensions_label,
                                                    folder_extensions_entry]

        self.number_of_folders += 1

        self.update()

    def delete_folder(self, folder_number):
        single_folder_frame = self.all_folders[folder_number][0]
        single_folder_frame.destroy()
        del self.all_folders[folder_number]

    def done(self):
        folders = []
        for folder_number in self.all_folders.keys():
            name = self.all_folders[folder_number][3].get()
            extensions = self.all_folders[folder_number][5].get()
            folders.append((name, extensions))

        self.queue.insert(folders)
        self.destroy()


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def get_frame_inside(self):
        return self.scrollable_frame


class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """

    def __init__(self):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """

        # Create the queue
        self.queue = Queue()

        # Set up the GUI part
        self.gui = AskExtensions(self.queue)

        # It's used to end the application
        self.running = True

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.thread1 = Thread(target=self.worker_check_queue)
        self.thread1.start()

        # Start the periodic call in the GUI to check if the queue contains anything
        self.periodically_check_queue()

    def periodically_check_queue(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)

        self.master.after(200, self.periodicCall)

    def worker_check_queue(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following two lines with the real
            # thing.
            sleep(50)
            if not self.queue.empty():
                pass

    def endApplication(self):
        self.running = False


if __name__ == '__main__':
    root = AskExtensions()
    root.mainloop()
