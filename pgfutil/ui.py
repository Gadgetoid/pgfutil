from tkinter import Button, Canvas, Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

from PIL import Image, ImageTk, ImageDraw


class PGFUtil:
    def __init__(self, i2f, scale=7):
        self.root = Tk()
        self.scale = scale

        self.i2f = i2f

        self.pen = None
        self.image = None

        self.enable_chessboard = True
        self.enable_onionskin = True

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
        self.update_chessboard()
        self.update_onionskin()

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

    def update_chessboard(self):
        cw, ch = self.i2f.char_size
        self.chessboard = Image.new("RGBA", self.i2f.font_image.size)
        draw = ImageDraw.Draw(self.chessboard)
        for y in range(self.i2f.LAYOUT_ROWS):
            for x in range(self.i2f.LAYOUT_COLS):
                cx = x * cw
                cy = y * ch
                fill = (255, 0, 255, 32) if (y + x) % 2 == 0 else (0, 255, 255, 32)
                draw.rectangle((cx, cy, cx + cw, cy + ch), fill=fill)
        print(f"Chessboard {cw}x{ch}")

    def update_onionskin(self):
        self.onionskin = self.i2f.font_image.copy().convert("RGBA")
        w, h = self.onionskin.size
        for y in range(h):
            for x in range(w):
                r, g, b, _ = self.onionskin.getpixel((x, y))
                if (r, g, b) == (255, 255, 255):
                    self.onionskin.putpixel((x, y), (255, 255, 255, 0))
                else:
                    self.onionskin.putpixel((x, y), (0, 0, 0, 50))

    def clear(self):
        self.i2f.fill((255, 255, 255, 0))
        self.configure_canvas()

    def get_scaled_image(self):
        new_image = self.i2f.font_image

        if self.chessboard:
            new_image = Image.alpha_composite(self.chessboard, new_image)
    
        if self.onionskin:
            new_image = Image.alpha_composite(new_image, self.onionskin)

        w, h = new_image.size
        new_image = new_image.resize((w * self.scale, h * self.scale), resample=Image.NEAREST)

        return new_image

    def pen_black(self, event):
        self.pen = (0, 0, 0, 255)
        self.paint(event)

    def pen_white(self, event):
        self.pen = (255, 255, 255, 0)
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