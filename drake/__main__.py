from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from drake import config, response
from drake.logging import setup_logging


def main():
    setup_logging()

    application = ApplicationBuilder().token(config.TOKEN).build()

    application.add_handler(CommandHandler("start", response.start))
    application.add_handler(CommandHandler("help", response.help))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), response.msg))

    application.add_error_handler(response.error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
