import enum
import textwrap
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFont

import error


@dataclass
class Item:
    msg_type: Type
    is_link: bool
    message: str | Image.Image


class MemeGenerator:
    def __init__(self):
        resource = Path("./resources/")
        font01 = str(resource / "Caveat-Bold.ttf")
        font02 = str(resource / "Spectral-Medium.ttf")

        self.drake_yes = Image.open(resource / "drake-yes-small.png")
        self.drake_no = Image.open(resource / "drake-no-small.png")
        self.drake_size = self.drake_yes.size

        self.big_font = ImageFont.truetype(font01, size=150)
        self.medium_font = ImageFont.truetype(font01, size=90)
        self.small_font = ImageFont.truetype(font01, size=48)
        self.tiny_font = ImageFont.truetype(font01, size=32)
        self.extra_font = ImageFont.truetype(font02, size=34)

        self.black_color = (0, 0, 0)
        self.white_color = (255, 255, 255)

        self.logo = Image.open(resource / "logo-small.png")
        self.logo_bg = (0x0D, 0x3C, 0xA7)
        self.logo_text = "@drake_meme_bot — https://github.com/ceilors/drake-bot"

    def generate_image(self, meme="drake", links=None):
        meme_images = self.memes.get(meme)
        if not meme_images:
            raise error.NoSuchMemeException("Такого мема у меня нет")
        max_height = self.meme_images[0].size[1]
        max_width = 0

        message_count = len(items)
        magic_text_size_number, font = self.select_font(items)

        # заглушка для тестового рендеринга
        img = Image.new(mode="RGB", size=(0, 0))
        drw = ImageDraw.Draw(img)

        # подгружаем изображения и считаем размеры
        for item in items:
            if item.is_link:
                result = Image.open(urlopen(item.message))
                width, height = result.size
                if height > max_height:
                    ratio = width / height
                    width = int(ratio * max_height)
                    result = result.resize((width, max_height))
                max_width = max(max_width, self.drake_size[0] + result.size[0])
                item.message = result
            else:
                text = "\n".join(textwrap.wrap(item.message, width=magic_text_size_number))
                w, _ = drw.textsize(text, font=font)
                max_width = max(max_width, self.drake_size[0] + w + x_border * 2)

        max_height = message_count * self.drake_size[1] + self.logo.size[1]
        right_width = max_width - self.drake_size[0]
        # создаём картинку
        img = Image.new(mode="RGB", size=(max_width, max_height), color=self.white_color)
        drw = ImageDraw.Draw(img)

        # рендеринг контент
        y_index = 0
        for item in items:
            drake = self.drake_no if item.msg_type is Type.NO else self.drake_yes
            img.paste(drake, box=(0, y_index))

            if item.is_link:
                x_shift = (right_width - item.message.size[0]) // 2
                y_shift = (self.drake_size[1] - item.message.size[1]) // 2
                img.paste(item.message, box=(x_shift + self.drake_size[0], y_shift + y_index))
            else:
                text = "\n".join(textwrap.wrap(item.message, width=magic_text_size_number))
                w, h = drw.textsize(text, font=font)
                x_text_align = self.drake_size[0] + (right_width - w) // 2
                y_text_align = y_index + (self.drake_size[1] - h) // 2
                drw.text(
                    xy=(x_text_align, y_text_align),
                    text=text,
                    fill=self.black_color,
                    font=font,
                )

            y_index += self.drake_size[1]

        # добавляем футер
        drw.rectangle(
            xy=(0, y_index, max_width, y_index + self.logo.size[0]),
            fill=self.logo_bg,
        )
        img.paste(self.logo, box=(0, y_index))
        w, h = drw.textsize(self.logo_text, font=self.big_font)
        xy = (self.logo.size[0] + 10, y_index - 2)
        drw.text(xy=xy, text=self.logo_text, fill=self.white_color, font=self.extra_font)

        # и сохраняем картинку в BytesIO
        photo = BytesIO()
        img.save(photo, format="png")
        photo.seek(0)

        return photo
