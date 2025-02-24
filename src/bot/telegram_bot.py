import telebot
from telebot.apihelper import ApiTelegramException

from threading import Lock
from time import sleep
from loguru import logger
import requests

from config import Config


class TelegramBot:
    _instance = None
    _lock = Lock()
    _initialized = False

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(TelegramBot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        config = Config.get_instance()
        telebot.apihelper.SESSION_TIME_TO_LIVE = 5 * 60
        self._bot = telebot.TeleBot(config.TOKEN)
        self._initialized = True

    @property
    def bot(self) -> telebot.TeleBot:
        return self._bot

    def start_polling(self) -> None:
        RETRY_DELAY_BASE = 2
        MAX_RETRY_DELAY = 600
        retry_delay = RETRY_DELAY_BASE

        while True:
            try:
                self._bot.polling(none_stop=True)
                break
            except (requests.exceptions.ReadTimeout, ApiTelegramException, requests.exceptions.ConnectionError) as e:
                if isinstance(e, ApiTelegramException) and e.error_code == 502:
                    error_message = "Ошибка 502: Bad Gateway. Повторная попытка..."
                elif isinstance(e, requests.exceptions.ReadTimeout):
                    error_message = "Ошибка таймаута. Повторная попытка..."
                elif isinstance(e, requests.exceptions.ConnectionError):
                    error_message = "Ошибка соединения. Повторная попытка..."

                logger.error(error_message)
                sleep(retry_delay)
                retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
