from time import sleep
from loguru import logger
from telebot import types, apihelper
from bot.config import Config
from bot.utils import get_content_description

import sys
from pathlib import Path

src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from database import db

BUTTON_TEXTS = Config.get_instance().BUTTON_TEXTS

def register_admin_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]['send_all'], content_types=['text', 'photo', 'sticker', 'animation', 'voice'])
    def get_text_to_send_all(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)
        user_is_admin = db.get_user_admin_status(message.chat.id)

        logger.info(
            f'User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) tried to send all')
        if not user_is_admin:
            bot.reply_to(message, BUTTON_TEXTS[user_language]["no_rights_error"])
            logger.info(
                f'User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) has no rights to send all')
            return

        msg = bot.reply_to(message, BUTTON_TEXTS[user_language]["send_all_prompt"])

        bot.register_next_step_handler(msg, send_all)

    def send_all(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)
        users_ids = db.get_user_subscriptions()

        successful_sends = 0
        total_users = 0
        content_description = ''

        for user_id in users_ids:
            if user_id[0] == message.chat.id:
                continue
            try:
                if message.content_type == 'text':
                    bot.send_message(user_id[0], message.text)
                elif message.content_type == 'photo':
                    photo_id = message.photo[-1].file_id
                    bot.send_photo(user_id[0], photo_id)
                elif message.content_type == 'sticker':
                    sticker_id = message.sticker.file_id
                    bot.send_sticker(user_id[0], sticker_id)
                elif message.content_type == 'animation':
                    animation_id = message.animation.file_id
                    bot.send_animation(user_id[0], animation_id)
                elif message.content_type == 'voice':
                    voice_id = message.voice.file_id
                    bot.send_voice(user_id[0], voice_id)
                content_description = get_content_description(message)
                logger.info(
                    f'User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) sent {content_description} to {user_id[0]} via send all command')
                successful_sends += 1
            except apihelper.ApiException as e:
                if e.error_code == 403 and 'bot was blocked by the user' in e.result.text:
                    db.delete_user(user_id[0])
                    logger.info(
                        f'User with user_id - {user_id[0]} has been removed from the database due to blocking the bot.')
                else:
                    logger.warning(
                        f'Failed to send a message to user with user_id - {user_id[0]}: {e}')
            total_users += 1
            sleep(1)

        bot_reply_content = content_description if message.content_type != 'text' else f'Сообщение:\n{message.text}'
        success_message = BUTTON_TEXTS[user_language]["send_all_success"].format(
            successful_sends=successful_sends,
            total_users=total_users,
            bot_reply_content=bot_reply_content
        )
        bot.reply_to(message, success_message)
