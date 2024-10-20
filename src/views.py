import json
import logging
import os
from typing import Any

from dotenv import load_dotenv

from src.utils import (card_information, get_currency_rates, get_price_stocks, greeting, read_data_from_excel,
                       top_transactions, filter_by_date)

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/views.log")
abs_file_path = os.path.abspath(rel_file_path)

path_to_user_settings = os.path.join(current_dir, "../user_settings.json")
abs_path_to_user_settings = os.path.abspath(path_to_user_settings)

logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


with open(abs_path_to_user_settings, "r") as file:
    logger.info(f"Чтение файла {file}")
    user_choice = json.load(file)

PATH_TO_FILE = os.path.join("", "../.env")
load_dotenv(PATH_TO_FILE)

API_KEY_CURRENCY = os.getenv("API_KEY_CURRENCY")
API_KEY_STOCKS = os.getenv("API_KEY_STOCKS")
PATH_TO_EXCEL = os.path.join(os.path.dirname(__file__), "", "../data", "operations.xlsx")


def response_json(date: str) -> Any:
    """Основная функция принимающая на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ"""
    transactions = read_data_from_excel(PATH_TO_EXCEL)
    ranged_transactions = filter_by_date(transactions, date)
    greetings = greeting()
    cards = card_information(ranged_transactions)
    top_5 = top_transactions(ranged_transactions)
    currency_rates = get_currency_rates(user_choice["user_currencies"], API_KEY_CURRENCY)
    price_stocks = get_price_stocks(user_choice["user_stocks"], API_KEY_STOCKS)
    user_data = {
        "greeting": greetings,
        "cards": cards,
        "top_transactions": top_5,
        "exchange_rates": currency_rates,
        "stocks": price_stocks,
    }
    logger.info("Формирование JSON-ответа")
    return json.dumps(user_data, ensure_ascii=False, indent=4)

