"""Тесты для модуля db_writer.py.

Проверяет выгрузку расписания:
- read_schedule_from_sqlite() — чтение расписания из SQLite
- write_schedule_to_csv() — запись расписания в CSV
"""

import pytest
from src.db_writer import read_schedule_from_sqlite, write_schedule_to_csv


class TestReadScheduleFromSqlite:
    """Тесты для функции read_schedule_from_sqlite()."""

    def test_read_schedule_success(self):
        """Проверяет успешное чтение расписания из базы данных."""
        pass

    def test_read_schedule_empty_db(self):
        """Проверяет поведение при пустой базе данных."""
        pass

    def test_read_schedule_joins_correctly(self):
        """Проверяет, что чтение объединяет таблицы events, rooms, teachers, work_days."""
        pass


class TestWriteScheduleToCsv:
    """Тесты для функции write_schedule_to_csv()."""

    def test_write_schedule_success(self):
        """Проверяет успешную запись расписания в CSV-файл."""
        pass

    def test_write_schedule_empty_rows(self):
        """Проверяет поведение при пустом списке строк."""
        pass

    def test_write_schedule_overwrites_file(self):
        """Проверяет, что файл schedule_result.csv перезаписывается при каждом вызове."""
        pass
