import json
import os
from dotenv import load_dotenv
from threading import Lock
from loguru import logger


class Config:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        logger.add('../../logs/logging.log', format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}',
                level='DEBUG', rotation='10 MB', compression='zip')
        
        load_dotenv()
        self.TOKEN = os.getenv('TOKEN')
        self.ADMINS = [int(admin) for admin in os.getenv('ADMINS').split(',')]
        
        with open('../data/localization.json', 'r', encoding='utf-8') as file:
            BUTTON_TEXTS = json.load(file)
        self.BUTTON_TEXTS = BUTTON_TEXTS
        
        self.FIRST_WEEK_NUMBER = 36
        self.saturday_lessons = False
        self._initialized = True

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

localized_weekday_names = {
    "rus": {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
        "saturday": "Суббота",
        "sunday": "Воскресенье"
    },
    "ukr": {
        "monday": "Понеділок",
        "tuesday": "Вівторок",
        "wednesday": "Середа",
        "thursday": "Четвер",
        "friday": "П'ятниця",
        "saturday": "Субота",
        "sunday": "Неділя"
    }
}

day_names = [None, 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']

quote_tags = [
    'Age',
    'Athletics',
    'Business',
    'Change',
    'Character',
    'Competition',
    'Conservative',
    'Courage',
    'Creativity',
    'Education',
    'Ethics',
    'Failure',
    'Faith',
    'Family',
    'Famous Quotes',
    'Film',
    'Freedom',
    'Friendship',
    'Future',
    'Generosity',
    'Genius',
    'Gratitude',
    'Happiness',
    'Health',
    'History',
    'Honor',
    'Humor',
    'Humorous',
    'Imagination',
    'Inspirational',
    'Knowledge',
    'Leadership',
    'Life',
    'Literature',
    'Love',
    'Mathematics',
    'Motivational',
    'Nature',
    'Opportunity',
    'Pain',
    'Perseverance',
    'Philosophy',
    'Politics',
    'Power Quotes',
    'Proverb',
    'Religion',
    'Sadness',
    'Science',
    'Self',
    'Self Help',
    'Social Justice',
    'Society',
    'Spirituality',
    'Sports',
    'Stupidity',
    'Success',
    'Technology',
    'Time',
    'Tolerance',
    'Truth',
    'Virtue',
    'War',
    'Weakness',
    'Wellness',
    'Wisdom',
    'Work'
]
