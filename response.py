from telegram import Update
from telegram.constants import ParseMode

import config
import error
from generator import Item, MemeGenerator, Type

generator = MemeGenerator()


async def start(update: Update, context):
    await update.effective_chat.send_message(config.hello_msg + config.help_msg, parse_mode=ParseMode.HTML)


async def help(update: Update, context):
    await update.effective_chat.send_message(config.help_msg, parse_mode=ParseMode.HTML)


def parse_msg(message, chat_type):
    lines = []
    match chat_type:
        case "private":
            lines = [parse_line(l) for l in message.split("\n")]
        case "supergroup" | "group" | "channel":
            hash_tag = "#drake"
            if message.startswith(hash_tag):
                lines = [parse_line(l) for l in message[len(hash_tag) :].strip().split("\n")]
            else:
                return []
    l = len(lines)
    if l < 2:
        raise error.ParseError("Напиши мне не меньше двух строк")
    if l == 2:
        fst, snd = lines
        if fst.msg_type == Type.UNKNOWN:
            fst.msg_type = Type.NO
        if snd.msg_type == Type.UNKNOWN:
            snd.msg_type = Type.YES
    else:
        for l in lines:
            if l.msg_type == Type.UNKNOWN:
                raise error.ParseError(f'Не могу определится с эмоциями для "{l.message}"')
    return lines


def is_link(text):
    return text.startswith("http")


def parse_line(s):
    yes = ["yes", "да", "+"]
    no = ["no", "нет", "-"]

    head, *tail = s.split(maxsplit=1)
    rest = tail[0] if tail else ""
    head = head.lower()
    if head in yes:
        return Item(Type.YES, is_link(rest), rest)
    if head in no:
        return Item(Type.NO, is_link(rest), rest)
    return Item(Type.UNKNOWN, is_link(s), s)


async def msg(update: Update, context):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type

    try:
        # TODO: пофиксить данный костыль
        text = update.message.text if update.message else update.channel_post.text
        messages = parse_msg(text, chat_type)
        if not messages:
            return
        if len(messages) > config.max_messages_count:
            raise error.TooManyMessages(
                f"Максимально количество реплик должно быть не больше {config.max_messages_count}"
            )
        await update.effective_chat.send_photo(generator.create(messages))
    except Exception as e:
        await update.effective_chat.send_message(f"<b>Бип-буп:</b> {e}", parse_mode=ParseMode.HTML)
        print(e)
