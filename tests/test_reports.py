import pandas as pd
import pytest

from src.reports import report_to_file, spending_by_category


def test_spending_by_category(transactions_df: pd.DataFrame) -> None:
    result = spending_by_category(transactions_df, "Продукты", "03.05.2024")
    assert result == (
        "[\n"
        "    {\n"
        '        "Категория":"Продукты",\n'
        '        "Сумма":100\n'
        "    },\n"
        "    {\n"
        '        "Категория":"Продукты",\n'
        '        "Сумма":200\n'
        "    }\n"
        "]"
    )
    empty_result = spending_by_category(transactions_df, "Нет категории")
    assert empty_result == "[\n\n]"
    incorrect_date = spending_by_category(transactions_df, "Продукты", "31.04.2024")
    assert incorrect_date == ""


def test_decorator() -> None:

    @report_to_file("test_report.txt")
    def report() -> str:
        return "Тест выполнен успешно"

    report()

    with open("test_report.txt", "r", encoding="utf-8") as file:
        report_content = file.read()

        assert "Тест выполнен успешно" in report_content

    @report_to_file()
    def report_exception() -> None:
        raise ValueError("Test error")

    with pytest.raises(Exception):
        report_exception()

    with open("test_report.txt", "r", encoding="utf-8") as file:
        report_content = file.read()

    assert "Тест выполнен успешно" in report_content, f"Ожидаемое содержимое файла: 'Тест выполнен успешно', но получено: {report_content}"
