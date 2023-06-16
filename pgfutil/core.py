from PIL import Image


class Image2Font:
    FIRST_CHAR = 32
    TOTAL_CHARS = 105
    DIACRITIC_MARKS = 8

    LAYOUT_COLS = 16
    LAYOUT_ROWS = 8

    BLACK = (0, 0, 0, 255)
    WHITE = (255, 255, 255, 0)

    def __init__(self, font_data):
        self.load_bytes(font_data)

    @staticmethod
    def new_font(width, height):
        data = []
        bytes_per_column = 2 if width > 8 else 1
        data.append(width)
        data.append(height)
        data += [0 for _ in range(Image2Font.TOTAL_CHARS)]  # Widths
        data += [0 for _ in range(Image2Font.TOTAL_CHARS * width * bytes_per_column)]
        data += [0 for _ in range(8 * ((width * bytes_per_column) + 2))]

    def load_bytes(self, font_data):
        font_data = list(font_data)

        self.CHAR_HEIGHT = font_data[0]
        self.CHAR_WIDTH = font_data[1]
        self.bytes_per_column = 2 if self.CHAR_WIDTH > 8 else 1

        chars_start = 1 + 1 + self.TOTAL_CHARS
        chars_end = chars_start + (self.TOTAL_CHARS * self.CHAR_WIDTH * self.bytes_per_column)

        self.WIDTH_DATA = font_data[2:self.TOTAL_CHARS + 2]
        self.CHAR_DATA = font_data[chars_start:chars_end]
        self.ACCENT_DATA = font_data[chars_end:]

        self._font_image = Image.new("RGBA", (self.width(), self.height()), color=self.WHITE)

        self.font2image()

    @property
    def char_size(self):
        return self.CHAR_WIDTH + 1, self.CHAR_HEIGHT + 1

    @property
    def font_data(self):
        data = []
        data.append(self.CHAR_HEIGHT)
        data.append(self.CHAR_WIDTH)
        data += self.WIDTH_DATA
        data += self.CHAR_DATA
        data += self.ACCENT_DATA
        return data

    @property
    def font_image(self):
        return self._font_image.convert("RGBA")

    def save_data(self, filename):
        if filename.endswith(".bitmapfont"):
            with open(filename, "wb") as f:
                f.write(bytes(self.font_data))
        else:
            self.font2image()
            self._font_image.convert("RGBA").save(filename)

    def load_data(self, filename):
        if filename.endswith(".bitmapfont"):
            self.load_bytes(open(filename, "rb").read())
        else:
            #pal = Image.new("P", (1, 1))
            #pal.putpalette(b"\x00\x00\x00\xff\xff\xff\xff\x00")
            self._font_image = Image.open(filename) #.quantize(2, palette=pal).convert("RGBA")

            w, h = self._font_image.size
            self.CHAR_WIDTH = (w // self.LAYOUT_COLS) - 1
            self.CHAR_HEIGHT = (h // self.LAYOUT_ROWS) - 1

            print(f"Loading image {w}x{h}, Char size {self.CHAR_WIDTH}x{self.CHAR_HEIGHT}")

            self.bytes_per_column = 2 if self.CHAR_WIDTH > 8 else 1

            self.WIDTH_DATA = [0 for _ in range(self.TOTAL_CHARS)]
            self.CHAR_DATA = [0 for _ in range(self.CHAR_WIDTH * self.bytes_per_column * self.TOTAL_CHARS)]
            self.ACCENT_DATA = [0 for _ in range((self.CHAR_WIDTH + 2) * 8)]

            self.image2font()

    def width(self):
        return (self.CHAR_WIDTH + 1) * self.LAYOUT_COLS

    def height(self):
        return (self.CHAR_HEIGHT + 1) * self.LAYOUT_ROWS

    def putpixel(self, xy, pen):
        self._font_image.putpixel(xy, pen)
        self.image2font()

    def fill(self, pen):
        w, h = self._font_image.size
        for y in range(h):
            for x in range(w):
                self._font_image.putpixel((x, y), pen)

    def font2image(self):
        for c in range(self.TOTAL_CHARS):
            x = (c % 16) * (self.CHAR_WIDTH + 1)
            y = (c // 16) * (self.CHAR_HEIGHT + 1)
            o = c * self.CHAR_WIDTH * self.bytes_per_column
            data = self.CHAR_DATA[o:o + (self.CHAR_WIDTH * self.bytes_per_column)]
            self.draw_char(x, y, data, self.CHAR_HEIGHT)

        for a in range(self.DIACRITIC_MARKS):
            data = self.ACCENT_DATA[a * (self.CHAR_WIDTH + 2) + 2:]
            self.draw_char(a * (self.CHAR_WIDTH + 1), 7 * (self.CHAR_HEIGHT + 1), data, 8)

    def image2font(self):
        # Printable characters
        for c in range(self.TOTAL_CHARS):
            x = (c % 16) * (self.CHAR_WIDTH + 1)
            y = (c // 16) * (self.CHAR_HEIGHT + 1)
            o = c * self.CHAR_WIDTH * self.bytes_per_column
            char_data = self.get_char(x, y, self.CHAR_HEIGHT)
            self.CHAR_DATA[o:o + (self.CHAR_WIDTH * self.bytes_per_column)] = char_data
            width = self.CHAR_WIDTH

            if self.bytes_per_column == 2:
                char_data = [sum(char_data[i:i + 2]) for i in range(0, len(char_data), 2)]

            # Figure out character widths by counting back from the right-hand edge until we find a non-clear char
            if c > 0:
                for col in reversed(char_data):
                    if col == 0:
                        width -= 1
                    else:
                        break
                self.WIDTH_DATA[c] = width
            else:
                self.WIDTH_DATA[c] = int(self.CHAR_WIDTH // 2) # TODO: Make space width user configurable

        for a in range(self.DIACRITIC_MARKS):
            o = a * (self.CHAR_WIDTH + 2)
            self.ACCENT_DATA[o:o + self.CHAR_WIDTH] = self.get_char(a * (self.CHAR_WIDTH + 1), 7 * (self.CHAR_HEIGHT + 1), 8)

    def get_char(self, x, y, height):
        bytes_per_column = 2 if height > 8 else 1
        data = [0 for _ in range(self.CHAR_WIDTH * bytes_per_column)]
        for cx in range(0, self.CHAR_WIDTH):
            for cy in range(0, height):
                p = self._font_image.getpixel((x + cx, y + cy)) == self.BLACK
                if bytes_per_column == 2:
                    data[cx * 2 + (cy < 8)] |= p << (cy % 8)
                else:
                    data[cx] |= p << cy
        return data

    def draw_char(self, x, y, data, height):
        bytes_per_column = 2 if height > 8 else 1
        for cx in range(0, self.CHAR_WIDTH):
            if bytes_per_column == 2:
                column = (data[cx * 2] << 8) | data[cx * 2 + 1]
            else:
                column = data[cx]
            for cy in range(0, height):
                p = (column & (1 << cy))
                self._font_image.putpixel((x + cx, y + cy), self.BLACK if p else self.WHITE)