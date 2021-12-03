from io import BytesIO

from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Update, ParseMode

from generator import MemeGenerator, LongTextException
from config import TOKEN


generator = MemeGenerator()
greetings =\
    '<b>Привет!</b>\n\n'\
    'Я бот генерирующий <i>drake meme</i> по твоим фразам.\n\n'\
    '<i>Сначала</i> отправить сообщение с фразами <b>для шаблона "нет"</b>.\n'\
    '<i>Следующим</i> сообщением <b>на шаблон "да"</b>.\n'\
    'Немного подожди и я пришлю тебе готовую картинку!\n\n'\
    '<i>И не забывай что переносы строк разделяют фразы на пару картинок!</i>'
user_data = {}


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=greetings, parse_mode=ParseMode.HTML)


def msg(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id in user_data:
        text_no = user_data[chat_id].split('\n')
        text_yes = update.message.text.split('\n')
        try:
            img = generator.generate(for_yes=text_yes, for_no=text_no)
            photo = BytesIO()
            img.save(photo, format='png')
            photo.seek(0)
            context.bot.send_photo(chat_id, photo=photo)
        except LongTextException:
            context.bot.send_message(chat_id=chat_id, text='Текст слишком длинный!')
        except Exception:
            context.bot.send_message(chat_id=chat_id, text='Что-то пошло не так!')
        del user_data[chat_id]
    else:
        user_data[chat_id] = update.message.text


if __name__ == '__main__':
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    msg_handler = MessageHandler(Filters.text & (~Filters.command), msg)
    dispatcher.add_handler(msg_handler)

    updater.start_polling()
    updater.idle()
