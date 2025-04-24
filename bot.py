#!/usr/bin/env python3
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
import commands


def main():
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logging.error("Environment variable TELEGRAM_TOKEN not defined.")
        return

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    app = ApplicationBuilder().token(token).build()

    # Add the conversation handler - it returns just one handler, not multiple
    app.add_handler(commands.get_handlers())

    # Add report command handler
    app.add_handler(commands.get_report_handler())

    # Add cancel command handler
    app.add_handler(CommandHandler('cancel', commands.cancel))

    app.add_handler(CommandHandler('undo', commands.undo))

    logging.info("Bot started. Running polling...")
    app.run_polling()


if __name__ == '__main__':
    main()