from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from src.utils import (card_information, get_currency_rates, get_price_stocks, greeting, read_data_from_excel,
                       top_transactions)


def test_read_data_from_excel_success(sample_excel_file: str) -> None:
    with patch(
        "pandas.read_excel",
        return_value=pd.DataFrame({"Дата": ["01.01.2024"], "Тип транзакции": ["Расход"], "Сумма": [-100]}),
    ):
        result = read_data_from_excel(sample_excel_file)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["Дата"].iloc[0] == "01.01.2024"
        assert result["Тип транзакции"].iloc[0] == "Расход"
        assert result["Сумма"].iloc[0] == -100


def test_read_data_from_excel_empty_file(mock_logger: MagicMock, sample_excel_file: str) -> None:
    with patch("pandas.read_excel", side_effect=pd.errors.EmptyDataError("File is empty")):
        result = read_data_from_excel(sample_excel_file)
        assert result is None
        mock_logger.error.assert_called_once_with("Произошла ошибка: File is empty")


def test_read_data_from_excel_not_found(mock_logger, sample_excel_file):
    with patch('pandas.read_excel', side_effect=FileNotFoundError("File not found")):
        result = read_data_from_excel(sample_excel_file)
        assert result is None
        mock_logger.warning.assert_called_once_with("Файл не найден")


def test_read_data_from_excel_invalid_path(mock_logger: MagicMock) -> None:
    invalid_path = "/invalid/path/to/file.xlsx"
    result = read_data_from_excel(invalid_path)
    assert result is None


@pytest.mark.parametrize(
    "date, result",
    [
        ("2021-12-27 16:44:00", "Добрый день"),
        ("2021-12-31 10:42:40", "Доброе утро"),
        ("2021-12-20 02:34:14", "Доброй ночи"),
        ("2021-12-21 21:01:32", "Добрый вечер"),
    ],
)
def test_greeting(date: str, result: str) -> None:
    assert greeting(date) == result


def test_card_information_data_empty(test_empty_df: pd.DataFrame) -> None:
    assert card_information(test_empty_df) == []


def test_get_cards_data_single_transaction(test_df: pd.DataFrame) -> None:
    expected_result = [
        {"last_digits": "1234", "total_spent": 300.0, "cashback": 3.0},
        {"last_digits": "5678", "total_spent": 50.0, "cashback": 0.5},
    ]
    assert card_information(test_df) == expected_result


def test_get_cards_data_nan_card_number(test_df_nan: pd.DataFrame) -> None:
    expected_result = [
        {"last_digits": "1234", "total_spent": 100.0, "cashback": 1.0},
        {"last_digits": "5678", "total_spent": 50.0, "cashback": 0.5},
    ]
    assert card_information(test_df_nan) == expected_result


def test_get_cards_data_cashback(test_df_not_cashback: pd.DataFrame) -> None:
    expected_result = [
        {"last_digits": "1234", "total_spent": 100.0, "cashback": 1.0},
        {"last_digits": "5678", "total_spent": 50.0, "cashback": 0.5},
    ]
    assert card_information(test_df_not_cashback) == expected_result


def test_top_transactions_empty(test_empty_df: pd.DataFrame) -> None:
    assert top_transactions(test_empty_df) == []


def test_top_transactions(test_df_top_5: pd.DataFrame) -> None:
    expected_result = [
        {"amount": -400.0, "category": "Магазины", "date": "25.06.2023 12:00:00", "description": "Покупка техники"},
        {"amount": -300.0, "category": "Магазины", "date": "23.06.2023 12:00:00", "description": "Покупка одежды"},
        {"amount": -200.0, "category": "Транспорт", "date": "21.06.2023 12:00:00", "description": "Оплата проезда"},
        {"amount": -100.0, "category": "Еда", "date": "20.06.2023 12:00:00", "description": "Покупка еды"},
        {"amount": -50.0, "category": "Развлечения", "date": "22.06.2023 12:00:00", "description": "Кино"},
    ]
    assert top_transactions(test_df_top_5) == expected_result


@patch("src.utils.requests.get")
def test_get_currency_rates(mock_get: MagicMock) -> None:
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "success": True,
        "query": {"from": "USD", "to": "RUB", "amount": "1"},
        "info": {"timestamp": 1726849624, "rate": 92.349211},
        "date": "2024-09-20",
        "result": 92.349211,
    }
    result = get_currency_rates(["USD", "EUR"], api_key="abc")
    assert result == [{"currency": "USD", "rate": 92.349211}, {"currency": "EUR", "rate": 92.349211}]


@patch("src.utils.requests.get")
def test_get_currency_rates_invalid_api(mock_get: MagicMock) -> None:
    mock_get.return_value.status_code = 401
    mock_get.return_value.json.return_value = {"message": "Invalid authentication credentials"}
    result = get_currency_rates(["USD"], api_key="abc")
    assert result == [{"currency": "USD", "rate": None}]


@patch("src.utils.requests.get")
def test_get_price_stocks(mock_get: MagicMock) -> None:
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"symbol": "AAPL", "name": "Apple Inc.", "price": 145.775}]
    result = get_price_stocks(["AAPL"], api_key="abc")
    assert result == [{"stock": "AAPL", "price": 145.775}]


@patch("src.utils.requests.get")
def test_get_price_stocks_invalid_api(mock_get: MagicMock) -> None:
    mock_get.return_value.status_code = 401
    mock_get.return_value.json.return_value = {
        "Error Message": "Invalid API KEY. Feel free to create a Free API Key or visit "
        "https://site.financialmodelingprep.com/faqs?search=why-is-my-api-key-invalid for more information."
    }
    result = get_price_stocks(["AAPL"], api_key="abc")
    assert result == [{"stock": "AAPL", "price": None}]