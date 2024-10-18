import json
import logging
import os
from datetime import datetime

import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/services.log")
abs_file_path = os.path.abspath(rel_file_path)

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def transaction_analysis(data: pd.DataFrame, year: int, month: int) -> str | None:
    """Функция принимает: data - данные с транзакциями;
                       year — год, за который проводится анализ;
                       month — месяц, за который проводится анализ.
    Возвращает: JSON с анализом, сколько на каждой категории можно
                заработать кешбэка в указанном месяце года."""
    try:
        transactions = data.to_dict(orient="records")
        cashback_analysis: dict = {}
        for transaction in transactions:
            transaction_date = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if transaction_date.year == year and transaction_date.month == month:
                category = transaction["Категория"]
                amount = transaction["Сумма платежа"]
                if amount < 0:
                    cashback = transaction["Кэшбэк"]
                    if cashback is not None and cashback >= 0:
                        cashback = float(cashback)
                    else:
                        cashback = round(amount * -0.01, 2)
                    if category in cashback_analysis:
                        cashback_analysis[category] += cashback
                    else:
                        cashback_analysis[category] = cashback
                else:
                    continue
        logger.info("Посчитана сумма кэшбэка по категориям")
        return json.dumps(cashback_analysis, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Произошла ошибка {e}")
        print(f"Произошла ошибка {e}")
        return None
