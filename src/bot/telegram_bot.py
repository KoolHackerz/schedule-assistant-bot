import telebot
from telebot.apihelper import ApiTelegramException
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import uvicorn
import ssl
import os

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
        self._config = config
        self._initialized = True
        self._app = None

        if config.USE_WEBHOOK:
            self._app = FastAPI()

            @self._app.get('/')
            def index():
                return PlainTextResponse('')
            
            @self._app.post(config.WEBHOOK_URL_PATH)
            async def webhook(request: Request):
                if request.headers.get('content-type') == 'application/json':
                    json_string = await request.body()
                    update = telebot.types.Update.de_json(json_string.decode('utf-8'))
                    self._bot.process_new_updates([update])
                    return Response(status_code=200)
                else:
                    return Response(status_code=400, content='Invalid content type')
        
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
                self._bot.remove_webhook()
                logger.info("Starting polling...")
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
    
    def start_webhook(self) -> None:
        if not self._config.USE_WEBHOOK:
            logger.info("Webhook is not enabled. Skipping webhook start.")
            return
        
        self._bot.remove_webhook()
        sleep(0.1)

        try:
            webhook_url = f"{self._config.WEBHOOK_URL_BASE}{self._config.WEBHOOK_URL_PATH}"
            logger.info(f"Setting webhook to {webhook_url}")

            if not os.path.exists(self._config.WEBHOOK_SSL_CERT):
                logger.error(f"SSL сертификат не найден: {self._config.WEBHOOK_SSL_CERT}")
                return
                
            if not os.path.exists(self._config.WEBHOOK_SSL_PRIV):
                logger.error(f"SSL приватный ключ не найден: {self._config.WEBHOOK_SSL_PRIV}")
                return
            
            if self._config.USE_SSL_CERT:
                with open(self._config.WEBHOOK_SSL_CERT, 'r') as cert:
                    self._bot.set_webhook(
                        url=webhook_url,
                        certificate=cert,
                )
            else:
                self._bot.set_webhook(url=webhook_url)
            
            logger.info("Webhook set successfully.")

            logger.info("Starting webhook server...")
            uvicorn.run(
                self._app,
                host=self._config.WEBHOOK_LISTEN,
                port=self._config.WEBHOOK_PORT,
                log_level="info",
                ssl_certfile=self._config.WEBHOOK_SSL_CERT,
                ssl_keyfile=self._config.WEBHOOK_SSL_PRIV,
            )
        
        except Exception as e:
            logger.error(f"Failed to start webhook: {e}")
    
    def start(self):
        if self._config.USE_WEBHOOK:
            self.start_webhook()
        else:
            self.start_polling()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
