import datetime as dt
import logging
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from config import ROOT_PATH

# Настройки логгера
logger = logging.getLogger("decorators_logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(Path(ROOT_PATH, "logs/decorators.log"), "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def report_save_to_xlsx(filename: str | None = None) -> Callable:
    """Функция-декоратор, записывающая отчёт в указанный файл. Если файл не указан, отчёт будет записан
    в файл ./reports/SkyBank-report_<текущая дата>"""

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            if filename == "":
                logger.info(f"Вызван декоратор для записи отчёта в файл reports/SkyBank-report_{dt.date.today()}.xlsx")
                report_name = f"SkyBank-report_{dt.date.today()}"
            else:
                logger.info(f"Вызван декоратор для записи отчёта в файл reports/{filename}.xlsx")
                report_name = filename
            result = func(*args, **kwargs)
            result.to_excel(f"reports/{report_name}.xlsx")
            logger.info(f"Декоратор report_save_to_xlsx - записал отчёт в файл reports/{report_name}.xlsx")
            print(f"Отчёт о средних тратах за три месяца записан в файл reports/{report_name}.xlsx")

        return inner

    return wrapper
