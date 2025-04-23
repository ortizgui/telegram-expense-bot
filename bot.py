from telegram.ext import Updater, CommandHandler
import commands, db
import os

def main():
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    if not TOKEN:
        print("Defina a variável de ambiente TELEGRAM_TOKEN")
        return

    # init DB
    db.init_db()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Conversa de adicionar despesa
    dp.add_handler(commands.get_handlers())

    # /report
    dp.add_handler(CommandHandler('report', commands.report))

    updater.start_polling()
    print("Bot rodando...")
    updater.idle()

if __name__ == '__main__':
    main()