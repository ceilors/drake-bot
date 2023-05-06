import logging

from telegram import Update
from telegram.constants import MessageEntityType, ParseMode

from drake import config, error
from drake.generator import Item, MemeGenerator, Type

generator = MemeGenerator()


async def start(update: Update, context):
    await update.effective_chat.send_message(config.hello_msg + config.help_msg, parse_mode=ParseMode.HTML)


async def help(update: Update, context):
    await update.effective_chat.send_message(config.help_msg, parse_mode=ParseMode.HTML)


async def error_handler(update, context) -> None:
    logging.error("Exception while handling an update: %s", context.error)


def parse_msg(message, entities, chat_type):
    lines = []
    if chat_type == "private":
        lines = [parse_line(line) for line in message.split("\n")]
    elif chat_type in ["supergroup", "group", "channel"]:
        if len(entities) == 0:
            return []
        entity = entities[0]
        msg_hash_tag = message[entity.offset : entity.length]
        if entity.type == MessageEntityType.HASHTAG and msg_hash_tag == "#drake":
            message = message[entity.length :]
            if len(message) == 0:
                raise error.ParseError("Где текст Билли?")
            lines = [parse_line(line) for line in message.strip().split("\n")]
        else:
            return []
    line_count = len(lines)
    if line_count < 2:
        raise error.ParseError("Напиши мне не меньше двух строк")
    if line_count == 2:
        fst, snd = lines
        if fst.msg_type == Type.UNKNOWN:
            fst.msg_type = Type.NO
        if snd.msg_type == Type.UNKNOWN:
            snd.msg_type = Type.YES
    else:
        for line in lines:
            if line.msg_type == Type.UNKNOWN:
                raise error.ParseError(f'Не могу определится с эмоциями для "{line.message}"')
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
    chat_type = update.effective_chat.type

    try:
        if update.message is None and update.channel_post is None:
            logging.warning("Something went wrong! update: %s", update)
            return
        obj = update.message if update.message else update.channel_post
        messages = parse_msg(obj.text, obj.entities, chat_type)
        if not messages:
            return
        if len(messages) > config.max_messages_count:
            raise error.TooManyMessages(
                f"Максимально количество реплик должно быть не больше {config.max_messages_count}"
            )
        await update.effective_chat.send_photo(generator.create(messages))
    except Exception as e:
        await update.effective_chat.send_message(f"<b>Бип-буп:</b> {e}", parse_mode=ParseMode.HTML)
        logging.exception("exception occured")
