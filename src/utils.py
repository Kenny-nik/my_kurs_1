import logging
import os
from datetime import datetime, timedelta
from typing import Any, List, Dict

import pandas as pd
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/utils.log")
abs_file_path = os.path.abspath(rel_file_path)

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def read_data_from_excel(path: str) -> pd.DataFrame:
    """Функция принимает на вход путь до excel-файла
    и возвращает датафрейм с банковскими операциями."""
    try:
        transactions_df = pd.read_excel(path)
        logger.info(f"Чтение данных из файла: {path}")
        operations = transactions_df.to_dict(orient="records")
        return operations
    except pd.errors.EmptyDataError as e:
        logger.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")
    except FileNotFoundError:
        logger.warning("Файл не найден")
        print("Файл не найден")


def greeting() -> str:
    """Приветствие в формате "???", где ??? — «Доброе утро» /
    «Добрый день» / «Добрый вечер» / «Доброй ночи» в зависимости от текущего времени."""
    now = datetime.now()
    current_hour = now.hour
    if 0 <= current_hour < 6:
        logger.info("Приветствие: 'Доброй ночи'")
        return "Доброй ночи"
    elif 6 <= current_hour < 12:
        logger.info("Приветствие: 'Доброе утро'")
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        logger.info("Приветствие: 'Добрый день'")
        return "Добрый день"
    elif 18 <= current_hour < 24:
        logger.info("Приветствие: 'Добрый вечер'")
        return "Добрый вечер"


# def card_information(operations: pd.DataFrame) -> list[dict]:
#     """Функция принимает на вход DataFrame c финансовыми операциями и
#     выводит информацию по каждой карте:
#     последние 4 цифры карты;
#     общая сумма расходов;
#     кешбэк (1 рубль на каждые 100 рублей)."""
#     logger.info("Преобразование DataFrame в список словарей")
#     transactions = operations.to_dict(orient="records")
#     card_info = {}
#     logger.info("Сортировка по номерам карт,подсчет суммы платежей и кэшбэка")
#     for transaction in transactions:
#         card_number = transaction.get("Номер карты")
#         # если поле номер карты None, операцию пропускаем
#         if not card_number or str(card_number).strip().lower() == "nan":
#             continue
#         amount = float(transaction["Сумма операции"])
#         if card_number not in card_info:
#             card_info[card_number] = {"total_spent": 0.0, "cashback": 0.0}
#         if amount < 0:
#             card_info[card_number]["total_spent"] += abs(amount)
#             cashback_value = transaction.get("Кэшбэк")
#             # убираем категории переводы и наличные т.к. с них кэшбэка не будет
#             if transaction["Категория"] != "Переводы" and transaction["Категория"] != "Наличные":
#                 # рассчитываем кэшбек как 1% от траты, но если поле кэшбек содержит сумму просто ее добавляем
#                 if cashback_value is not None:
#                     cashback_amount = float(cashback_value)
#                     if cashback_amount >= 0:
#                         card_info[card_number]["cashback"] += cashback_amount
#                     else:
#                         card_info[card_number]["cashback"] += amount * -0.01
#                 else:
#                     card_info[card_number]["cashback"] += amount * -0.01
#     cards_data = []
#     for last_digits, data in card_info.items():
#         cards_data.append(
#             {
#                 "last_digits": last_digits,
#                 "total_spent": round(data["total_spent"], 2),
#                 "cashback": round(data["cashback"], 2),
#             }
#         )
#     logger.info("получен словарь по тратам и кэшбэку по каждой карте")
#     return cards_data


def card_information(operations: List[Dict]) -> List[Dict]:
    """Функция создает словарь с ключами номеров карт и в значения добавляет сумму трат и сумму кэшбека"""
    card_data = {}
    for operation in operations:
        card_number = operation.get("Номер карты")
            # если поле номер карты пустое, операцию пропускаем, т.к. не понятно к какой карте привязать трату
        if not card_number or str(card_number).strip().lower() == "nan":
            continue

        amount = float(operation["Сумма операции"])
        if card_number not in card_data:
            card_data[card_number] = {"total_spent": 0.0, "cashback": 0.0}

        if amount < 0:
            card_data[card_number]["total_spent"] += abs(amount)
            cashback_value = operation.get("Кэшбэк")

            # убираем категории переводы и наличные т.к. с них кэшбека не будет
            if operation["Категория"] != "Переводы" and operation["Категория"] != "Наличные":
                # рассчитываем кэшбек как 1% от траты, но если поле кешбек содержит сумму просто ее добавляем
                if cashback_value is not None:
                    cashback_amount = float(cashback_value)
                    if cashback_amount >= 0:
                        card_data[card_number]["cashback"] += cashback_amount
                    else:
                        card_data[card_number]["cashback"] += amount * -0.01
                else:
                    card_data[card_number]["cashback"] += amount * -0.01
    logger.info("кэшбек и суммы по картам посчитаны")
    cards_data = []
    for last_digits, data in card_data.items():
        cards_data.append(
            {
                "last_digits": last_digits,
                "total_spent": round(data["total_spent"], 2),
                "cashback": round(data["cashback"], 2),
            }
        )
    logger.info("получен словарь по тратам и кешбеку по каждой карте")
    return cards_data

def top_transactions(transactions_df: pd.DataFrame) -> list[dict[str, Any | None]]:
    """Функция принимает на вход датафрейм с транзакциями, сортирует и выводит топ-5 транзакций по сумме платежа"""
    try:
        logger.info("Сортировка транзакций по сумме платежа")
        transactions_df = transactions_df.sort_values(by="Сумма платежа", ascending=False, key=lambda x: abs(x))
        # Выбор топ-5 транзакций
        top_5_transactions = transactions_df.head(5).to_dict("records")
        # Преобразование результатов в список словарей
        result = []
        for transaction in top_5_transactions:
            operation = {
                "date": transaction.get("Дата операции"),
                "amount": transaction.get("Сумма платежа"),
                "category": transaction.get("Категория"),
                "description": transaction.get("Описание"),
            }
            result.append(operation)
        logger.info("Выполнение сортировки транзакций по сумме платежа завершено")

        return result
    except Exception as e:
        logger.error(f"Произошла ошибка {e}")
        return []


def get_currency_rates(currencies: list[str], api_key: Any) -> list[dict]:
    """Функция принимает список с кодами валют,
    а возвращает список словарей с текущими курсами"""
    currency_rates = []
    headers = {"apikey": api_key}

    for currency in currencies:
        currency_code = currency
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency_code}&amount=1"
        logger.info(f"Запрос курса валюты {currency}")
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            logger.info("Успешный запрос")
            result = response.json()
            ruble_cost = result["result"]
            currency_rates.append({"currency": currency, "rate": ruble_cost})
        else:
            logger.warning(f"Ошибка: {response.status_code}, {response.text}")
            print(f"Ошибка: {response.status_code}, {response.text}")
            currency_rates.append({"currency": currency, "rate": None})
    logger.info("Курсы валют созданы")
    return currency_rates


def get_price_stocks(companies: list[str], api_key: Any) -> list[dict]:
    """Функция принимает список с кодами компаний
    и возвращает список словарей со стоимостью акций каждой компании"""
    price_stocks = []
    for company in companies:
        url = f"https://financialmodelingprep.com/api/v3/quote/{company}?apikey={api_key}"
        logger.info(f"Запрос стоимости акций компании {company}")
        response = requests.get(url)
        if response.status_code == 200:
            logger.info("Успешный запрос")
            result = response.json()
            price = result[0]["price"]
            price_stocks.append({"stock": company, "price": price})
        else:
            logger.warning(f"Ошибка: {response.status_code}, {response.text}")
            print(f"Ошибка: {response.status_code}, {response.text}")
            price_stocks.append({"stock": company, "price": None})
    logger.info("Стоимость акций создана")
    return price_stocks


input_date_str = "20.03.2020"

def filter_by_date(operations: List[Dict], input_date_str: str) -> List[Dict]:  # дата дд.мм.гггг
    """Функция принимает список словарей с транзакциями и дату
    фильтрует транзакции с начала месяца, на который выпадает входящая дата по входящую дату."""

    input_date = datetime.strptime(input_date_str, "%d.%m.%Y")
    end_date = input_date + timedelta(days=1)
    start_date = datetime(end_date.year, end_date.month, 1)

    def parse_date(date_str: str) -> datetime:
        """Функция переводит дату из формата строки в формат datetime"""
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")

    filtered_operations = [
        operation for operation in operations if start_date <= parse_date(operation["Дата операции"]) <= end_date
    ]
    logger.info(f"Транзакции в списке отфильтрованы по датам от {start_date} до {end_date}")
    return filtered_operations