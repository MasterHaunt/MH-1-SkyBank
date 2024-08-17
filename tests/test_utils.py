import datetime as dt
from pathlib import Path
from unittest.mock import patch

import pytest

from config import ROOT_PATH
from src import utils


def test_import_xlsx_transactions():
    """Тестирование функции загрузки и преобразования в датафрейм данных о транзакциях из тестового xlsx-файла"""
    assert utils.import_xlsx_transactions(Path(ROOT_PATH, "data/test_operations.xlsx")).shape == (40, 15)


def test_get_last_datetime():
    """Тестирование функции определения даты и времени последней транзакции"""
    assert utils.get_last_datetime(
        utils.import_xlsx_transactions(Path(ROOT_PATH, "data/test_operations.xlsx"))
    ) == dt.datetime(2021, 12, 31, 16, 44, 00)


def test_get_last_date():
    """Тестирование функции определения даты последней транзакции"""
    assert utils.get_last_date(
        utils.import_xlsx_transactions(Path(ROOT_PATH, "data/test_operations.xlsx"))
    ) == dt.datetime(2021, 12, 31, 00, 00, 00)


@pytest.mark.parametrize(
    "query_date, df_shape",
    [(dt.datetime(2021, 12, 31, 23, 59, 59), (40, 15)), (dt.datetime(2021, 12, 15, 00, 00, 00), (11, 15))],
)
def test_get_transactions_for_month(query_date, df_shape):
    """Тестирование функции отбора транзакций за текущий (указанный) месяц"""
    assert (
        utils.get_transactions_for_month(
            (utils.import_xlsx_transactions(Path(ROOT_PATH, "data/test_operations.xlsx"))), query_date
        ).shape
        == df_shape
    )
    assert (
        utils.get_transactions_for_month(
            (utils.import_xlsx_transactions(Path(ROOT_PATH, "data/test_operations.xlsx"))),
            dt.datetime(2021, 11, 30, 22, 00, 00),
        )
        is None
    )


@pytest.mark.parametrize(
    "first_date, last_date, df_shape",
    [
        (dt.datetime(2021, 12, 1, 15, 00), dt.datetime(2021, 12, 31, 12, 00), (40, 15)),
        (dt.datetime(2021, 12, 15, 18, 00), dt.datetime(2021, 12, 31, 16, 00), (29, 15)),
        (dt.datetime(2021, 11, 1, 20, 00), dt.datetime(2021, 12, 1, 19, 0), (1, 15)),
    ],
)
def test_get_transactions_for_period(first_date, last_date, df_shape):
    """Тестирование функции отбора транзакций за указанный период"""
    assert (
        utils.get_transactions_for_period(
            (utils.import_xlsx_transactions(Path(ROOT_PATH, "data/test_operations.xlsx"))), first_date, last_date
        ).shape
        == df_shape
    )
    assert (
        utils.get_transactions_for_period(
            (utils.import_xlsx_transactions(Path(ROOT_PATH, "data/test_operations.xlsx"))),
            dt.datetime(2021, 11, 1),
            dt.datetime(2021, 11, 20),
        )
        is None
    )


def test_get_transactions_analyzed():
    """Тестирование функции вывода совокупных трат по картам"""
    assert utils.get_transactions_analyzed(
        (utils.import_xlsx_transactions(Path(ROOT_PATH, "data/test_operations.xlsx")))
    ) == [
        {"last_digits": "*4556", "total_spent": -5526.4, "cashback": 55.26},
        {"last_digits": "*5091", "total_spent": -4524.89, "cashback": 45.25},
        {"last_digits": "*7197", "total_spent": -6220.59, "cashback": 62.21},
    ]


def test_get_transactions_top_five():
    """Тестирование функции поиска пяти наибольших по сумме транзакций"""
    assert utils.get_transactions_top_five(
        (utils.import_xlsx_transactions(Path(ROOT_PATH, "data/test_operations.xlsx")))
    ) == [
        {
            "date": "30.12.2021",
            "amount": 174000.0,
            "category": "Пополнения",
            "description": "Пополнение через Газпромбанк",
        },
        {"date": "23.12.2021", "amount": 20000.0, "category": "Другое", "description": "Иван С."},
        {
            "date": "08.12.2021",
            "amount": 3500.0,
            "category": "Пополнения",
            "description": "Внесение наличных через банкомат Тинькофф",
        },
        {"date": "06.12.2021", "amount": 500.0, "category": "Пополнения", "description": "Перевод с карты"},
        {"date": "16.12.2021", "amount": 453.0, "category": "Бонусы", "description": "Кэшбэк за обычные покупки"},
    ]


def test_get_currency_rates():
    """Тестирование функции получения курсов валют (использована заглушка mock для замены обращения к сайту)"""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"base": "RUB", "rates": {"USD": 0.02, "EUR": 0.01, "CNY": 0.1}}
        assert utils.get_currency_rates(["USD", "EUR", "CNY"]) == [
            {"currency": "USD", "rate": 50.0},
            {"currency": "EUR", "rate": 100.0},
            {"currency": "CNY", "rate": 10.0},
        ]

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 201
        with pytest.raises(Exception):
            assert utils.get_currency_rates(["USD", "EUR", "CNY"])


def test_get_stocks_prices():
    """Тестирование функции получения стоимости акций (использована заглушка mock для замены обращения к сайту)"""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"Global Quote": {"05. price": "205.95"}}
        assert utils.get_stock_prices(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]) == [
            {"stock": "AAPL", "price": 205.95},
            {"stock": "AMZN", "price": 205.95},
            {"stock": "GOOGL", "price": 205.95},
            {"stock": "MSFT", "price": 205.95},
            {"stock": "TSLA", "price": 205.95},
        ]

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 201
        with pytest.raises(Exception):
            assert utils.get_stock_prices(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
