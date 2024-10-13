import json
import unittest
from unittest.mock import Mock, patch


import pytest

from src.views import response_json


def test_response_json() -> None:
    # Подготовка тестовых данных
    date = "2023-05-15 12:34:56"

    # Создание моков
    mock_read_data_from_excel = Mock(return_value=[{"amount": 100, "category": "Food"}])
    mock_greeting = Mock(return_value="Добрый день")
    mock_card_information = Mock(return_value={"card1": "Info1", "card2": "Info2"})
    mock_top_transactions = Mock(return_value=[{"amount": 50, "category": "Transport"}])
    mock_get_currency_rates = Mock(return_value={"USD": 1.0, "EUR": 0.85})
    mock_get_price_stocks = Mock(return_value={"AAPL": 150.00, "GOOGL": 3000.00})

    # Замена реальных функций моками
    with patch('src.views.read_data_from_excel', mock_read_data_from_excel):
        with patch('src.views.greeting', mock_greeting):
            with patch('src.views.card_information', mock_card_information):
                with patch('src.views.top_transactions', mock_top_transactions):
                    with patch('src.views.get_currency_rates', mock_get_currency_rates):
                        with patch('src.views.get_price_stocks', mock_get_price_stocks):
                            # Вызов тестируемой функции
                            result = response_json(date)

    # Проверка результата
    expected_result = {
        "greeting": "Добрый день",
        "cards": {"card1": "Info1", "card2": "Info2"},
        "top_transactions": [{"amount": 50, "category": "Transport"}],
        "exchange_rates": {"USD": 1.0, "EUR": 0.85},
        "stocks": {"AAPL": 150.00, "GOOGL": 3000.00}
    }

    assert isinstance(result, str)
    assert json.loads(result) == expected_result


def test_response_json_invalid_date_format():
    invalid_date = "invalid-date"
    with unittest.mock.patch('src.views.response_json') as mock_func:
        mock_func.side_effect = ValueError("Invalid date format")

        with pytest.raises(ValueError):
            response_json(invalid_date)