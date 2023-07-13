import telebot
import datetime
from time import sleep
import json
import sqlite3
from threading import Thread
import schedule as sc
import settings
from loguru import logger
from dotenv import load_dotenv
import os

logger.add("logging.log", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}", level="DEBUG", rotation="10 MB", compression="zip")

load_dotenv()

# TOKEN = os.getenv('TOKEN')
TOKEN = "6052649938:AAHRY1Ndy3wB378cidObLPspazWka1AEOW4"

bot = telebot.TeleBot(TOKEN)

def schedule_checker() -> None:
    while True:
        sc.run_pending()
        sleep(1)

def schedule_text(today: datetime.date, language: str) -> str:
    """Функция для составления сообщения с расписанием"""

    day_name_en = today.strftime('%A').lower()
    day_name_ru = settings.weekday_name_ru_dict.get(day_name_en, day_name_en)
    day_name_uk = settings.weekday_name_uk_dict.get(day_name_en, day_name_en)

    schedule_file = f'{language}_schedule.json'
    
    with open(schedule_file, 'r', encoding='utf-8') as f:
        schedule = json.load(f).get(day_name_en)

    # with open('schedule.json', 'r', encoding='utf-8') as f:
    #     schedule = json.load(f).get(day_name_en)

    if language == "rus":
        if not schedule:
            message_text = "Ты бессмертн(-ый/-ая) что ли? Иди проспись"
            return message_text

        message_text = f"Расписание на {day_name_ru}:\n\n"
    else:
        if not schedule:
            message_text = "Ти шо, з глузду з'їха(-в/-ла) чи шо? Іди поспи"
            return message_text

        message_text = f"Розклад на {day_name_uk}:\n\n"

    #Проверка на чётность/нечётность False - нечётная, True - чётная
    current_week_number = today.isocalendar()[1]
    week_parity = False
    if (current_week_number - settings.FIRST_WEEK_NUMBER) % 2 == 0:
        week_parity = False
    else:
        week_parity = True

    for item in schedule:
        if item.get('week_parity') is None or item.get('week_parity') is week_parity:
            message_text += f"{item['time']}{item['name']}:\n"
            for link in item["links"]:
                message_text += f"{link}\n"

        # elif item.get('week_parity') is week_parity:
        #     message_text += f"{item['time']}{item['name']}:\n"
        #     for link in item["links"]:
        #         message_text += f"{link}\n"

    return message_text

# * Я закоментил и сделал просто вызов функии schedule_text с завтрашним днём
# def schedule_tomorrow_text(today: datetime.date) -> str:
#     """Функция для составления сообщения с расписанием на завтра"""

#     tomorrow = today + datetime.timedelta(days=1)
#     return schedule_text(tomorrow, 'ukr')

def send_schedule() -> None:
    """Функция для авторассылки сообщений"""
    today = datetime.date.today()
    
    message_text = schedule_text(today, 'ukr')

    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM subscriptions')
    subscribers = cursor.fetchall()

    for subscriber in subscribers:
        bot.send_message(chat_id=subscriber[0], text=message_text)
        logger.info(f"Sent schedule to user_id - {subscriber[0]} via autosending")

    conn.commit()
    conn.close()

def get_user_language(chat_id) -> str:
    """Функция для получения языка пользователя"""
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()

    cursor.execute("SELECT language FROM subscriptions WHERE user_id = ?", (chat_id, ))
    language: str = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return language


@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f"New user - {message.from_user.username}")

    username = message.from_user.username
    user_id = message.chat.id
    subscribed = 0
    language = "ukr"
    is_admin = 0

    if user_id in [688575921, 700766922]: # admins
        is_admin = 1

    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS subscriptions
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                user_id INTEGER NOT NULL,
                subscribed INTEGER NOT NULL CHECK (subscribed IN (0, 1)),
                language TEXT NOT NULL CHECK (language IN ("rus", "ukr")),
                is_admin INTEGER NOT NULL CHECK (is_admin IN (0, 1)))""")

    cursor.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.execute("""UPDATE subscriptions 
            SET username = ?, subscribed = ?, language = ?, is_admin = ? 
            WHERE user_id = ?""",
            (username, subscribed, language, is_admin, user_id))
    else:
        cursor.execute("INSERT INTO subscriptions (username, user_id, subscribed, language, is_admin) VALUES (?, ?, ?, ?, ?)",
            (username, user_id, subscribed, language, is_admin))
        
    conn.commit()
    conn.close()

    # todo: отдельные кнопки для укр и рус языков
    button = telebot.types.KeyboardButton('Расписание')
    button_tomorrow = telebot.types.KeyboardButton('Расписание на завтра')  # новая кнопка
    button_subscribe = telebot.types.KeyboardButton('Подписаться')
    button_unsubscribe = telebot.types.KeyboardButton('Отписаться')
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(button, button_tomorrow)  # добавление новой кнопки в клавиатуру
    keyboard.row(button_subscribe, button_unsubscribe)

    bot.send_message(chat_id=message.chat.id, text=f'Привет, сливка! Нажми на кнопку, чтобы получить расписание!', reply_markup=keyboard)

# todo: в хендлерах добавить варианты текста на украинском
@bot.message_handler(func=lambda message: message.text == 'Расписание', content_types=['text'])
def schedule(message):
    today: datetime.date = datetime.date.today()
    user_language: str = get_user_language(message.chat.id)
    message_text = schedule_text(today, user_language)

    bot.send_message(chat_id=message.chat.id, text=message_text)
    logger.info(f"Sent schedule to {message.from_user.username}(user_id - {message.from_user.id}) via command /Расписание")

@bot.message_handler(func=lambda message: message.text == 'Расписание на завтра', content_types=['text'])
def schedule_tomorrow(message):
    tomorrow: datetime.date = datetime.date.today() + datetime.timedelta(days=1)
    user_language: str = get_user_language(message.chat.id)
    message_text: str = schedule_text(tomorrow, user_language)

    bot.send_message(chat_id=message.chat.id, text=message_text)
    logger.info(f"Sent schedule to {message.from_user.username}(user_id - {message.from_user.id}) via command /Расписание на завтра")

@bot.message_handler(func=lambda message: message.text == 'Подписаться', content_types=['text'])
def subscribe(message):
    user_language: str = get_user_language(message.chat.id)
    user_id = message.chat.id

    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()

    cursor.execute('SELECT subscribed FROM subscriptions WHERE user_id = ?', (user_id,))
    subscribed = cursor.fetchone()[0]

    logger.info(f"User {message.from_user.id} tried to subscribe")
    if subscribed:
        bot.reply_to(message, "Вы уже подписаны на рассылку!" if user_language == "rus" else "Ви вже підписані на розсилку!")
        logger.info(f"User {message.from_user.username}(user_id - {message.from_user.id}) has been already subscribed")
    else:
        cursor.execute('UPDATE subscriptions SET subscribed = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        bot.reply_to(message, "Вы успешно подписались на рассылку!" if user_language == "rus" else "Ви успішно підписалися на розсилку!")
        logger.info(f"User {message.from_user.username}(user_id - {message.from_user.id}) has successfully subscribed")

    conn.close()

@bot.message_handler(func=lambda message: message.text == 'Отписаться', content_types=['text'])
def unsubscribe(message):
    language: str = get_user_language(message.chat.id)
    user_id = message.chat.id

    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()

    cursor.execute('SELECT subscribed FROM subscriptions WHERE user_id = ?', (user_id,))
    subscribed = cursor.fetchone()[0]

    logger.info(f"User {message.from_user.id} tried to unsubscribe")
    if not subscribed:
        bot.reply_to(message, "Вы не подписаны на рассылку!" if language == "rus" else "Ви не підписані на розсилку!")
        logger.info(f"User {message.from_user.username}(user_id - {message.from_user.id}) has been already unsubscribed")
    else:
        cursor.execute('UPDATE subscriptions SET subscribed = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        bot.reply_to(message, "Вы успешно отписались от рассылки!" if language == "rus" else "Ви успішно відписалися від розсилки!")
        logger.info(f"User {message.from_user.username}(user_id - {message.from_user.id}) has successfully unsubscribed")

    conn.close()

@bot.message_handler(func=lambda message: message.text in ["Поменять язык", "Змінити мову"], content_types=["text"])
def change_language(message):
    language: str = get_user_language(message.chat.id)
    keyboard = telebot.types.InlineKeyboardMarkup()
    rus_lang = telebot.types.InlineKeyboardButton(text="Русский", callback_data="rus")
    ukr_lang = telebot.types.InlineKeyboardButton(text="Украинский", callback_data="ukr")

    keyboard.add(rus_lang, ukr_lang)
    bot.send_message(message.chat.id, "На какой язык поменять?" if language == "rus" else "На яку мову змінити?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def answer_change_language(call):
    user_language = get_user_language(call.message.chat.id)

    if call.data == "rus":
        if user_language == "rus":
            bot.answer_callback_query(call.id, "Этот язык уже стоит")
            return
        
        conn = sqlite3.connect("subscriptions.db")
        cursor = conn.cursor()

        cursor.execute("""UPDATE subscriptions SET language = 'rus' WHERE user_id == ?""", (call.message.chat.id, ))
        bot.send_message(call.message.chat.id, "Ярусский, я иду до конца")
        bot.answer_callback_query(call.id, "Язык поменян")

        conn.commit()
        conn.close()

    elif call.data == "ukr":
        if user_language == "ukr":
            bot.answer_callback_query(call.id, "Ця мова вже стоїть")
            return
        
        conn = sqlite3.connect("subscriptions.db")
        cursor = conn.cursor()
        cursor.execute("""UPDATE subscriptions SET language = 'ukr' WHERE user_id == ?""", (call.message.chat.id, ))
        bot.send_message(call.message.chat.id, "Я українець")
        bot.answer_callback_query(call.id, "Мову змінено")

        conn.commit()
        conn.close()

    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')




if __name__ == '__main__':
    sc.every().monday.at("07:00").do(send_schedule)
    sc.every().tuesday.at("07:00").do(send_schedule)
    sc.every().wednesday.at("07:00").do(send_schedule)
    sc.every().thursday.at("07:00").do(send_schedule)
    sc.every().friday.at("07:00").do(send_schedule)

    thread = Thread(target=schedule_checker, daemon=True)
    thread.start()

    bot.polling(none_stop=True)

    while thread.is_alive:                              
        thread.join(1)
