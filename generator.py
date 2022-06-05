import enum
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class Type(enum.Enum):
    UNKNOWN = None
    YES = True
    NO = False


class LongTextException(Exception):
    pass


class MemeGenerator:
    def __init__(self):
        resource = Path("./resources/")
        font01 = str(resource / "Caveat-Bold.ttf")
        font02 = str(resource / "Spectral-Medium.ttf")

        self.drake_yes = Image.open(resource / "drake-yes-small.png")
        self.drake_no = Image.open(resource / "drake-no-small.png")
        self.drake_size = self.drake_yes.size

        self.big_font = ImageFont.truetype(font01, size=150)
        self.medium_font = ImageFont.truetype(font01, size=100)
        self.small_font = ImageFont.truetype(font01, size=48)
        self.extra_font = ImageFont.truetype(font02, size=34)

        self.black_color = (0, 0, 0)
        self.white_color = (255, 255, 255)

        self.logo = Image.open(resource / "logo-small.png")
        self.logo_bg = (0x0D, 0x3C, 0xA7)
        self.logo_text = "drakeposting meme made by @drake_meme_bot: https://github.com/ceilors/drake-bot"

    def generate(self, *, message=None, max_width=20):
        # бордер по ширине для шрифта
        x_border = 100

        # выбираем размер шрифта под размер текста
        text_max_len = max([len(text) for _, text in message])
        select_font = None
        if text_max_len <= 200:
            select_font = self.big_font
        elif text_max_len < 300:
            select_font = self.medium_font
        elif text_max_len < 600:
            select_font = self.small_font
        else:
            raise LongTextException("Текст слишком длинный!")

        # расчитываем размер картинки
        height = (len(message)) * self.drake_size[1] + self.logo.size[1]
        width = self.drake_size[0]
        # создаём картинку и объект для рисования
        img = Image.new(mode="RGB", size=(width, height), color=self.white_color)
        drw = ImageDraw.Draw(img)

        # находим самый длинный текст
        f_width, f_height = 0, 0
        for _, text in message:
            text = "\n".join(textwrap.wrap(text, width=max_width))
            w, h = drw.textsize(text, font=select_font)
            f_width = max(f_width, w)
            f_height = max(f_height, h)
        f_width += 2 * x_border
        # ресайзим картинку
        img = img.resize((width + f_width, height))
        # пересоздаём объект для рисования
        drw = ImageDraw.Draw(img)

        # добавляем Дрейков
        y_index = 0
        for t, text in message:
            i = self.drake_no if t is Type.NO else self.drake_yes
            img.paste(i, box=(0, y_index))
            y_index += self.drake_size[1]

        # добавляем лого и текста
        drw.rectangle(
            xy=(0, y_index, width + f_width, y_index + self.logo.size[0]),
            fill=self.logo_bg,
        )
        img.paste(self.logo, box=(0, y_index))
        w, h = drw.textsize(self.logo_text, font=self.big_font)
        xy = (self.logo.size[0] + 10, y_index - 2)
        drw.text(xy=xy, text=self.logo_text, fill=self.white_color, font=self.extra_font)

        # добавляем текст со всякими выравниваниями
        x_index = width
        y_index = (self.drake_size[1] - f_height) // 2
        for _, text in message:
            text = "\n".join(textwrap.wrap(text, width=max_width))
            w, h = drw.textsize(text, font=select_font)
            x_text_align = (f_width - w) // 2
            y_text_align = (f_height - h) // 2
            xy = (x_index + x_text_align, y_index + y_text_align)
            drw.text(
                xy=xy,
                text=text,
                align="center",
                fill=self.black_color,
                font=select_font,
            )
            y_index += self.drake_size[1]

        return img
