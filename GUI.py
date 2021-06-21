import tkinter
from PIL import Image, ImageTk
from tkinter import Canvas, Button, Tk


class Interface:
    """
    This class attempts to present a graphical sketch of what is going on
    during the process of doing the puzzle.
    """
    def __init__(self, n):
        # Variables
        self.counter = -1
        self.item_size = int(600 / n)
        self.starting_x = 50
        self.starting_y = 50
        self.font = "Helvetica 16 bold italic"
        self.boards = []
        self.board_size = n
        self.index = 0

        # Components
        self.root = Tk()
        self.canvas = Canvas(self.root, height=600, width=650)

        self.nb = Button(self.root, text='NEXT', command=self.update_gui, font=self.font)
        self.jb = Button(self.root, text='JUMP TO END', command=self.jump_to_last, font=self.font)

        # Images
        self.Unit = Image.open("Images\\Unit.png").resize((self.item_size, self.item_size),
                                                          Image.ANTIALIAS)
        self.U = ImageTk.PhotoImage(master=self.canvas, image=self.Unit)

        self.arrange_component()

    def display(self):
        self.root.mainloop()

    def arrange_component(self):
        self.canvas.pack()
        self.nb.pack(padx=0, pady=10, side=tkinter.LEFT)
        self.jb.pack(padx=0, pady=10, side=tkinter.LEFT)

    def update_canvas(self, board):
        # Clearing canvas
        self.canvas.delete("all")

        changed_row = board.pop(0)
        changed_column = board.pop(0)
        # Drawing items on the canvas
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.canvas.create_image(self.starting_x + j * self.item_size,
                                         self.starting_y + i * self.item_size,
                                         image=self.U)
                value = board.pop(0)
                value_text = '' if value == -1 else str(value)
                self.canvas.create_text(self.starting_x + j * self.item_size - int(self.item_size / 4),
                                        self.starting_y + i * self.item_size, text=value_text, font=self.font)
                value = board.pop(0)
                value_text = '' if value == -1 else str(value)
                self.canvas.create_text(self.starting_x + j * self.item_size + int(self.item_size / 4),
                                        self.starting_y + i * self.item_size - int(self.item_size / 4),
                                        text=value_text)
                value = board.pop(0)
                value_text = '' if value == -1 else str(value)
                self.canvas.create_text(self.starting_x + j * self.item_size + int(self.item_size / 4),
                                        self.starting_y + i * self.item_size + int(self.item_size / 4),
                                        text=value_text)
        if changed_row != -1:
            self.canvas.create_rectangle(self.starting_x + int((changed_column - 0.5) * self.item_size),
                                         self.starting_y + int((changed_row - 0.5) * self.item_size),
                                         self.starting_x + int((changed_column + 0.5) * self.item_size),
                                         self.starting_y + int((changed_row + 0.5) * self.item_size),
                                         width=4, outline='red')

    def jump_to_last(self):
        self.index = len(self.boards) - 1
        self.nb['state'] = 'disabled'
        self.jb['state'] = 'disabled'
        self.update_gui()

    def update_gui(self):
        self.update_canvas(self.boards.pop(self.index))
        if len(self.boards) == 0:
            self.nb['state'] = 'disabled'
            self.jb['state'] = 'disabled'
