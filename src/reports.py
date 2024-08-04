import datetime as dt
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from config import ROOT_PATH
from src import utils
from src.decorators import report_save_to_xlsx

# Настройки логгера
logger = logging.getLogger("reports_logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(Path(ROOT_PATH, "logs/reports.log"), "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_weekday_of_transaction(input_string: pd.Series) -> pd.Series:
    """Функция преобразует строку датафрейма с информацией о транзакции в строку датафрейма заданного формата:
    <День недели, когда была проведена транзакция> : <Сумма платежа>"""

    result = pd.Series()
    result["weekday"] = input_string["Дата операции"].strftime("%A")
    result["amount"] = input_string["Сумма платежа"]

    return result


def get_weekdays_transactions_df(input_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Функция принимает на вход датафрейм с информацией о транзакциях, преобразует каждую строку датафрейма функцией
    get_weekday_of_transaction"""

    weekdays_transactions = input_dataframe.apply(get_weekday_of_transaction, axis=1)

    return weekdays_transactions


@report_save_to_xlsx(filename=input("Введите имя файла для записи отчёта: "))
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame | pd.DataFrame | None:
    """Функция расчёта средней величины расходов за последние три месяца до указанной даты.
    Если дата не указана, за дату окончания исследуемого периода принимается дата последней транзакции в датафрейме,
    поступающем на вход."""
    if date is None:
        logger.info("Вызвана функция расчёта среднего значения трат за три месяца без указания конечной даты")
        date_stop = utils.get_last_date(transactions)
        logger.info(f"Конечная дата установлена по последней транзакции: {date_stop.strftime("%d.%m.%Y")}")
    else:
        date_stop = dt.datetime.strptime(date, "%d.%m.%Y")
        logger.info(
            f"Вызвана функция расчёта среднего значения трат "
            f"за три месяца от даты: {date_stop.strftime("%d.%m.%Y")}"
        )
    try:
        # получаем начальную дату: вычитаем 90 дней (3 месяца) от конечной даты
        date_start = date_stop - dt.timedelta(days=90)

        # добавляем 23 часа 59 минут 59 секунд к конечной дате, чтобы включить также транзакции,
        # проведённые в конечную дату
        date_stop += dt.timedelta(hours=23, minutes=59, seconds=59)

        # выбираем за указанный период те транзакции, у которых "Сумма платежа" отрицательна - то есть
        # расходные операции
        selected_transactions = utils.get_transactions_for_period(transactions, date_start, date_stop).loc[
            transactions["Сумма платежа"] < 0
        ]
        # Обрабатываем отобранные транзакции функцией определения дня недели, группируем по дням недели, вычисляем
        # среднее значение расходов
        weekdays_avg_spends = get_weekdays_transactions_df(selected_transactions).groupby("weekday").mean()
        logger.info(
            f"Функция расчёта среднего значения трат за период"
            f" с {date_start.strftime("%d.%m.%Y")} по"
            f" {date_stop.strftime("%d.%m.%Y")} успешно завершила работу."
        )
        print(
            f"Функция расчёта среднего значения трат за период"
            f" с {date_start.strftime("%d.%m.%Y")} по"
            f" {date_stop.strftime("%d.%m.%Y")} успешно завершила работу."
        )
        return weekdays_avg_spends
    except Exception as e:
        logger.info(
            f"Функция расчёта среднего значения трат за период"
            f" с {date_start.strftime("%d.%m.%Y")} по"
            f" {date_stop.strftime("%d.%m.%Y")} завершилась с ошибкой {e}."
        )
        print(
            f"Функция расчёта среднего значения трат за период"
            f" с {date_start.strftime("%d.%m.%Y")} по"
            f" {date_stop.strftime("%d.%m.%Y")} завершилась с ошибкой {e}."
        )
        return None
