from loguru import logger
from telebot import types
import config
import json
import datetime
import sys
from pathlib import Path
from telegram_bot import TelegramBot

src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from database import db


configuration = config.Config.get_instance()

def escape_chars(text: str) -> str:
    '''Функция для экранирования символов в text'''
    chars_to_escape = ['|', '_', '-', '=', '.', '!']

    for char in chars_to_escape:
        text = text.replace(char, f"\{char}")

    return text

def get_platform(link: str) -> str:
    '''Функция для получения платформы по ссылке link'''
    if 'zoom' in link:
        return 'Zoom'
    elif 'meet.google' in link:
        return 'Google Meet'
    elif 'teams.microsoft' in link:
        return 'Microsoft Teams'
    else:
        return 'Unknown'

def quote_tags_by_letters() -> str:
    '''Функция для получения тегов цитат по буквам'''
    return """A: Age, Athletics
B: Business 
C: Change, Character, Competition, Conservative, Courage, Creativity 
E: Education, Ethics 
F: Failure, Faith, Family, Famous Quotes, Film, Freedom, Friendship, Future
G: Generosity, Genius, Gratitude
H: Happiness, Health, History, Honor, Humor, Humorous
I: Imagination, Inspirational
K: Knowledge
L: Leadership, Life, Literature, Love
M: Mathematics, Motivational
N: Nature
O: Opportunity
P: Pain, Perseverance, Philosophy, Politics, Power Quotes, Proverb
R: Religion
S: Sadness, Science, Self, Self Help, Social Justice, Society, Spirituality, Sports, Stupidity, Success
T: Technology, Time, Tolerance, Truth
V: Virtue
W: War, Weakness, Wellness, Wisdom, Work"""

def load_voice_file(voice_file_path: str) -> bytes:
    """Функция для загрузки голосового файла в память"""
    try:
        with open(voice_file_path, 'rb') as file:
            return file.read()  # Чтение содержимого файла в байты
    except FileNotFoundError as e:
        logger.error(f"Голосовой файл не найден: {e}")
        return None

def update_buttons(language: str, user_id: int, is_admin: bool = False, mode: str = 'main') -> types.ReplyKeyboardMarkup:
    '''Функция для обновления кнопок в соответствии с языком пользователя и выбранным режимом.'''
    # Главное меню
    if mode == 'main':
        button = types.KeyboardButton(configuration.BUTTON_TEXTS[language]["schedule"])
        button_tomorrow = types.KeyboardButton(
            configuration.BUTTON_TEXTS[language]["schedule_tomorrow"])
        button_subscribe_unsubscribe = db.get_subcribe_unsubscibe_button(
            language, user_id)
        button_view_assignments = types.KeyboardButton(
            configuration.BUTTON_TEXTS[language]["view_assignments"])
        button_find_sticker = types.KeyboardButton(
            configuration.BUTTON_TEXTS[language]["find_sticker"])
        button_settings = types.KeyboardButton(
            configuration.BUTTON_TEXTS[language]["settings"])

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row(button, button_tomorrow)
        keyboard.row(button_subscribe_unsubscribe, button_view_assignments)
        keyboard.row(button_find_sticker, button_settings)

        if is_admin:
            button_send_all = types.KeyboardButton(
                configuration.BUTTON_TEXTS[language]["send_all"])
            button_add_assignment = types.KeyboardButton(
                configuration.BUTTON_TEXTS[language]["add_assignment"])
            keyboard.row(button_send_all, button_add_assignment)

    # Меню настроек
    elif mode == 'settings':
        button_change_language = types.KeyboardButton(
            configuration.BUTTON_TEXTS[language]["change_language"])
        button_change_group = types.KeyboardButton(
            configuration.BUTTON_TEXTS[language]["change_group"])
        button_configure_quote = types.KeyboardButton(
            configuration.BUTTON_TEXTS[language]["configure_quote"])
        button_return = types.KeyboardButton(configuration.BUTTON_TEXTS[language]["return"])

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row(button_change_language, button_change_group)
        keyboard.row(button_configure_quote)
        keyboard.row(button_return)

    # Меню цитат
    elif mode == 'quotes':
        subscribe_quote_button = db.get_subcribe_unsubscibe_quote_button(
            language, user_id)
        change_quote_theme_button = types.KeyboardButton(
            configuration.BUTTON_TEXTS[language]["change_quote_theme"])
        return_to_settings_button = types.KeyboardButton(
            configuration.BUTTON_TEXTS[language]["return_to_settings"])

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row(subscribe_quote_button, change_quote_theme_button)
        keyboard.row(return_to_settings_button)

    return keyboard

def get_content_description(message: types.Message) -> str:
    '''Функция для получения описания контента сообщения'''
    match message.content_type:
        case 'text':
            return f'text "{message.text}"'
        case 'photo':
            return 'a photo'
        case 'sticker':
            return 'a sticker'
        case 'animation':
            return 'an animation'
        case 'voice':
            return 'a voice'
        case _:
            return 'an unknown content'

def load_assignments():
    '''Функция для загрузки заданий из файла'''
    try:
        with open('../data/assignments.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Ошибка загрузки заданий: {e}")
        return {'assignments': []}

def save_assignments(assignments):
    '''Функция для сохранения заданий в файл'''
    with open('../data/assignments.json', 'w', encoding='utf-8') as file:
        json.dump(assignments, file, ensure_ascii=False, indent=4)

def remove_expired_assignments():
    '''Функция для удаления просроченных заданий'''
    today = datetime.date.today()
    assignments = load_assignments()
    updated_assignments = [a for a in assignments['assignments'] if datetime.datetime.strptime(
        a['deadline'], '%Y-%m-%d').date() >= today]

    if len(updated_assignments) < len(assignments['assignments']):
        assignments['assignments'] = updated_assignments
        save_assignments(assignments)


def schedule_text(today: datetime.date, language: str, group: int, chat_id: int) -> str:
    '''Функция для составления сообщения с расписанием'''
    VOICE_FILE_CONTENT = load_voice_file('../data/audio/voice.m4a')

    day_name_en = today.strftime('%A').lower()
    day_name_local = config.localized_weekday_names[language].get(
        day_name_en, day_name_en)

    schedule_file = f'../data/schedules/{language}_schedule.json'

    with open(schedule_file, 'r', encoding='utf-8') as file:
        schedule = json.load(file).get(day_name_en)

    if not schedule:
        if VOICE_FILE_CONTENT:
            bot = TelegramBot.get_instance().bot
            bot.send_voice(chat_id, VOICE_FILE_CONTENT, caption=configuration.BUTTON_TEXTS[language]["no_schedule"])
            logger.info(f'Sent voice message to {chat_id}')
        return ''

    message_text = configuration.BUTTON_TEXTS[language]["schedule_for_day"].format(
        day_name=day_name_local)

    if day_name_en != 'saturday':
        # Проверка на чётность/нечётность. False - нечётная, True - чётная
        current_week_number = today.isocalendar()[1]
        week_parity = (current_week_number -
                       configuration.FIRST_WEEK_NUMBER) % 2 != 0
    else:
        schedule_day = schedule[0].get('schedule-day', 0)

        day = schedule_day % 5 + 1
        week_parity = ((schedule_day // 5) + 1) % 2 == 0

        with open(schedule_file, 'r', encoding='utf-8') as file:
            schedule = json.load(file).get(config.day_names[day])

    for item in schedule:
        if (item.get("week_parity") is None or item.get("week_parity") is week_parity) and (item.get("group") is None or item.get("group") is group):
            message_text += f'{item["time"]}\n{item["name"]}:\n'
            for link in item["links"]:
                if 'Пароль' in link:
                    message_text += f'{link}\n'
                else:
                    link_shortcut = configuration.BUTTON_TEXTS[language]["link_to"] + \
                        get_platform(link)
                    message_text += f'[{link_shortcut}]({link})\n'
            message_text += f'{item["teachers"]}\n\n'

    return message_text