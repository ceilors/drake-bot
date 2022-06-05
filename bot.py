from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)

import response
import config


if __name__ == "__main__":
    application = ApplicationBuilder().token(config.TOKEN).build()

    start_handler = CommandHandler("start", response.start)
    application.add_handler(start_handler)

    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), response.msg)
    application.add_handler(msg_handler)

    if config.USE_HEROKU:
        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            url_path="",
            webhook_url=f"https://{config.APP}.herokuapp.com/",
        )
    else:
        application.run_polling()
