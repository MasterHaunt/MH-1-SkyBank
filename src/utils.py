import datetime
import logging

import pandas as pd
from pandas import DataFrame
from config import ROOT_PATH
from pathlib import Path

logger = logging.getLogger("utils_logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(Path(ROOT_PATH, "logs/utils.log"), "w", encoding='utf-8')
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def import_xlsx_transactions(xlsx_filename: str) -> DataFrame | DataFrame | None:
    """Функция чтения информации о транзакциях из файла *.xlsx. На вход принимает имя файла с данными о транзакциях, на
    выходе возвращает датафрейм. Если файл с указанным именем пуст или отсутствует - функция вернёт None """

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


def get_last_datetime(transactions: DataFrame) -> datetime:
    return max(transactions["Дата операции"])


def get_transactions_for_period(transactions: DataFrame, query_date: datetime.datetime) -> DataFrame | DataFrame | None:
    """Функция отбора информации о транзакциях с первого числа месяца заданной даты по заданную дату"""
    first_date = query_date.replace(day=1, hour=0, minute=0, second=0)
    logger.info(
        f"Вызвана функция отбора транзакций с {first_date.strftime("%d.%m.%Y")} по {query_date.strftime("%d.%m.%Y")}")
    selected_transactions = transactions.loc[
        (transactions["Дата операции"] <= query_date) & (transactions["Дата операции"] >= first_date)]
    if not selected_transactions.empty:
        logger.info(
            f"Выбраны транзакции с {first_date.strftime("%d.%m.%Y")} по {query_date.strftime("%d.%m.%Y")}")
        return selected_transactions
    else:
        logger.error(
            f"В период с {first_date.strftime("%d.%m.%Y")} по {query_date.strftime("%d.%m.%Y")} транзакций не найдено!")


def get_transactions_analyzed(transactions: DataFrame) -> list[dict]:
    """Функция анализа транзакций: суммирование расходов по картам, расчёт кэшбэка"""
    logger.info("Вызов функции get_transactions_analyzed")

    transactions_analyzed = (transactions.loc[transactions["Сумма платежа"] < 0].groupby(by="Номер карты").agg(
        "Сумма платежа").sum().to_dict())

    cards = []
    for card_number, total_expenses in transactions_analyzed.items():
        cards.append({
            "last_digits": card_number,
            "total_spent": round(total_expenses, 2),
            "cashback": abs(round(total_expenses / 100, 2))
        })
    logger.info("- - - Получена информация по расходам и суммам кэшбэка")
    return cards


def get_transactions_top_five(transactions: DataFrame) -> list[dict]:
    """Функция выбора пяти транзакций с наибольшей суммой """
    logger.info("Вызов функции get_transactions_top_five")

    top_transactions = (
        transactions.sort_values(by="Сумма платежа", ascending=False).iloc[:5].to_dict(orient="records")
    )
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
    logger.info("- - - Получена информация о топ-5 транзакциях")
    return transactions_top_five


def get_currency_rates(currencies: str):
    pass


def get_stock_prices(stocks: str):
    pass
