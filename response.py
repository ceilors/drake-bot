from io import BytesIO

from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram import Update

from generator import MemeGenerator, LongTextException, Type


generator = MemeGenerator()
greetings = (
    "<b>Привет!</b>\n\n"
    "Я бот генерирующий <i>drake meme</i> по твоим фразам.\n\n"
    '<i>Сначала</i> отправить сообщение с фразами <b>для шаблона "нет"</b>.\n'
    '<i>Следующим</i> сообщением <b>на шаблон "да"</b>.\n'
    "Немного подожди и я пришлю тебе готовую картинку!\n\n"
    "<i>И не забывай что переносы строк разделяют фразы на пару картинок!</i>"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message(greetings, parse_mode=ParseMode.HTML)


def generate_response(context, chat_id, text_yes, text_no):
    try:
        img = generator.generate(for_yes=text_yes, for_no=text_no)
        photo = BytesIO()
        img.save(photo, format="png")
        photo.seek(0)
        context.bot.send_photo(chat_id, photo=photo)
    except LongTextException:
        context.bot.send_message(
            chat_id=chat_id,
            text="<b>Бип-бип:</b> Текст слишком длинный!",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        context.bot.send_message(
            chat_id=chat_id,
            text="<b>Бип-буп:</b> Что-то пошло не так!",
            parse_mode=ParseMode.HTML,
        )
        print(e)


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
                lines = [
                    parse_line(l) for l in message[len(hash_tag) :].strip().split("\n")
                ]
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

    start, rest = s.split(maxsplit=1)
    if start in yes:
        return [Type.YES, rest]
    if start in no:
        return [Type.NO, rest]
    return [Type.UNKNOWN, s]


async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type

    try:
        message = parse_msg(update.message.text, chat_type)
        if not message:
            return
        img = generator.generate(message)
        photo = BytesIO()
        img.save(photo, format="png")
        photo.seek(0)
        await update.effective_chat.send_photo(photo)
    except Exception as e:
        await update.effective_chat.send_message(
            f"<b>Бип-бип:</b> {e}", parse_mode=ParseMode.HTML
        )
        print(e)
