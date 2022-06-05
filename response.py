from io import BytesIO

from telegram import Update
from telegram.constants import ParseMode

from generator import LongTextException, MemeGenerator, Type

generator = MemeGenerator()
greetings = (
    "<b>Привет!</b>\n\n"
    "Я бот генерирующий <i>drake meme</i> по твоим фразам.\n\n"
    "Поддерживаю следующие форматы сообщений:\n"
    ' — Две строки без префиксов для генерации картинки "Нет" и "Да"\n'
    " — Любое количество строк, но с каждая строка начинается с одного из префиксов да|yes|нет|no|+|-\n\n"
    "Немного подожди и я пришлю тебе готовую картинку!\n\n"
    "Также бот поддерживает работу с группами и супергруппами, но его нужно сделать админом и указывать тег #drake в начале сообщения!\n\n\n"
    "<i>И не забывай что переносы строк разделяют фразы на пару картинок!</i>\n\n"
)


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
        await update.effective_chat.send_message(f"<b>Бип-бип:</b> {e}", parse_mode=ParseMode.HTML)
        print(e)
