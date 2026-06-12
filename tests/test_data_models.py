"""Тесты для модуля data_models.py.

Проверяет корректность создания классов-моделей данных:
- Group (учебная группа)
- Room (аудитория)
- Teacher (преподаватель)
- Event (учебное событие)
- TimeSlot (временной слот)
- WorkDay (рабочий день)

Также проверяются вспомогательные методы (full_name, __repr__).
"""

import pytest
from datetime import date
from src.data_models import Group, Room, Teacher, Event, TimeSlot, WorkDay


class TestGroup:
    """Тесты для класса Group."""

    def test_group_creation(self, group):
        """Проверяет, что объект Group создаётся с корректными атрибутами."""
        assert group.id == 1
        assert group.course == 1
        assert group.department == "ИАИТ"
        assert group.number == 110
        assert group.size == 31

    def test_group_attributes_types(self, group):
        """Проверяет типы атрибутов Group."""
        assert isinstance(group.id, int)
        assert isinstance(group.course, int)
        assert isinstance(group.department, str)
        assert isinstance(group.number, int)
        assert isinstance(group.size, int)

    def test_group_repr(self, group):
        """Проверяет работу метода __repr__."""
        repr_str = repr(group)
        assert "1" in repr_str
        assert "ИАИТ" in repr_str
        assert "110" in repr_str


class TestRoom:
    """Тесты для класса Room."""

    def test_room_creation(self, room):
        """Проверяет, что объект Room создаётся с корректными атрибутами."""
        assert room.id == 1
        assert room.number == 402
        assert room.capacity == 40
        assert room.equipment == ["доска", "компьютеры"]
        assert len(room.equipment) == 2

    def test_room_empty_equipment(self, room_without_equipment):
        """Проверяет создание аудитории без оборудования."""
        assert room_without_equipment.equipment == []

    def test_room_repr(self, room):
        """Проверяет работу метода __repr__."""
        repr_str = repr(room)
        assert "Room" in repr_str
        assert "id=1" in repr_str
        assert "number=402" in repr_str
        assert "capacity=40" in repr_str
        assert "доска" in repr_str


class TestTeacher:
    """Тесты для класса Teacher."""

    def test_teacher_creation(self, teacher):
        """Проверяет, что объект Teacher создаётся с корректными атрибутами."""
        assert teacher.id == 1
        assert teacher.surname == "Иванов"
        assert teacher.name == "Иван"
        assert teacher.patronymic == "Иванович"
        assert teacher.specialization == ["Матанализ"]
        assert teacher.department == "ПМиИ"

    def test_teacher_full_name(self, teacher, teacher_no_patron, teacher_no_name):
        """Проверяет метод full_name() для разных вариантов ФИО."""
        # Полное ФИО
        assert teacher.full_name() == "Иванов И.И."

        # Без отчества
        assert teacher_no_patron.full_name() == "Петров П."

        # Без имени и отчества (граничный случай)
        assert teacher_no_name.full_name() == "Сидоров"

    def test_teacher_repr(self, teacher):
        """Проверяет работу метода __repr__."""
        repr_str = repr(teacher)
        assert "Teacher" in repr_str
        assert "id=1" in repr_str
        assert "full_name='Иванов И.И.'" in repr_str
        assert "specialization=['Матанализ']" in repr_str
        assert "department='ПМиИ'" in repr_str


class TestEvent:
    """Тесты для класса Event."""

    def test_event_creation(self, event):
        """Проверяет, что объект Event создаётся с корректными атрибутами."""
        assert event.id == 1
        assert event.name == "Матанализ"
        assert event.group_id == 1
        assert event.teacher_id == 1
        assert event.total_hours == 4
        assert event.required_features == ["доска"]

    def test_event_empty_required_features(self, event_empty_features):
        """Проверяет создание события без требований к оборудованию."""
        assert event_empty_features.required_features == []

    def test_event_total_hours_zero(self, event_zero_hours):
        """Проверяет создание события с нулевым количеством часов."""
        assert event_zero_hours.total_hours == 0

    def test_event_repr(self, event):
        """Проверяет работу метода __repr__."""
        repr_str = repr(event)
        assert "Event" in repr_str
        assert "id=1" in repr_str
        assert "name='Матанализ'" in repr_str
        assert "group_id=1" in repr_str
        assert "teacher_id=1" in repr_str
        assert "total_hours=4" in repr_str
        assert "required_features=['доска']" in repr_str

    def test_event_total_hours_type(self, event):
        """Проверяет, что total_hours — целое неотрицательное число."""
        assert isinstance(event.total_hours, int)
        assert event.total_hours >= 0


class TestTimeSlot:
    """Тесты для класса TimeSlot."""

    def test_timeslot_creation(self, slot1):
        """Проверяет, что объект TimeSlot создаётся с корректными атрибутами."""
        assert slot1.id == 1
        assert slot1.number == 1
        assert slot1.start_time == "09:00"
        assert slot1.end_time == "10:30"

    def test_timeslot_time_format(self, slot1):
        """Проверяет, что время хранится в строковом формате."""
        assert isinstance(slot1.start_time, str)
        assert isinstance(slot1.end_time, str)
        assert ":" in slot1.start_time
        assert ":" in slot1.end_time

    def test_timeslot_repr(self, slot1):
        """Проверяет работу метода __repr__."""
        repr_str = repr(slot1)
        assert "TimeSlot" in repr_str
        assert "id=1" in repr_str
        assert "number=1" in repr_str
        assert "start_time='09:00'" in repr_str
        assert "end_time='10:30'" in repr_str


class TestWorkDay:
    """Тесты для класса WorkDay."""

    def test_workday_creation(self, workday):
        """Проверяет, что объект WorkDay создаётся с корректными атрибутами."""
        assert workday.date == date(2026, 3, 27)
        assert workday.is_holiday is False
        assert workday.day_type == "четная"
        assert len(workday.available_slots) == 2
        assert workday.available_slots[0].number == 1
        assert workday.available_slots[1].number == 2

    def test_workday_empty_slots(self, workday_holiday):
        """Проверяет создание рабочего дня без доступных слотов."""
        assert workday_holiday.available_slots == []

    def test_workday_day_type_values(self):
        """Проверяет, что day_type может принимать разные значения."""
        for day_type in ["четная", "нечетная", "обычный", "праздник"]:
            wd = WorkDay(
                date=date(2026, 3, 27),
                is_holiday=False,
                day_type=day_type,
                available_slots=[]
            )
            assert wd.day_type == day_type

    def test_workday_repr(self, workday):
        """Проверяет работу метода __repr__."""
        repr_str = repr(workday)
        assert "WorkDay" in repr_str
        assert "2026-03-27" in repr_str
        assert "is_holiday=False" in repr_str
        assert "day_type='четная'" in repr_str
        assert "available_slots_count=2" in repr_str

    def test_workday_available_slots_is_list_of_timeslots(self, workday):
        """Проверяет, что available_slots — это список объектов TimeSlot."""
        assert isinstance(workday.available_slots, list)
        assert all(isinstance(slot, TimeSlot) for slot in workday.available_slots)

    def test_workday_available_slots_empty(self, workday_holiday):
        """Проверяет, что available_slots может быть пустым списком."""
        assert workday_holiday.available_slots == []