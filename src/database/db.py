import sqlite3
from telebot import types
from bot.config import Config

configuration = Config.get_instance()
subscriptions_db_path = '../data/databases/subscriptions.db'
stickers_db_path = '../data/databases/stickers.db'

def get_user_language(chat_id: int) -> str:
    '''Функция для получения языка пользователя'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT language FROM subscriptions WHERE user_id == ?""", (chat_id, ))
        fetched = cursor.fetchone()

    language = fetched[0] if fetched is not None else "rus"

    return language

def get_user_group(chat_id: int) -> str:
    '''Функция для получения группы пользователя'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT user_group FROM subscriptions WHERE user_id == ?""", (chat_id, ))
        fetched = cursor.fetchone()

    group = fetched[0] if fetched is not None else 1

    return group

def get_user_quote_tag(chat_id: int) -> str:
    '''Функция для получения тэга цитаты пользователя'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT quote_tag FROM subscriptions WHERE user_id == ?""", (chat_id, ))
        fetched = cursor.fetchone()

    tag = fetched[0] if fetched is not None else 'Success'

    return tag

def get_stickers() -> list[str]:
    with sqlite3.connect(stickers_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT sticker_id, keyword FROM stickers""")
        stickers = cursor.fetchall()
    
    return stickers

def get_user_admin_status(chat_id: int) -> bool:
    '''Функция для получения статуса админа пользователя'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT is_admin FROM subscriptions WHERE user_id == ?""", (chat_id, ))
        fetched = cursor.fetchone()

    is_admin = fetched[0] if fetched is not None else False

    return is_admin

def get_user_subscribed(chat_id: int) -> None | bool:
    '''Функция для получения статуса подписки пользователя'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT subscribed FROM subscriptions WHERE user_id == ?""", (chat_id, ))
        fetched = cursor.fetchone()

    return fetched

def update_with_query_and_user_id(query: str, user_id: int) -> None:
    '''Функция для обновления данных в БД'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id, ))
        conn.commit()

def update_selected_quotes_tag(tag: str, user_id: int) -> None:
    '''Функция для обновления тэга цитаты пользователя'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE subscriptions SET quote_tag = ? WHERE user_id == ?""", (tag, user_id))
        conn.commit()

def update_user_language(language: str, user_id: int) -> None:
    '''Функция для обновления языка пользователя'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE subscriptions SET language = ? WHERE user_id == ?""", (language, user_id))
        conn.commit()

def update_user_group(group: int, user_id: int) -> None:
    '''Функция для обновления группы пользователя'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE subscriptions SET user_group = ? WHERE user_id == ?""", (group, user_id))
        conn.commit()

def get_user_quotes_subscription(user_id: int) -> None | bool:
    '''Функция для получения статуса подписки на цитаты пользователя'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT quotes_subscribed FROM subscriptions WHERE user_id == ?""", (user_id, ))
        fetched = cursor.fetchone()

    return fetched

def get_user_subscriptions() -> list[tuple]:
    '''Функция для получения подписок пользователей'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT user_id FROM subscriptions""")
        fetched = cursor.fetchall()

    return fetched

def delete_user(user_id: int) -> None:
    '''Функция для удаления пользователя из БД'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """DELETE FROM subscriptions WHERE user_id == ?""", (user_id, ))
        conn.commit()

def create_table() -> None:
    '''Функция для создания таблицы в БД'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS subscriptions
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        user_id INTEGER NOT NULL,
                        subscribed INTEGER NOT NULL CHECK (subscribed IN (0, 1)),
                        language TEXT NOT NULL CHECK (language IN ('rus', 'ukr')),
                        is_admin INTEGER NOT NULL CHECK (is_admin IN (0, 1)),
                        user_group INTEGER DEFAULT 1 CHECK (user_group IN (1, 2)),
                        quotes_subscribed INTEGER DEFAULT 0 CHECK (quotes_subscribed IN (0, 1)),
                        quote_tag TEXT DEFAULT 'Success')""")
        conn.commit()

def get_user(user_id: int) -> None | tuple:
    '''Функция для получения пользователя из БД'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM subscriptions WHERE user_id == ?""", (user_id, ))
        fetched = cursor.fetchone()

    return fetched

def add_user(username: str, user_id: int, subscribed: int, language: str, is_admin: int) -> None:
    '''Функция для добавления пользователя в БД'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO subscriptions (username, user_id, subscribed, language, is_admin) VALUES (?, ?, ?, ?, ?)""",
                    (username, user_id, subscribed, language, is_admin))
        conn.commit()

def update_user(username: str, subscribed: int, language: str, is_admin: int, user_id: int) -> None:
    '''Функция для обновления данных пользователя в БД'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE subscriptions 
                    SET username = ?, subscribed = ?, language = ?, is_admin = ? 
                    WHERE user_id == ?""",
                    (username, subscribed, language, is_admin, user_id))
        conn.commit()

def get_subcribe_unsubscibe_button(language: str, user_id: int) -> types.KeyboardButton:
    '''Функция для получения кнопки подписки'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT subscribed FROM subscriptions WHERE user_id == ?""", (user_id, ))
        fetched = cursor.fetchone()
        subscribed = fetched[0] if fetched else False

    return types.KeyboardButton(configuration.BUTTON_TEXTS[language]["unsubscribe"] if subscribed else configuration.BUTTON_TEXTS[language]["subscribe"])

def get_subcribe_unsubscibe_quote_button(language: str, user_id: int) -> types.KeyboardButton:
    '''Функция для получения кнопки подписки на цитаты'''

    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT quotes_subscribed FROM subscriptions WHERE user_id == ?""", (user_id, ))
        fetched = cursor.fetchone()
        quotes_subscribed = fetched[0] if fetched else False

    return types.KeyboardButton(configuration.BUTTON_TEXTS[language]["unsubscribe_quotes"] if quotes_subscribed else configuration.BUTTON_TEXTS[language]["subscribe_quotes"])

def get_subscribers() -> list[tuple]:
    '''Функция для получения подписчиков'''
    
    with sqlite3.connect(subscriptions_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT user_id, language, user_group, quotes_subscribed FROM subscriptions WHERE subscribed == 1""")
        fetched = cursor.fetchall()

    return fetched
