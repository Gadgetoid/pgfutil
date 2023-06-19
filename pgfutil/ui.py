from tkinter import HORIZONTAL, Button, Canvas, Scale, Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

from PIL import Image, ImageDraw, ImageTk

from .core import Image2Font


class PGFUtil:
    def __init__(self, scale=6, filename=None):
        self.root = Tk()
        self.root.wm_title("PicoGraphics Font Util")
        self.scale = scale

        self.pen = None
        self.image = None

        self.enable_chessboard = True
        self.enable_onionskin = True

        self.sld_width = Scale(self.root, from_=3, to=16, orient=HORIZONTAL)
        self.sld_width.grid(row=0, column=0)

        self.sld_height = Scale(self.root, from_=3, to=16, orient=HORIZONTAL)
        self.sld_height.grid(row=0, column=1)

        self.btn_new = Button(self.root, text="New", command=self.new)
        self.btn_new.grid(row=0, column=2)

        self.btn_clear = Button(self.root, text="Clear", command=self.clear)
        self.btn_clear.grid(row=0, column=3)

        self.btn_save = Button(self.root, text="Save", command=self.save)
        self.btn_save.grid(row=0, column=4)

        self.btn_load = Button(self.root, text="Load", command=self.load)
        self.btn_load.grid(row=0, column=5)

        self.btn_load_os = Button(self.root, text="Load Onionskin", command=self.load_onionskin)
        self.btn_load_os.grid(row=0, column=6)

        self.c = Canvas(self.root, bg='white')

        if filename:
            self.i2f = Image2Font(filename=filename)
        else:
            self.i2f = Image2Font.new_font(6, 6)

        self.update_onionskin(self.i2f.font_image.copy())
        self.configure_canvas()
        self.c.grid(row=2, columnspan=7)

        self.c.bind('<ButtonPress-1>', self.input_dispatch)
        self.c.bind('<ButtonRelease-1>', self.input_dispatch)
        self.c.bind('<ButtonPress-2>', self.input_dispatch) # macOS two-finger right click
        self.c.bind('<ButtonRelease-2>', self.input_dispatch) # macOS two-finger right click
        self.c.bind('<ButtonPress-3>', self.input_dispatch)
        self.c.bind('<ButtonRelease-3>', self.input_dispatch)
        self.c.bind('<Motion>', self.input_dispatch)

        self.root.mainloop()

    def configure_canvas(self):
        self.update_chessboard()

        self.c.configure(width=self.i2f.width() * self.scale, height=self.i2f.height() * self.scale)
        self.font_photo_image = ImageTk.PhotoImage(self.get_scaled_image())
        if not self.image:
            self.image = self.c.create_image((0, 0), image=self.font_photo_image, state="normal", anchor="nw")
        else:
            self.c.itemconfigure(self.image, image=self.font_photo_image)

    def new(self):
        self.i2f = Image2Font.new_font(
            self.sld_width.get(),
            self.sld_height.get()
        )
        self.onionskin = None
        self.configure_canvas()

    def save(self):
        try:
            filename = asksaveasfilename(defaultextension=".bitmapfont", filetypes=(
                ("Bitmap Font File", "*.bitmapfont"),
                ("Image File", "*.png"),
                ("C Header", "*.h"),
                ("Python File", "*.py"),
                ("All Files", "*.*")))
        except ValueError:
            return
        if filename is None:
            return
        self.i2f.save_data(filename)

    def load(self):
        try:
            filename = askopenfilename(defaultextension=".bitmapfont", filetypes=(
                ("Bitmap Font File", "*.bitmapfont"),
                ("Image File", "*.png"),
                ("All Files", "*.*")))
        except ValueError:
            return
        if filename is None:
            return
        self.i2f.load_data(filename)
        self.update_onionskin(self.i2f.font_image.copy())
        self.configure_canvas()

    def load_onionskin(self):
        try:
            filename = askopenfilename(defaultextension=".bitmapfont", filetypes=(
                ("Bitmap Font File", "*.bitmapfont"),
                ("Image File", "*.png"),
                ("All Files", "*.*")))
        except ValueError:
            return
        if filename is None:
            return
        i2f = Image2Font(filename=filename)
        self.update_onionskin(i2f.font_image.copy())
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
                draw.rectangle((cx, cy, cx + cw - 2, cy + ch - 2), fill=fill)
        print(f"Chessboard {cw}x{ch}")

    def update_onionskin(self, image):
        self.onionskin = image.convert("RGBA")
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

    def input_dispatch(self, event):
        if event.type == "6": # Motion
            self.paint(event)
        if event.type == "4": # Button
            if event.num == 1:
                self.pen_black()
            else:
                self.pen_white()
            self.paint(event)
        if event.type == "5": # ButtonRelease
            self.pen_off()

    def pen_black(self):
        self.pen = (0, 0, 0, 255)

    def pen_white(self):
        self.pen = (255, 255, 255, 0)

    def pen_off(self):
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