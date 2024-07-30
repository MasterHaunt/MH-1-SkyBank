import datetime as dt
import json
import logging
import os
from pathlib import Path
import requests as re
from dotenv import load_dotenv

from config import ROOT_PATH

# Настройки логгера
logger = logging.getLogger("views_logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(Path(ROOT_PATH, "logs/views.log"), "w", encoding="utf-8")
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


def get_user_settings() -> tuple:
    """Функция считывает json-файл с настройками пользователя, возвращает кортеж из двух списков:
    в первом записаны валюты, во втором - акции, стоимость которых необходимо отобразить"""
    user_settings_path = Path(ROOT_PATH, "user_settings.json")
    logger.info(f"Загрузка настроек пользователя из файла {user_settings_path}")
    with open(user_settings_path) as file:
        user_settings = json.load(file)
        logger.info("Настройки пользователя получены")
    return user_settings["user_currencies"], user_settings["user_stocks"]


def get_currency_rates(currencies: str):
    """Функция обращается к сайту через API для получения курсов валют, указанных в <user_settings.json>"""

    logger.info(f"Вызов функции get_currency_rates с параметрами: {currencies}")
    logger.info("Получение API-ключа из файла переменных окружения...")
    load_dotenv()
    apilayer_key = os.getenv("APILAYER_KEY")
    logger.info("API-ключ получен")
    url = "https://api.apilayer.com/exchangerates_data/latest"
    params = {"base": "RUB", "symbols": ",".join(currencies)}
    response = re.get(url, params=params, headers={"apikey": apilayer_key})

    if response.status_code == 200:
        logger.info(f" Сайт {url[:26]} передал запрошенные данные")
        response_data = response.json()
        currency_rates = []
        for currency in currencies:
            currency_rates.append({"currency": currency, "rate": round(1 / response_data["rates"][currency], 2)})
        return currency_rates
    else:
        logger.error(f"Сайт {url[:26]} не отвечает")
        raise re.RequestException


def get_stock_prices(stocks: list[str]):
    """Функция обращается к сайту через API для получения курсов акций, указанных в <user_settings.json>"""
    logger.info(f"Вызов функции get_stock_prices с параметрами {stocks}")
    logger.info("Получение API-ключа из файла переменных окружения...")
    load_dotenv()
    alphavantage_key = os.getenv("ALPHAVANTAGE_KEY")
    logger.info("API-ключ получен")
    stock_prices = []
    for stock in stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={alphavantage_key}"
        response = re.get(url)
        if response.status_code != 200:
            logger.error(f"Не удалось получить информацию о стоимости акций {stock} с сайта {url[:27]}")
            raise re.RequestException
        logger.info(f"Получен ответ о стоимости акций {stock} с сайта {url[:27]}")
        response_data = response.json()
        stock_prices.append({"stock": stock, "price": round(float(response_data["Global Quote"]["05. price"]), 3)})
    return stock_prices
