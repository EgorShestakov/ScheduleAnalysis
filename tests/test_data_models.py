"""Тесты для модуля data_models.py.

Проверяет корректность создания классов-моделей данных:
- Group (учебная группа)
- Room (аудитория)
- Teacher (преподаватель)
- Event (учебное событие)
- TimeSlot (временной слот)
- WorkDay (рабочий день)
"""

import pytest
from src.data_models import Group, Room, Teacher, Event, TimeSlot, WorkDay


class TestGroup:
    """Тесты для класса Group."""

    def test_group_creation(self):
        """Проверяет, что объект Group создаётся с корректными атрибутами."""
        pass

    def test_group_attributes_types(self):
        """Проверяет типы атрибутов Group (int, str, и т.д.)."""
        pass


class TestRoom:
    """Тесты для класса Room."""

    def test_room_creation(self):
        """Проверяет, что объект Room создаётся с корректными атрибутами."""
        pass

    def test_room_capacity_positive(self):
        """Проверяет, что вместимость аудитории — положительное число."""
        pass


class TestTeacher:
    """Тесты для класса Teacher."""

    def test_teacher_creation(self):
        """Проверяет, что объект Teacher создаётся с корректными атрибутами."""
        pass

    def test_teacher_department_optional(self):
        """Проверяет, что поле department может быть None."""
        pass


class TestEvent:
    """Тесты для класса Event."""

    def test_event_creation(self):
        """Проверяет, что объект Event создаётся с корректными атрибутами."""
        pass

    def test_event_total_hours_positive(self):
        """Проверяет, что total_hours — положительное целое число."""
        pass


class TestTimeSlot:
    """Тесты для класса TimeSlot."""

    def test_timeslot_creation(self):
        """Проверяет, что объект TimeSlot создаётся с корректными атрибутами."""
        pass

    def test_timeslot_time_format(self):
        """Проверяет, что время начала и окончания — корректные строки."""
        pass


class TestWorkDay:
    """Тесты для класса WorkDay."""

    def test_workday_creation(self):
        """Проверяет, что объект WorkDay создаётся с корректными атрибутами."""
        pass

    def test_workday_available_slots_list(self):
        """Проверяет, что available_slots — это список TimeSlot."""
        pass
