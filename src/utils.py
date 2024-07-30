import datetime
import logging
import os
import pandas as pd
import requests as req
from dotenv import load_dotenv
from config import ROOT_PATH
from pathlib import Path

# Настройки логгера
logger = logging.getLogger("utils_logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(Path(ROOT_PATH, "logs/utils.log"), "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def import_xlsx_transactions(xlsx_filename: str) -> pd.DataFrame | pd.DataFrame | None:
    """Функция чтения информации о транзакциях из файла *.xlsx. На вход принимает имя файла с данными о транзакциях, на
    выходе возвращает датафрейм. Если файл с указанным именем пуст или отсутствует - функция вернёт None"""

    logger.info("Вызвана функция загрузки информации о транзакциях из XLSX-файла")
    try:
        try:
            transactions = pd.read_excel(xlsx_filename)
            transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
            if transactions.empty:
                logger.error("В указанном XLSX-файле информация отсутствует!")
                print("В указанном XLSX-файле информация отсутствует!")
                return None
            else:
                logger.info("Информация о транзакциях успешно загружена")
                return transactions
        except Exception as e:
            logger.error(f"Функция чтения информации о транзакциях из XLSX-файла завершилась ошибкой: {e}")
            print("Ошибка чтения/декодирования файла!")
            return None
    except FileNotFoundError as fnfe:
        logger.error(f"Функция чтения информации о транзакциях завершилась ошибкой: {fnfe}")
        print("Ошибка: файл не найден")
        return None


def get_last_datetime(transactions: pd.DataFrame) -> datetime:
    return max(transactions["Дата операции"])


def get_transactions_for_month(transactions: pd.DataFrame, query_date: datetime.datetime) -> pd.DataFrame | pd.DataFrame | None:
    """Функция отбора информации о транзакциях с первого числа месяца заданной даты по заданную дату"""
    first_date = query_date.replace(day=1, hour=0, minute=0, second=0)
    logger.info(
        f"Вызвана функция отбора транзакций с {first_date.strftime("%d.%m.%Y")} по {query_date.strftime("%d.%m.%Y")}"
    )
    selected_transactions = transactions.loc[
        (transactions["Дата операции"] <= query_date) & (transactions["Дата операции"] >= first_date)
        ]
    if not selected_transactions.empty:
        logger.info(f"Выбраны транзакции с {first_date.strftime("%d.%m.%Y")} по {query_date.strftime("%d.%m.%Y")}")
        return selected_transactions
    else:
        logger.error(
            f"В период с {first_date.strftime("%d.%m.%Y")} по {query_date.strftime("%d.%m.%Y")} транзакций не найдено!"
        )
        return None


def get_transactions_for_period(
        transactions: pd.DataFrame, date_start: datetime.datetime, date_stop: datetime.datetime
) -> pd.DataFrame | pd.DataFrame | None:
    """Функция отбора информации о транзакциях за заданный период времени"""
    logger.info(
        f"Вызвана функция отбора транзакций с {date_start.strftime("%d.%m.%Y")} по {date_stop.strftime("%d.%m.%Y")}"
    )
    selected_transactions = transactions.loc[
        (transactions["Дата операции"] <= date_stop) & (transactions["Дата операции"] >= date_start)
        ]
    if not selected_transactions.empty:
        logger.info(f"Выбраны транзакции с {date_start.strftime("%d.%m.%Y")} по {date_stop.strftime("%d.%m.%Y")}")
        return selected_transactions
    else:
        logger.error(
            f"В период с {date_start.strftime("%d.%m.%Y")} по {date_stop.strftime("%d.%m.%Y")} транзакций не найдено!"
        )
        return None


def get_transactions_analyzed(transactions: pd.DataFrame) -> list[dict]:
    """Функция анализа транзакций: суммирование расходов по картам, расчёт кэшбэка"""
    logger.info("Вызов функции get_transactions_analyzed")

    transactions_analyzed = (
        transactions.loc[transactions["Сумма платежа"] < 0]
        .groupby(by="Номер карты")
        .agg("Сумма платежа")
        .sum()
        .to_dict()
    )

    cards = []
    for card_number, total_expenses in transactions_analyzed.items():
        cards.append(
            {
                "last_digits": card_number,
                "total_spent": round(total_expenses, 2),
                "cashback": abs(round(total_expenses / 100, 2)),
            }
        )
    logger.info("Получена информация по расходам и суммам кэшбэка")
    return cards


def get_transactions_top_five(transactions: pd.DataFrame) -> list[dict]:
    """Функция выбора пяти транзакций с наибольшей суммой"""
    logger.info("Вызов функции get_transactions_top_five")

    top_transactions = transactions.sort_values(by="Сумма платежа", ascending=False).iloc[:5].to_dict(orient="records")
    transactions_top_five = []
    for transaction in top_transactions:
        transactions_top_five.append(
            {
                "date": transaction["Дата операции"].date().strftime("%d.%m.%Y"),
                "amount": transaction["Сумма платежа"],
                "category": transaction["Категория"],
                "description": transaction["Описание"],
            }
        )
    logger.info("Получена информация о топ-5 транзакциях")
    return transactions_top_five


def get_currency_rates(currencies: str):
    """Функция обращается к сайту через API для получения курсов валют, указанных в <user_settings.json>"""

    logger.info(f"Вызов функции get_currency_rates с параметрами: {currencies}")
    logger.info("Получение API-ключа из файла переменных окружения...")
    load_dotenv()
    apilayer_key = os.getenv("APILAYER_KEY")
    logger.info("API-ключ получен")
    url = "https://api.apilayer.com/exchangerates_data/latest"
    params = {"base": "RUB", "symbols": ",".join(currencies)}
    response = req.get(url, params=params, headers={"apikey": apilayer_key})

    if response.status_code == 200:
        logger.info(f" Сайт {url[:26]} передал запрошенные данные")
        response_data = response.json()
        currency_rates = []
        for currency in currencies:
            currency_rates.append({"currency": currency, "rate": round(1 / response_data["rates"][currency], 2)})
        return currency_rates
    else:
        logger.error(f"Сайт {url[:26]} не отвечает")
        raise req.RequestException


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
        response = req.get(url)
        if response.status_code != 200:
            logger.error(f"Не удалось получить информацию о стоимости акций {stock} с сайта {url[:27]}")
            raise req.RequestException
        logger.info(f"Получен ответ о стоимости акций {stock} с сайта {url[:27]}")
        response_data = response.json()
        stock_prices.append({"stock": stock, "price": round(float(response_data["Global Quote"]["05. price"]), 3)})
    return stock_prices
