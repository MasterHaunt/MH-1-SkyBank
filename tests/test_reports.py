from pathlib import Path

import pandas as pd
import pytest

from config import ROOT_PATH
from src import reports


@pytest.fixture
def input_transactions():
    """Фикстура, получающая на вход файл с тестовыми транзакциями, фозвращает датафрейм"""
    transactions = pd.read_excel(Path(ROOT_PATH, "data/test_operations.xlsx"))
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    return transactions


def test_spending_by_weekday(input_transactions):
    """Тестирование функции расчёта средних трат по дням недели. Входные данные - датафрейм тестовых транзакций"""
    assert reports.spending_by_weekday(input_transactions, "31.12.2021").shape == (7, 1)
    assert reports.spending_by_weekday(input_transactions, "31.12.2021").loc["weekday":].empty
    assert reports.spending_by_weekday(input_transactions, "31.12.2021").loc[:].values[0] == -236.13125
    assert reports.spending_by_weekday(input_transactions, "31.12.2021").loc[:].values[1] == -79.00000
    assert reports.spending_by_weekday(input_transactions, "31.12.2021").loc[:].values[2] == -1367.00000
    assert reports.spending_by_weekday(input_transactions, "31.12.2021").loc[:].values[3] == -854.50000
    assert reports.spending_by_weekday(input_transactions, "31.12.2021").loc[:].values[4] == -8606.85500
    assert reports.spending_by_weekday(input_transactions, "31.12.2021").loc[:].values[5] == -949.84750
    assert reports.spending_by_weekday(input_transactions, "31.12.2021").loc[:].values[6] == -5987.26800
