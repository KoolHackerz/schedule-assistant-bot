import datetime
from bot.utils import escape_chars, schedule_text
from bot.config import Config
from telebot import types
from loguru import logger
import sys
from pathlib import Path


src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from database import db

configuration = Config.get_instance()
BUTTON_TEXTS = configuration.BUTTON_TEXTS

def register_schedule_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]['schedule'])
    def schedule(message: types.Message) -> None:
        today = datetime.date.today()
        user_language = db.get_user_language(message.chat.id)
        user_group = db.get_user_group(message.chat.id)

        message_text = schedule_text(
            today, user_language, user_group, message.chat.id)

        if message_text:
            message_text = escape_chars(message_text)
            bot.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2",
                            link_preview_options=types.LinkPreviewOptions(is_disabled=True))

        logger.info(
            f'Sent schedule to {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) via command "{message.text}"')

    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]['schedule_tomorrow'])
    def schedule_tomorrow(message: types.Message) -> None:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        user_language = db.get_user_language(message.chat.id)
        user_group = db.get_user_group(message.chat.id)
        message_text = schedule_text(
            tomorrow, user_language, user_group, message.chat.id)

        message_text = escape_chars(message_text)

        bot.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2",
                        link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        logger.info(
            f'Sent schedule to {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) via command "{message.text}"')
