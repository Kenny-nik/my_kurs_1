import json

import pandas as pd

from src.services import transaction_analysis


def test_transaction_analysis() -> None:
    # Подготовка тестовых данных
    test_data = {
        "Дата операции": ["01.01.2024 10:00:00", "02.01.2024 11:30:00"],
        "Категория": ["Продукты", "Транспорт"],
        "Сумма платежа": [-100, -200],
        "Кэшбэк": [10, None],
    }

    df = pd.DataFrame(test_data)

    result = transaction_analysis(df, 2024, 1)

    assert json.loads(result) == {"Продукты": 10.0, "Транспорт": 2.0}


def test_transaction_analysis_error() -> None:
    # Подготовка тестовых данных
    test_data = {
        "Дата операции": ["01.01.2024 10:00:00", "02.01.2024 11:30:00"],
        "Сумма платежа": [-100, -200],
        "Кэшбек": [None, None],
    }

    df = pd.DataFrame(test_data)
    result = transaction_analysis(df, 2024, 1)
    assert result is None


def test_transaction_analysis_2() -> None:
    # Подготовка тестовых данных
    test_data = {
        "Дата операции": ["01.01.2024 10:00:00", "02.01.2024 11:30:00"],
        "Категория": ["Продукты", "Транспорт"],
        "Сумма платежа": [100, 200],
        "Кэшбэк": [None, None],
    }

    df = pd.DataFrame(test_data)
    result = transaction_analysis(df, 2024, 1)
    assert result == "{}"


def test_transaction_analysis_3(test_empty_df: pd.DataFrame) -> None:

    result = transaction_analysis(test_empty_df, 2022, 1)
    assert result == "{}"