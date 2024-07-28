import datetime
import logging
import json
import re

from config import ROOT_PATH
from pathlib import Path
from config import SOURCE_FILE
from src import utils

# Настройки логгера
logger = logging.getLogger("services_logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(Path(ROOT_PATH, "logs/services.log"), "w", encoding='utf-8')
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_transactions_mobile(start_date: datetime.datetime, stop_date: datetime.datetime) -> str | None:
    logger.info(
        f"Вызвана функция поиска транзакций с указанием мобильного телефона за период с "
        f"{start_date.strftime("%d.%m.%Y")} по {stop_date.strftime("%d.%m.%Y")}")
    mobile_number_pattern = '\d+\W\d+\W\d+\W\d+$'
    transactions = utils.get_transactions_for_period(utils.import_xlsx_transactions(SOURCE_FILE), start_date, stop_date)
    queried_transactions = []
    for index, transaction in transactions.iterrows():
        if re.search(mobile_number_pattern, transaction["Описание"], flags=re.IGNORECASE):
            queried_transactions.append({
                "date": transaction["Дата операции"].date().strftime("%d.%m.%Y"),
                "amount": transaction["Сумма платежа"],
                "category": transaction["Категория"],
                "description": transaction["Описание"]
            })

    if queried_transactions == []:
        logger.error(
            f"За период с {start_date.strftime("%d.%m.%Y")} по {stop_date.strftime("%d.%m.%Y")} "
            f"транзакций с указанием мобильного телефона не найдено!")
        return None
    logger.info(
        f"За период с {start_date.strftime("%d.%m.%Y")} по {stop_date.strftime("%d.%m.%Y")} "
        f"найдено {len(queried_transactions)} транзакций с указанием мобильного телефона.")
    result = json.dumps(queried_transactions, ensure_ascii=False)

    return result
