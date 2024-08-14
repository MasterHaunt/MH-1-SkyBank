import datetime as dt
from pathlib import Path

import pytest

from config import ROOT_PATH
from src import services


@pytest.mark.parametrize(
    "start_date, stop_date, result_string",
    [
        (
            dt.datetime(2021, 12, 1, 00, 00),
            dt.datetime(2021, 12, 31, 23, 59),
            '[{"date": "03.12.2021", "amount": -200.0, "category": "Мобильная связь", '
            '"description": "Тинькофф Мобайл +7 995 555-55-55"}, '
            '{"date": "01.12.2021", "amount": -20.0, "category": "Мобильная связь", '
            '"description": "МегаФон +7 921 333-33-33"}]',
        ),
        (
            dt.datetime(2021, 12, 1, 00, 00),
            dt.datetime(2021, 12, 2, 00, 00),
            '[{"date": "01.12.2021", "amount": -20.0, "category": "Мобильная связь", '
            '"description": "МегаФон +7 921 333-33-33"}]',
        ),
    ],
)
def test_get_transactions_mobile(start_date, stop_date, result_string):
    """Тестирование функции поиска транзакций, в которых указан номер мобильного телефона"""
    assert (
        services.get_transactions_mobile((Path(ROOT_PATH, "data/test_operations.xlsx")), start_date, stop_date)
        == result_string
    )


def test_get_transactions_mobile_empty():
    """Тестирование функции поиска транзакций, в которых указан номер мобильного телефона, в случае, если
    в указанном диапазоне дат искомых транзакций нет"""
    assert (
        services.get_transactions_mobile(
            Path(ROOT_PATH, "data/test_operations.xlsx"),
            dt.datetime(2021, 11, 29, 00, 00),
            dt.datetime(2021, 11, 30, 18, 00),
        )
        is None
    )
    assert (
        services.get_transactions_mobile(
            Path(ROOT_PATH, "data/test_operations.xlsx"),
            dt.datetime(2021, 12, 4, 00, 00),
            dt.datetime(2021, 12, 30, 18, 00),
        )
        is None
    )
