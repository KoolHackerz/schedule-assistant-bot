from threading import Thread
from time import sleep
import schedule as sc
import sys
from pathlib import Path

from config import Config
from telegram_bot import TelegramBot
from schedule_sending import send_schedule


src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from handlers import main_handlers

def schedule_checker() -> None:
    while True:
        sc.run_pending()
        sleep(1)

if __name__ == '__main__':
    telegram_bot = TelegramBot.get_instance()
    main_handlers.register_handlers(telegram_bot.bot)

    sc.every().monday.at('07:00').do(send_schedule)
    sc.every().tuesday.at('07:00').do(send_schedule)
    sc.every().wednesday.at('07:00').do(send_schedule)
    sc.every().thursday.at('07:00').do(send_schedule)
    # sc.every().friday.at('07:00').do(send_schedule)
    
    if Config.get_instance().saturday_lessons:
        sc.every().saturday.at('07:00').do(send_schedule)
    
    # sc.every().second.do(send_schedule) # for testing purposes

    thread = Thread(target=schedule_checker, daemon=True)
    thread.start()

    telegram_bot.start()

    while thread.is_alive:
        thread.join(1)
    
    telegram_bot.bot.remove_webhook()