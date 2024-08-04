import datetime as dt
import json
import logging
from pathlib import Path

from config import ROOT_PATH, SOURCE_FILE
from src import utils

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


def main_page() -> str:
    """Функция Главной страницы. Запрашивает у пользователя дату, относительно которой будет проводится анализ
    транзакций. Если дата не введена (введена пустая строка) - за введённую дату принимается дата последней транзакции
    в анализируемом Excel-файле. Возвращает json со следующими данными:
    - Приветствие (в зависимости от текущего времени суток)
    - суммарные траты по всем картам с начала месяца введённой даты по введённую дату
    - пять наиболее крупных по сумме транзакций за тот же период
    - курсы валют, указанных в файле с пользовательскими настройками (user_settings.json)
    - стоимость акций, указанных в файле с пользовательскими настройками (user_settings.json)"""

    logger.info("Вызвана функция главной страницы")
    transactions = utils.import_xlsx_transactions(SOURCE_FILE)
    greeting = say_hello()
    while True:
        user_input = input(
            "Введите дату в формате ДД.ММ.ГГГГ для формирования отчёта о транзакциях, "
            "либо нажмите <Enter> для выбора последней даты: "
        )
        if user_input == "":
            user_date = utils.get_last_datetime(transactions)
            logger.info(f"Пользователь не ввёл дату. Выбрана дата последней транзакции: {user_date}")
            break
        else:
            try:
                user_date = dt.datetime.strptime(user_input, "%d.%m.%Y")
                logger.info(f"Пользователь ввёл дату {user_date}")
                break
            except Exception:
                print("Дата введена некорректно! Повторите ввод: ")
                logger.info("Пользователь ввёл некорректную дату")

    month_transactions = utils.get_transactions_for_month(transactions, user_date)
    analyzed_transactions = utils.get_transactions_analyzed(month_transactions)
    top_five_transactions = utils.get_transactions_top_five(month_transactions)
    currency_rates = utils.get_currency_rates(get_user_settings()[0])
    stock_prices = utils.get_stock_prices(get_user_settings()[1])

    main_page_json = json.dumps(
        {
            "greeting": greeting,
            "cards": analyzed_transactions,
            "top_transactions": top_five_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        },
        indent=4,
        ensure_ascii=False,
    )
    logger.info("Функция главной страницы завершила работу")
    return main_page_json
