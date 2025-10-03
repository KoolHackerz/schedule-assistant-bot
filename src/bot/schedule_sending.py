import datetime
import config
from utils import escape_chars, schedule_text
from loguru import logger
from telebot import types
from time import sleep
import json
import quotes
import telebot
from telegram_bot import TelegramBot
import sys
from pathlib import Path


src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from database import db

configuration = config.Config.get_instance()

bot = TelegramBot.get_instance().bot

def send_schedule() -> None:
    '''Функция для авторассылки сообщений'''

    today = datetime.date.today()

    subscribers = db.get_subscribers()

    for subscriber in subscribers:
        chat_id = subscriber[0]
        language = subscriber[1]
        group = subscriber[2]
        quotes_subscribed = subscriber[3]
        
        try:
            message_text = schedule_text(
                today, language, group, chat_id)

            if quotes_subscribed:
                quote = quotes.get_random_quote(db.get_user_quote_tag(chat_id), language[:-1])
                if quote:
                    message_text += f"\n>{quote}**"
                else:
                    logger.warning(
                        f"Failed to get a quote with tag {db.get_user_quote_tag(chat_id)}" + \
                        f" for user with user_id - {chat_id}. Changed to default tag.")
                    db.change_user_quote_tag_to_default(chat_id)
                    message_text += f"\n>{quotes.get_random_quote('Success', language[:-1])}**"

            message_text = escape_chars(message_text)

            bot.send_message(chat_id=chat_id, text=message_text, parse_mode="MarkdownV2",
                             link_preview_options=types.LinkPreviewOptions(is_disabled=True))
            logger.info(
                f'Sent schedule to user_id - {chat_id} via autosending')
        except telebot.apihelper.ApiException as e:
            logger.warning(
                f'Failed to send a schedule to user with user_id - {chat_id}: {e}')
            sleep(1)

    if configuration.saturday_lessons:
        if today.strftime("%A").lower() == 'tuesday':
            schedule_files = ['../data/schedules/rus_schedule.json', '../data/schedules/ukr_schedule.json']
            for schedule_file in schedule_files:
                with open(schedule_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                data['saturday'][0]['schedule-day'] += 1

                with open(schedule_file, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)