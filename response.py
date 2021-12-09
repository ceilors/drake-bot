from io import BytesIO

from telegram.ext import CallbackContext
from telegram import Update, ParseMode

from generator import MemeGenerator, LongTextException


generator = MemeGenerator()
greetings =\
    '<b>Привет!</b>\n\n'\
    'Я бот генерирующий <i>drake meme</i> по твоим фразам.\n\n'\
    '<i>Сначала</i> отправить сообщение с фразами <b>для шаблона "нет"</b>.\n'\
    '<i>Следующим</i> сообщением <b>на шаблон "да"</b>.\n'\
    'Немного подожди и я пришлю тебе готовую картинку!\n\n'\
    '<i>И не забывай что переносы строк разделяют фразы на пару картинок!</i>'


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=greetings, parse_mode=ParseMode.HTML)


def generate_response(context, chat_id, text_yes, text_no):
    try:
        img = generator.generate(for_yes=text_yes, for_no=text_no)
        photo = BytesIO()
        img.save(photo, format='png')
        photo.seek(0)
        context.bot.send_photo(chat_id, photo=photo)
    except LongTextException:
        context.bot.send_message(chat_id=chat_id,
            text='<b>Бип-бип:</b> Текст слишком длинный!', parse_mode=ParseMode.HTML)
    except Exception as e:
        context.bot.send_message(chat_id=chat_id,
            text='<b>Бип-буп:</b> Что-то пошло не так!', parse_mode=ParseMode.HTML)
        print(e)


def parse_msg(message, chat_type):
    if chat_type == 'private':
        return message.split('\n')
    elif chat_type == 'supergroup':
        if message.startswith('#drake'):
            return message[6:].strip().split('\n')
    return None


def msg(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type

    if chat_type == 'supergroup' and not update.message.text.startswith('#drake'):
        return

    if 'msg' in context.chat_data:
        text_no = context.chat_data['msg']
        text_yes = parse_msg(update.message.text, chat_type)
        if text_yes and text_no:
            generate_response(context, chat_id, text_yes, text_no)
        del context.chat_data['msg']
    else:
        context.chat_data['msg'] = parse_msg(update.message.text, chat_type)
