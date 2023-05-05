from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)

import config
import response


def main():
    application = ApplicationBuilder().token(config.TOKEN).build()

    application.add_handler(CommandHandler("start", response.start))
    application.add_handler(CommandHandler("help", response.help))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), response.msg))

    application.add_error_handler(response.error_handler)

    application.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        url_path="",
        webhook_url=f"https://{config.APP}.{config.SITE}/",
    )


if __name__ == "__main__":
    main()
