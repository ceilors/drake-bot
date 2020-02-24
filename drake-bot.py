from PIL import ImageDraw, ImageFont, Image
from pathlib import Path
import textwrap


resource= Path('./resources/')
drake_yes = Image.open(resource / 'drake-yes.png')
drake_no = Image.open(resource / 'drake-no.png')
font01 = str(resource / 'Caveat-Bold.ttf')
font02 = str(resource / 'Spectral-Medium.ttf')
big_font = ImageFont.truetype(font01, size=150)
medium_font = ImageFont.truetype(font01, size=100)
small_font = ImageFont.truetype(font01, size=48)
extra_font = ImageFont.truetype(font02, size=48)
drake_size = drake_yes.size
black_color = (0, 0, 0)
white_color = (255, 255, 255)
logo = Image.open(resource / 'logo.png')
logo_bg = (0x0d, 0x3c, 0xa7)
logo_text = 'drakeposting meme made by drake-bot @ https://github.com/ceilors/drake-bot'


def generate(*, for_yes=None, for_no=None, max_width=20):
    # бордер по ширине для шрифта
    x_border = 100

    # выбираем размер шрифта под размер текста
    text_max_len = max([len(text) for text in for_no + for_yes])
    select_font = None
    if text_max_len <= 200:
        select_font = big_font
    elif text_max_len < 300:
        select_font = medium_font
    elif text_max_len < 600:
        select_font = small_font
    else:
        raise ValueError('Text size is too big!')

    # расчитываем размер картинки
    height = (len(for_yes) + len(for_no)) * drake_size[1] + logo.size[1]
    width = drake_size[0]
    # создаём картинку и объект для рисования
    img = Image.new(mode='RGB', size=(width, height), color=white_color)
    drw = ImageDraw.Draw(img)

    # находим самый длинный текст 
    f_width, f_height = 0, 0
    for text in for_no + for_yes:
        text = '\n'.join(textwrap.wrap(text, width=max_width))
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
    for no in for_no:
        img.paste(drake_no, box=(0, y_index))
        y_index += drake_size[1]
    for yes in for_yes:
        img.paste(drake_yes, box=(0, y_index))
        y_index += drake_size[1]

    # добавляем лого и текста
    drw.rectangle(xy=(0, y_index, width + f_width, y_index + logo.size[0]), fill=logo_bg)
    img.paste(logo, box=(0, y_index))
    w, h = drw.textsize(logo_text, font=big_font)
    xy = (logo.size[0] + 10, y_index - 2)
    drw.text(xy=xy, text=logo_text, fill=white_color, font=extra_font)

    # добавляем текст со всякими выравниваниями
    x_index = width
    y_index = (drake_size[1] - f_height) // 2
    for text in for_no + for_yes:
        text = '\n'.join(textwrap.wrap(text, width=max_width))
        w, h = drw.textsize(text, font=select_font)
        x_text_align = (f_width - w) // 2
        y_text_align = (f_height - h) // 2
        xy = (x_index + x_text_align, y_index + y_text_align)
        drw.text(xy=xy, text=text, align='center', fill=black_color, font=select_font)
        y_index += drake_size[1]
    
    return img


if __name__ == '__main__':
    stat_yes = ('Делать бота на Python',)
    stat_no = ('Делать мемы вручную',)
    img = generate(for_yes=stat_yes, for_no=stat_no)
    img.save('result.png')