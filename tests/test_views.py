from datetime import datetime
from unittest.mock import patch

import pytest

from src import views


@pytest.mark.parametrize(
    "time_hour, greeting",
    [
        (23, "Доброй ночи!"),
        (0, "Доброй ночи!"),
        (1, "Доброй ночи!"),
        (3, "Доброй ночи!"),
        (4, "Доброе утро!"),
        (9, "Доброе утро!"),
        (11, "Доброе утро!"),
        (12, "Добрый день!"),
        (15, "Добрый день!"),
        (16, "Добрый вечер!"),
        (20, "Добрый вечер!"),
        (22, "Добрый вечер!"),
    ],
)
def test_say_hello(time_hour, greeting):
    """Тестирование функции вывода приветствия в зависимости от текущего часа"""
    with patch("datetime.datetime") as mock_datetime:
        mock_now = datetime(2024, 8, 6, time_hour, 0, 0)
        mock_datetime.now.return_value = mock_now
        assert views.say_hello() == greeting


def test_get_user_settings():
    """Тестирование функции загрузки пользовательских настроек из json-файла"""
    assert views.get_user_settings() == (["USD", "EUR", "CNY"], ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
