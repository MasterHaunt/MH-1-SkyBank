import datetime as dt
import json
import logging
from config import ROOT_PATH
from pathlib import Path
import pandas as pd

from src.external_api import currency_rate, stocks_rate
from src.utils import date_converter

# Настройки логгирования
logger = logging.getLogger("views_logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(Path(ROOT_PATH, "logs/views.log"), "w", encoding='utf-8')
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def say_hello() -> str:
    """Функция возвращает приветствие в зависимости от текущего времени суток"""
    logger.info("Функция get_greeting вызвана")
    current_hour = dt.datetime.now().hour
    if current_hour >= 23 or current_hour < 4:
        return "Доброй ночи!"
    elif 4 <= current_hour < 12:
        return "Доброе утро!"
    elif 12 <= current_hour < 16:
        return "Добрый день!"
    else:
        return "Добрый вечер!"