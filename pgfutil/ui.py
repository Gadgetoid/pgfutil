from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import Image, ImageTk


class PGFUtil:
    def __init__(self, i2f, scale=10):
        self.root = Tk()
        self.scale = scale

        self.i2f = i2f

        self.pen = None
        self.image = None

        self.btn_clear = Button(self.root, text="Clear", command=self.clear)
        self.btn_clear.grid(row=0, column=0)
        self.btn_save = Button(self.root, text="Save", command=self.save)
        self.btn_save.grid(row=0, column=1)
        self.btn_load = Button(self.root, text="Load", command=self.load)
        self.btn_load.grid(row=0, column=2)

        self.c = Canvas(self.root, bg='white')
        self.configure_canvas()
        self.c.grid(row=1, columnspan=3)

        self.c.bind('<ButtonPress-1>', self.pen_black)
        self.c.bind('<ButtonRelease-1>', self.pen_off)
        self.c.bind('<ButtonPress-3>', self.pen_white)
        self.c.bind('<ButtonRelease-3>', self.pen_off)
        self.c.bind('<Motion>', self.paint)

        self.root.mainloop()

    def configure_canvas(self):
        self.c.configure(width=self.i2f.width() * self.scale, height=self.i2f.height() * self.scale)
        self.font_photo_image = ImageTk.PhotoImage(self.get_scaled_image())
        if not self.image:
            self.image = self.c.create_image((0, 0), image=self.font_photo_image, state="normal", anchor="nw")
        else:
            self.c.itemconfigure(self.image, image=self.font_photo_image)

    def save(self):
        filename = asksaveasfilename(defaultextension=".bitmapfont", filetypes=(
            ("Bitmap Font File", "*.bitmapfont"),
            ("Image File", "*.png"),
            ("C Header", "*.h"),
            ("Python File", "*.py"),
            ("All Files", "*.*")))
        self.i2f.save_data(filename)

    def load(self):
        filename = askopenfilename(defaultextension=".bitmapfont", filetypes=(
            ("Bitmap Font File", "*.bitmapfont"),
            ("Image File", "*.png"),
            ("All Files", "*.*")))
        self.i2f.load_data(filename)
        self.configure_canvas()

    def clear(self):
        self.i2f.fill(1)
        self.configure_canvas()

    def get_scaled_image(self):
        return self.i2f.get_scaled(self.scale)

    def pen_black(self, event):
        self.pen = 0
        self.paint(event)

    def pen_white(self, event):
        self.pen = 1
        self.paint(event)

    def pen_off(self, event):
        self.pen = None

    def paint(self, event):
        if self.pen is None:
            return

        ox = int(event.x // self.scale)
        oy = int(event.y // self.scale)

        try:
            self.i2f.putpixel((ox, oy), self.pen)
        except IndexError:
            pass

        self.font_photo_image.paste(self.get_scaled_image())