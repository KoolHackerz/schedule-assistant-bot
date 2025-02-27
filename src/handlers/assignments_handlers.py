import datetime
import re
from bot.utils import escape_chars, remove_expired_assignments, load_assignments, save_assignments
from bot.config import Config
from telebot import types
import sys
from pathlib import Path


src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from database import db

configuration = Config.get_instance()
BUTTON_TEXTS = configuration.BUTTON_TEXTS
ADMINS = configuration.ADMINS

def register_assignments_handlers(bot):
    @bot.message_handler(commands=['add_assignment'])
    def add_assignment(message):
        language = db.get_user_language(message.chat.id)
        if message.chat.id in ADMINS:
            msg = bot.send_message(
                message.chat.id, BUTTON_TEXTS[language]["assignment_subject_prompt"])
            bot.register_next_step_handler(msg, process_subject, language)
        else:
            bot.send_message(
                message.chat.id, BUTTON_TEXTS[language]["no_rights_error"])

    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]["add_assignment"])
    def handle_add_assignment(message: types.Message):
        if message.chat.id in ADMINS:
            add_assignment(message)
        else:
            bot.send_message(
            message.chat.id, BUTTON_TEXTS[db.get_user_language(message.chat.id)]["no_rights_error"])

    @bot.message_handler(commands=['view_assignments'])
    def view_assignments(message):
        language = db.get_user_language(message.chat.id)
        remove_expired_assignments()
        assignments = load_assignments()
        if not assignments['assignments']:
            bot.send_message(
                message.chat.id, BUTTON_TEXTS[language]["no_assignments"])
        else:
            response = f"📋 *{BUTTON_TEXTS[language]['assignments_list_header']}*\n\n"
            for assignment in assignments['assignments']:
                response += f"🔹 {BUTTON_TEXTS[language]['assignment_subject']}: *{assignment['subject']}*\n"
                response += f"✏️ {BUTTON_TEXTS[language]['task']}: {assignment['task']}\n"
                response += f"📅 {BUTTON_TEXTS[language]['deadline']}: {assignment['deadline']}\n\n"
            response = escape_chars(response)
            bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")

    @bot.message_handler(func=lambda message: message.text == BUTTON_TEXTS[db.get_user_language(message.chat.id)]["view_assignments"])
    def show_assignments(message: types.Message):
        view_assignments(message)

    def process_subject(message, language):
        subject = message.text
        if not subject:
            msg = bot.send_message(
                message.chat.id, BUTTON_TEXTS[language]["assignment_subject_prompt"])
            bot.register_next_step_handler(msg, process_subject, language)
        elif re.search(r'\d', subject):
            msg = bot.send_message(
                message.chat.id, BUTTON_TEXTS[language]["assignment_subject_number_error"])
            bot.register_next_step_handler(msg, process_subject, language)
        else:
            msg = bot.send_message(
                message.chat.id, BUTTON_TEXTS[language]["assignment_task_prompt"])
            bot.register_next_step_handler(msg, process_task, subject, language)

    def process_task(message, subject, language):
        task = message.text
        if not task:
            msg = bot.send_message(
                message.chat.id, BUTTON_TEXTS[language]["assignment_task_prompt"])
            bot.register_next_step_handler(msg, process_task, subject, language)
        else:
            msg = bot.send_message(
                message.chat.id, BUTTON_TEXTS[language]["assignment_deadline_prompt"])
            bot.register_next_step_handler(
                msg, process_deadline, subject, task, language)

    def process_deadline(message, subject, task, language):
        deadline_str = message.text
        try:
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%d').date()
            today = datetime.date.today()

            if deadline < today:
                raise ValueError("deadline_in_past")

            assignments = load_assignments()
            assignments['assignments'].append(
                {"subject": subject, "task": task, "deadline": deadline_str})
            save_assignments(assignments)
            bot.send_message(
                message.chat.id, BUTTON_TEXTS[language]["assignment_added_successfully"])

        except ValueError as e:
            error_code = str(e)
            if error_code == "deadline_in_past":
                msg = bot.send_message(
                    message.chat.id, BUTTON_TEXTS[language]["deadline_in_past_error"])
            else:
                msg = bot.send_message(
                    message.chat.id, BUTTON_TEXTS[language]["deadline_format_error"])
            bot.register_next_step_handler(
                msg, process_deadline, subject, task, language)
