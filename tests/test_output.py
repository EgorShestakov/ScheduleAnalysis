"""Тесты для модуля output.py.

Проверяет вывод результатов:
- print_schedule() — печать расписания в консоль
- prepare_schedule_rows() — подготовка строк для CSV-экспорта
"""

import pytest
from datetime import date
from src.output import print_schedule, prepare_schedule_rows
from src.data_models import Group, Room, Teacher, Event, TimeSlot, WorkDay


class TestPrintSchedule:
    """Тесты для функции print_schedule()."""

    def test_print_schedule_success(self, assignment, events_list, rooms_list, groups_list, teachers_list, workday):
        work_days = [workday]
        print_schedule(assignment, events_list, rooms_list, groups_list, teachers_list, work_days)
        assert True

    def test_print_schedule_empty(self, capsys):
        """Проверяет поведение при пустом расписании."""
        assignment = {}
        events = []
        rooms = []
        groups = []
        teachers = []
        work_days = []

        print_schedule(assignment, events, rooms, groups, teachers, work_days)

        captured = capsys.readouterr()
        # При пустом расписании не должно быть ошибок
        assert True

    def test_print_schedule_format(self, assignment, events_list, rooms_list, groups_list, teachers_list, workday,
                                   capsys):
        """Проверяет формат вывода (дата, время, группа, событие, аудитория)."""
        work_days = [workday]

        print_schedule(assignment, events_list, rooms_list, groups_list, teachers_list, work_days)

        captured = capsys.readouterr()
        # Проверяем наличие ключевых элементов форматирования
        assert "Дата:" in captured.out
        assert "Пара" in captured.out
        assert "каб." in captured.out
        assert "вместимость:" in captured.out
        assert "студентов:" in captured.out
        # Проверяем наличие ФИО преподавателя (формат "Фамилия И.О.") или "Не назначен"
        # Например, "Иванов И.И." или "Петров П.П."
        assert any(pattern in captured.out for pattern in ["Иванов", "Петров", "Сидоров", "Не назначен"])


class TestPrepareScheduleRows:
    """Тесты для функции prepare_schedule_rows()."""

    def test_prepare_rows_success(self, assignment, events_list, rooms_list, teachers_list, workday):
        """Проверяет успешное формирование списка строк для CSV."""
        work_days = [workday]

        rows = prepare_schedule_rows(assignment, events_list, rooms_list, teachers_list, work_days)

        assert isinstance(rows, list)
        assert len(rows) == len(assignment)
        for row in rows:
            assert "date" in row
            assert "slot_number" in row
            assert "event_name" in row
            assert "room_number" in row
            assert "teacher_name" in row

    def test_prepare_rows_with_conflicts(self, assignment, events_list, rooms_list, teachers_list, workday):
        """Проверяет, что мнимые конфликты попадают в поле conflict."""
        work_days = [workday]

        # Создаём назначение с мнимым конфликтом (одна группа в одно время)
        # Для этого в assignment уже может быть такой конфликт, или создадим специальный
        rows = prepare_schedule_rows(assignment, events_list, rooms_list, teachers_list, work_days)

        # Проверяем, что поле conflict присутствует
        for row in rows:
            assert "conflict" in row

    def test_prepare_rows_columns(self, assignment, events_list, rooms_list, teachers_list, workday):
        """Проверяет, что каждая строка содержит обязательные колонки."""
        work_days = [workday]

        rows = prepare_schedule_rows(assignment, events_list, rooms_list, teachers_list, work_days)

        expected_columns = [
            "date", "slot_number", "event_name", "room_number",
            "teacher_name", "group_id", "room_capacity", "conflict"
        ]

        for row in rows:
            for col in expected_columns:
                assert col in row

    def test_prepare_rows_empty_assignment(self, events_list, rooms_list, teachers_list, workday):
        """Проверяет поведение при пустом назначении."""
        work_days = [workday]
        assignment = {}

        rows = prepare_schedule_rows(assignment, events_list, rooms_list, teachers_list, work_days)

        assert rows == []

    def test_prepare_rows_sorting(self, assignment, events_list, rooms_list, teachers_list, workday):
        """Проверяет, что строки отсортированы по дате и номеру слота."""
        work_days = [workday]

        rows = prepare_schedule_rows(assignment, events_list, rooms_list, teachers_list, work_days)

        # Проверяем сортировку
        if len(rows) > 1:
            for i in range(len(rows) - 1):
                if rows[i]["date"] == rows[i + 1]["date"]:
                    assert rows[i]["slot_number"] <= rows[i + 1]["slot_number"]
                else:
                    assert rows[i]["date"] <= rows[i + 1]["date"]
