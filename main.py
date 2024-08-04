import os
from pathlib import Path

from src import utils
from src import views

from config import SOURCE_FILE

import datetime as dt
import logging

# Настройки логгера
logger = logging.getLogger("main_logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(Path(os.getcwd(), "logs/main.log"), "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def main_function():
    """Функция взаимодействия с пользователем. Предлагает сделать выбор:
    - Вывод данных главной страницы
    - Произвести поиск транзакций с номерами мобильных телефонов
    - Вывести отчёт о средних тратах по дням недели за три месяца от указанной даты"""

    logger.info("Вызвана функция main_function")
    print(views.say_hello())

    while True:
        print("Выберите функцию:")
        print("1 : Вывод json-строки главной страницы")
        print("2 : Поиск транзакций с номерами мобильных телефонов")
        print("3 : Отчёт о средних тратах по дням недели за три месяца")
        print("0 : Завершить работу программы")

        user_function = input("Выбор : ")

        if user_function == "1":
            logger.info("Выбран вывод json-строки главной страницы")
            print("Выбран вывод json-строки главной страницы")
            print(views.main_page())
            break

        elif user_function == "2":
            from src import services

            logger.info("Выбран поиск транзакций с номерами мобильных телефонов")
            print("Выбран поиск транзакций с номерами мобильных телефонов")
            while True:
                user_input = input("Введите начальную дату в формате ДД.ММ.ГГГГ: ")
                try:
                    date_start = dt.datetime.strptime(user_input, "%d.%m.%Y")
                    logger.info(f"Введена начальная дата: {date_start}")
                    break
                except Exception:
                    print("Дата введена некорректно! Повторите ввод: ")
                    logger.info("Пользователь ввёл некорректную дату")
            while True:
                user_input = input("Введите конечную дату в формате ДД.ММ.ГГГГ: ")
                try:
                    date_stop = dt.datetime.strptime(user_input, "%d.%m.%Y")
                    logger.info(f"Введена конечная дата: {date_stop}")
                    break
                except Exception:
                    print("Дата введена некорректно! Повторите ввод: ")
                    logger.info("Пользователь ввёл некорректную дату")
            if date_stop < date_start:
                print("Даты введены некорректно! Дата окончания периода раньше даты начала.")
                logger.info("Даты введены некорректно! Дата окончания периода раньше даты начала.")
            else:
                print(services.get_transactions_mobile(date_start, date_stop))
            break

        elif user_function == "3":

            logger.info("Выбран отчёт о средних тратах по дням недели за три месяца")
            print("Выбран отчёт о средних тратах по дням недели за три месяца")
            while True:
                user_input = input(
                    "Введите дату окончания анализируемого периода в формате ДД.ММ.ГГГГ, "
                    "либо нажмите <Enter> для выбора последней даты: "
                )
                if user_input == "":
                    user_input = None
                    logger.info("Пользователь не ввёл дату. Выбрана дата последней транзакции.")
                    break
                else:
                    try:
                        user_date = dt.datetime.strptime(user_input, "%d.%m.%Y")
                        logger.info(f"Введена дата окончания анализируемого периода: {user_date}")
                        break
                    except Exception:
                        print("Дата введена некорректно! Повторите ввод: ")
                        logger.info("Пользователь ввёл некорректную дату")
            from src import reports

            reports.spending_by_weekday(utils.import_xlsx_transactions(SOURCE_FILE), user_input)
            break

        elif user_function == "0":
            logger.info("Выбрано завершение работы программы")
            print("Выбрано завершение работы программы")
            exit("Программа завершила работу")

        else:
            logger.error("Введено некорректное значение")
            print("Некорректный выбор. Повторите ввод")


if __name__ == "__main__":
    main_function()
