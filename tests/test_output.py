"""Тесты для модуля output.py.

Проверяет вывод результатов:
- print_schedule() — печать расписания в консоль
- prepare_schedule_rows() — подготовка строк для CSV-экспорта
"""

import pytest
from src.output import print_schedule, prepare_schedule_rows


class TestPrintSchedule:
    """Тесты для функции print_schedule()."""

    def test_print_schedule_success(self):
        """Проверяет успешную печать расписания в консоль."""
        pass

    def test_print_schedule_empty(self):
        """Проверяет поведение при пустом расписании."""
        pass

    def test_print_schedule_format(self):
        """Проверяет формат вывода (дата, время, группа, событие, аудитория)."""
        pass


class TestPrepareScheduleRows:
    """Тесты для функции prepare_schedule_rows()."""

    def test_prepare_rows_success(self):
        """Проверяет успешное формирование списка строк для CSV."""
        pass

    def test_prepare_rows_with_conflicts(self):
        """Проверяет, что мнимые конфликты попадают в поле conflict."""
        pass

    def test_prepare_rows_columns(self):
        """Проверяет, что каждая строка содержит обязательные колонки."""
        pass
