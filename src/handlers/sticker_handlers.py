from time import sleep
from loguru import logger
from telebot import types
from bot.config import Config
import sys
from pathlib import Path


src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from database import db

BUTTON_TEXTS = Config.get_instance().BUTTON_TEXTS

def register_sticker_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]['find_sticker'])
    def get_text_to_find_stickers(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)

        msg = bot.reply_to(
            message, BUTTON_TEXTS[user_language]["enter_sticker_search"])
        logger.info(
            f'User {message.from_user.username}(user_id - {message.from_user.id}) tried to find sticker')

        bot.register_next_step_handler(msg, find_stickers)

    def find_stickers(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)

        stickers = db.get_stickers()

        result = []
        for sticker in stickers:
            try:
                if message.text.lower() in sticker[1].lower():
                    result.append(sticker[0])
            except AttributeError as e:
                logger.warning(
                    f'User {message.from_user.username}(user_id - {message.from_user.id}) sent something that caused AttributeError: {e}')
                bot.send_sticker(
                    message.chat.id, 'CAACAgIAAxUAAWT0z6Md0UVZkLHqaVvFesY_3q66AAJoIAAC4SO4SjsRfJMSVWi6MAQ')
                return

        if result:
            for sticker in result:
                sleep(0.5)
                bot.send_sticker(message.chat.id, sticker)
            logger.info(
                f'Sent {len(result)} stickers to user {message.from_user.username}(user_id - {message.from_user.id}). Searching text was {message.text}')
        else:
            bot.reply_to(message, BUTTON_TEXTS[user_language]["no_stickers_found"])
            logger.info(
                f'User {message.from_user.username}(user_id - {message.from_user.id}) did not find any sticker. Searching text was {message.text}')
