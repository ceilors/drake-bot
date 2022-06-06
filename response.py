from io import BytesIO
from random import choice

from telegram import Update
from telegram.constants import ParseMode

from generator import LongTextException, MemeGenerator, Type

generator = MemeGenerator()
greetings = """<b>Привет!</b>

Я бот генерирующий <i>drake meme</i> по твоим фразам.

Поддерживаю следующие форматы сообщений:
— Две строки в одном сообщении для генерации картинки "Нет" и "Да"
— Любое количество строк, где каждая начинается с <b>да</b> | <b>yes</b> | <b>нет</b> | <b>no</b> | <b>+</b> | <b>-</b>

Немного подожди и я пришлю тебе готовую картинку!

Также меня можно использовать в группах и супергруппах, но мне нужны админские права!
После добавления можешь обращаться за мемом с помощью тега #drake в начале сообщения.

<i>И не забывай что переносы строк разделяют фразы на пару картинок!</i>"""


async def start(update: Update, context):
    await update.effective_chat.send_message(greetings, parse_mode=ParseMode.HTML)


class ParseError(Exception):
    pass


def parse_msg(message, chat_type):
    lines = []
    match chat_type:
        case "private":
            lines = [parse_line(l) for l in message.split("\n")]
        case "supergroup" | "group":
            hash_tag = "#drake"
            if message.startswith(hash_tag):
                lines = [parse_line(l) for l in message[len(hash_tag) :].strip().split("\n")]
            else:
                return []
    l = len(lines)
    if l < 2:
        raise ParseError("Дрейку надо не меньше двух строк")
    if l == 2:
        fst, snd = lines
        if fst[0] == Type.UNKNOWN:
            fst[0] = Type.NO
        if snd[0] == Type.UNKNOWN:
            snd[0] = Type.YES
    else:
        for l in lines:
            if l[0] == Type.UNKNOWN:
                raise ParseError(f'Дрейк не определился с эмоциями для "{l[1]}"')
    return lines


def parse_line(s):
    yes = ["yes", "да", "+"]
    no = ["no", "нет", "-"]

    head, *tail = s.split(maxsplit=1)
    rest = tail[0] if tail else ""
    if head in yes:
        return [Type.YES, rest]
    if head in no:
        return [Type.NO, rest]
    return [Type.UNKNOWN, s]


async def msg(update: Update, context):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type

    try:
        message = parse_msg(update.message.text, chat_type)
        if not message:
            return
        img = generator.generate(message=message)
        photo = BytesIO()
        img.save(photo, format="png")
        photo.seek(0)
        await update.effective_chat.send_photo(photo)
    except Exception as e:
        await update.effective_chat.send_message(f"<b>Бип-буп:</b> {e}", parse_mode=ParseMode.HTML)
        print(e)
