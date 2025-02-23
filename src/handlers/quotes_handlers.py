from loguru import logger
from telebot import types
from bot.config import Config
from bot.utils import update_buttons
import sys
from pathlib import Path

src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from database import db

BUTTON_TEXTS = Config.get_instance().BUTTON_TEXTS

def register_quotes_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]["configure_quote"])
    def handle_configure_quote(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)
        prompt_text = BUTTON_TEXTS[user_language]["configure_quote_prompt"]
        bot.send_message(message.chat.id, prompt_text, reply_markup=update_buttons(
            user_language, message.chat.id, mode='quotes'))
    
    @bot.message_handler(func=lambda message: message.text in [BUTTON_TEXTS[db.get_user_language(message.chat.id)]['subscribe_quotes'], BUTTON_TEXTS[db.get_user_language(message.chat.id)]['unsubscribe_quotes']])
    def handle_quotes_subscription(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)
        user_id = message.chat.id

        is_subscribed = db.get_user_quotes_subscription(user_id)

        logger.info(
            f'User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) tried to subscribe/unsubscribe to/from quotes')
        if is_subscribed is None or not is_subscribed[0]:
            update_query = """UPDATE subscriptions SET quotes_subscribed = 1 WHERE user_id == ?"""
            success_message = BUTTON_TEXTS[user_language]["subscribe_quotes_success"]
            logger.info(
                f"User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) has successfully subscribed to quotes")
        else:
            update_query = """UPDATE subscriptions SET quotes_subscribed = 0 WHERE user_id == ?"""
            success_message = BUTTON_TEXTS[user_language]["unsubscribe_quotes_success"]
            logger.info(
                f"User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) has successfully unsubscribed from quotes")

        db.update_with_query_and_user_id(update_query, user_id)

        bot.send_message(user_id, success_message, reply_markup=update_buttons(
            user_language, user_id, mode='quotes'))
