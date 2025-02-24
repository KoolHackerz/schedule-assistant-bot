from telebot import types
from loguru import logger
from bot.config import Config, quote_tags
from bot.utils import quote_tags_by_letters, update_buttons
import sys
from pathlib import Path


src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from database import db


BUTTON_TEXTS = Config.get_instance().BUTTON_TEXTS

def register_settings_handlers(bot):
    @bot.message_handler(func=lambda message: message.text in [BUTTON_TEXTS[db.get_user_language(message.chat.id)]['subscribe'], BUTTON_TEXTS[db.get_user_language(message.chat.id)]['unsubscribe']])
    def subscribe_unsubscribe_handler(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)
        user_id = message.chat.id

        is_subscribed = db.get_user_subscribed(user_id)
        is_admin = db.get_user_admin_status(user_id)

        logger.info(
            f'User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) tried to subscribe/unsubscribe')
        if is_subscribed is None or not is_subscribed[0]:
            if is_subscribed is None:
                update_query = """INSERT INTO subscriptions (user_id, subscribed) VALUES (?, 1)"""
            else:
                update_query = """UPDATE subscriptions SET subscribed = 1 WHERE user_id == ?"""
            success_message = BUTTON_TEXTS[user_language]["subscribe_success"]
            logger.info(
                f"User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) has successfully subscribed")
        else:
            update_query = """UPDATE subscriptions SET subscribed = 0 WHERE user_id == ?"""
            success_message = BUTTON_TEXTS[user_language]["unsubscribe_success"]
            logger.info(
                f"User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) has successfully unsubscribed")

        db.update_with_query_and_user_id(update_query, user_id)

        bot.send_message(user_id, success_message, reply_markup=update_buttons(
            user_language, user_id, is_admin, mode='main'))

    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]['change_quote_theme'])
    def get_quote_tag_from_user(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)

        msg = bot.reply_to(message, BUTTON_TEXTS[user_language]
                        ["enter_quote_theme_prompt"] + quote_tags_by_letters())
        logger.info(
            f'User {message.from_user.username}(user_id - {message.from_user.id}) tried to change quote tag')

        bot.register_next_step_handler(msg, proccess_tag)

    def proccess_tag(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)
        tag = message.text

        if tag not in quote_tags:
            bot.reply_to(message, BUTTON_TEXTS[user_language]["no_quote_theme"])
            logger.info(
                f'User {message.from_user.username}(user_id - {message.from_user.id}) entered wrong tag - {tag}')
            return

        db.update_selected_quotes_tag(tag, message.chat.id)

        bot.reply_to(message, BUTTON_TEXTS[user_language]["quote_theme_changed"])
        logger.info(
            f'User {message.from_user.username}(user_id - {message.from_user.id}) changed quote tag to {tag}')

    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]['change_language'])
    def change_language(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)

        keyboard = types.InlineKeyboardMarkup()

        rus_lang = types.InlineKeyboardButton(text='Русский', callback_data='rus')
        ukr_lang = types.InlineKeyboardButton(
            text='Українська', callback_data='ukr')

        keyboard.add(rus_lang, ukr_lang)

        bot.send_message(
            message.chat.id, BUTTON_TEXTS[user_language]["language_change_prompt"], reply_markup=keyboard)
        logger.info(
            f'User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) tried to change language')

    @bot.callback_query_handler(func=lambda call: call.data == 'rus' or call.data == 'ukr')
    def answer_change_language(call: types.CallbackQuery) -> None:
        user_language = db.get_user_language(call.message.chat.id)
        full_language_name = 'russian' if call.data == 'rus' else 'ukranian'

        if user_language == call.data:
            bot.answer_callback_query(
                call.id, BUTTON_TEXTS[user_language]["language_already_selected"])
            logger.info(
                f'User {call.message.chat.username} ({call.from_user.first_name})(user_id - {call.message.chat.id}) already has {full_language_name} language')
            return

        db.update_user_language(call.data, call.message.chat.id)
        is_admin = db.get_user_admin_status(call.message.chat.id)

        bot.answer_callback_query(
            call.id, BUTTON_TEXTS[call.data]["language_changed"])

        keyboard = update_buttons(call.data, is_admin, 'settings')

        logger.info(
            f'User {call.message.chat.username} ({call.from_user.first_name})(user_id - {call.message.chat.id}) changed language to {full_language_name}')

        bot.send_message(chat_id=call.message.chat.id,
                        text=BUTTON_TEXTS[call.data]["language_selected"], reply_markup=keyboard)
        bot.edit_message_reply_markup(
            call.message.chat.id, message_id=call.message.message_id, reply_markup='')


    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]['change_group'])
    def change_group(message: types.Message) -> None:
        user_language = db.get_user_language(message.chat.id)

        keyboard = types.InlineKeyboardMarkup()

        first_group = types.InlineKeyboardButton(text='ВД01-14', callback_data='1')
        second_group = types.InlineKeyboardButton(
            text='ВД01-15', callback_data='2')

        keyboard.add(first_group, second_group)

        bot.send_message(
            message.chat.id, BUTTON_TEXTS[user_language]["group_change_prompt"], reply_markup=keyboard)
        logger.info(
            f'User {message.from_user.username} ({message.from_user.first_name})(user_id - {message.from_user.id}) tried to change group')


    @bot.callback_query_handler(func=lambda call: call.data == '1' or call.data == '2')
    def answer_change_group(call: types.CallbackQuery) -> None:
        new_user_group_number = int(call.data)
        new_user_group = 'ВД01-14' if new_user_group_number == 1 else 'ВД01-15'

        user_language = db.get_user_language(call.message.chat.id)
        user_group = db.get_user_group(call.message.chat.id)

        if new_user_group_number == user_group:
            bot.answer_callback_query(
                call.id, BUTTON_TEXTS[user_language]["group_already_selected"])
            logger.info(
                f'User {call.message.chat.username} ({call.from_user.first_name})(user_id - {call.message.chat.id}) had been already in {new_user_group} group')
            return

        db.update_user_group(new_user_group_number, call.message.chat.id)

        bot.answer_callback_query(
            call.id, BUTTON_TEXTS[user_language]["group_changed"])
        logger.info(
            f'User {call.message.chat.username} ({call.from_user.first_name})(user_id - {call.message.chat.id}) changed group to {new_user_group}')
        bot.send_message(chat_id=call.message.chat.id,
                        text=BUTTON_TEXTS[user_language]["current_group"].format(group_name=new_user_group))

        bot.edit_message_reply_markup(
            call.message.chat.id, message_id=call.message.message_id, reply_markup='')
