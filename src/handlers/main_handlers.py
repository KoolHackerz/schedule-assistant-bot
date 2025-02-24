from loguru import logger
from telebot import types
from bot.config import Config
from bot.utils import update_buttons

from .admin_handlers import register_admin_handlers
from .assignments_handlers import register_assignments_handlers
from .quotes_handlers import register_quotes_handlers
from .schedule_handlers import register_schedule_handlers
from .settings_handlers import register_settings_handlers
from .sticker_handlers import register_sticker_handlers

import sys
from pathlib import Path


src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from database import db

configuration = Config.get_instance()
BUTTON_TEXTS = configuration.BUTTON_TEXTS

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start(message: types.Message) -> None:
        logger.info(
            f'New user - {message.from_user.username} ({message.from_user.first_name})')

        username = message.chat.username
        user_id = message.chat.id
        subscribed = 0
        language = 'rus'
        is_admin = 0

        if user_id in configuration.ADMINS:
            is_admin = 1

        db.create_table()

        if db.get_user(user_id):
            db.update_user(username, subscribed, language, is_admin, user_id)
        else:
            db.add_user(username, user_id, subscribed, language, is_admin)

        keyboard = update_buttons(language, user_id, is_admin)

        bot.send_message(chat_id=message.chat.id,
                        text=configuration.BUTTON_TEXTS[language]["welcome_message"], reply_markup=keyboard)
    
    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]['settings'])
    def show_settings(message: types.Message) -> None:
        
        user_language = db.get_user_language(message.chat.id)
        prompt_text = BUTTON_TEXTS[user_language]["choose_action"]
        bot.send_message(message.chat.id, prompt_text, reply_markup=update_buttons(
            user_language, message.chat.id, mode='settings'))

    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]['return'])
    def return_to_main(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)
        is_admin = db.get_user_admin_status(message.chat.id)

        prompt_text = BUTTON_TEXTS[user_language]["what_next"]
        bot.send_message(message.chat.id, prompt_text, reply_markup=update_buttons(
            user_language, message.chat.id, is_admin, mode='main'))

    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]["return_to_settings"])
    def return_to_settings(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)
        prompt_text = BUTTON_TEXTS[user_language]["return_to_settings_prompt"]
        bot.send_message(message.chat.id, prompt_text, reply_markup=update_buttons(
            user_language, message.chat.id, mode='settings'))
    
    register_admin_handlers(bot)
    register_quotes_handlers(bot)
    register_schedule_handlers(bot)
    register_settings_handlers(bot)
    register_assignments_handlers(bot)
    register_sticker_handlers(bot)
