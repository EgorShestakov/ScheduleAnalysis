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

    def test_group_creation(self):
        """Проверяет, что объект Group создаётся с корректными атрибутами."""
        group = Group(id=1, course=1, department="ИАИТ", number="110", size=31)
        assert group.id == 1
        assert group.course == 1
        assert group.department == "ИАИТ"
        assert group.number == "110"
        assert group.size == 31

    def test_group_attributes_types(self):
        """Проверяет типы атрибутов Group."""
        group = Group(id=1, course=1, department="ИАИТ", number="110", size=31)
        assert isinstance(group.id, int)
        assert isinstance(group.course, int)
        assert isinstance(group.department, str)
        assert isinstance(group.number, str)
        assert isinstance(group.size, int)

    def test_group_repr(self):
        """Проверяет работу метода __repr__."""
        group = Group(id=1, course=1, department="ИАИТ", number="110", size=31)
        repr_str = repr(group)
        assert "Group" in repr_str
        assert "id=1" in repr_str
        assert "department='ИАИТ'" in repr_str
        assert "number='110'" in repr_str
        assert "size=31" in repr_str


class TestRoom:
    """Тесты для класса Room."""

    def test_room_creation(self):
        """Проверяет, что объект Room создаётся с корректными атрибутами."""
        equipment = ["доска", "компьютеры"]
        room = Room(id=1, number="402", capacity=30, equipment=equipment)
        assert room.id == 1
        assert room.number == "402"
        assert room.capacity == 30
        assert room.equipment == equipment
        assert len(room.equipment) == 2

    def test_room_empty_equipment(self):
        """Проверяет создание аудитории без оборудования."""
        room = Room(id=1, number="402", capacity=30, equipment=[])
        assert room.equipment == []

    def test_room_repr(self):
        """Проверяет работу метода __repr__."""
        equipment = ["доска", "компьютеры"]
        room = Room(id=1, number="402", capacity=30, equipment=equipment)
        repr_str = repr(room)
        assert "Room" in repr_str
        assert "id=1" in repr_str
        assert "number='402'" in repr_str
        assert "capacity=30" in repr_str
        assert "доска" in repr_str


class TestTeacher:
    """Тесты для класса Teacher."""

    def test_teacher_creation(self):
        """Проверяет, что объект Teacher создаётся с корректными атрибутами."""
        specialization = ["Математический анализ", "Численные методы"]
        teacher = Teacher(
            id=1,
            surname="Иванов",
            name="Иван",
            patronymic="Иванович",
            specialization=specialization,
            department="ПМиИ"
        )
        assert teacher.id == 1
        assert teacher.surname == "Иванов"
        assert teacher.name == "Иван"
        assert teacher.patronymic == "Иванович"
        assert teacher.specialization == specialization
        assert teacher.department == "ПМиИ"

    def test_teacher_full_name(self):
        """Проверяет метод full_name() для разных вариантов ФИО."""
        # Полное ФИО
        teacher1 = Teacher(
            id=1, surname="Иванов", name="Иван", patronymic="Иванович",
            specialization=[], department="ПМиИ"
        )
        assert teacher1.full_name() == "Иванов И.И."

        # Без отчества
        teacher2 = Teacher(
            id=2, surname="Петров", name="Петр", patronymic="",
            specialization=[], department="ПМиИ"
        )
        assert teacher2.full_name() == "Петров П."

        # Без имени и отчества (граничный случай)
        teacher3 = Teacher(
            id=3, surname="Сидоров", name="", patronymic="",
            specialization=[], department="ПМиИ"
        )
        assert teacher3.full_name() == "Сидоров"

    def test_teacher_repr(self):
        """Проверяет работу метода __repr__."""
        teacher = Teacher(
            id=1, surname="Иванов", name="Иван", patronymic="Иванович",
            specialization=["Матанализ"], department="ПМиИ"
        )
        repr_str = repr(teacher)
        assert "Teacher" in repr_str
        assert "id=1" in repr_str
        assert "full_name='Иванов И.И.'" in repr_str
        assert "specialization=['Матанализ']" in repr_str
        assert "department='ПМиИ'" in repr_str


class TestEvent:
    """Тесты для класса Event."""

    def test_event_creation(self):
        """Проверяет, что объект Event создаётся с корректными атрибутами."""
        required_features = ["доска", "проектор"]
        event = Event(
            id=1,
            name="Математический анализ",
            group_id=1,
            teacher_id=1,
            total_hours=4,
            required_features=required_features
        )
        assert event.id == 1
        assert event.name == "Математический анализ"
        assert event.group_id == 1
        assert event.teacher_id == 1
        assert event.total_hours == 4
        assert event.required_features == required_features

    def test_event_empty_required_features(self):
        """Проверяет создание события без требований к оборудованию."""
        event = Event(
            id=1, name="Лекция", group_id=1, teacher_id=1,
            total_hours=2, required_features=[]
        )
        assert event.required_features == []

    def test_event_total_hours_zero(self):
        """Проверяет создание события с нулевым количеством часов."""
        event = Event(
            id=1, name="Факультатив", group_id=1, teacher_id=1,
            total_hours=0, required_features=[]
        )
        assert event.total_hours == 0

    def test_event_repr(self):
        """Проверяет работу метода __repr__."""
        event = Event(
            id=1, name="Матанализ", group_id=1, teacher_id=1,
            total_hours=4, required_features=["доска"]
        )
        repr_str = repr(event)
        assert "Event" in repr_str
        assert "id=1" in repr_str
        assert "name='Матанализ'" in repr_str
        assert "group_id=1" in repr_str
        assert "teacher_id=1" in repr_str
        assert "total_hours=4" in repr_str
        assert "required_features=['доска']" in repr_str

    def test_event_total_hours_type(self):
        """Проверяет, что total_hours — целое неотрицательное число."""
        event = Event(
            id=1, name="Лекция", group_id=1, teacher_id=1,
            total_hours=4, required_features=[]
        )
        assert isinstance(event.total_hours, int)
        assert event.total_hours >= 0


class TestTimeSlot:
    """Тесты для класса TimeSlot."""

    def test_timeslot_creation(self):
        """Проверяет, что объект TimeSlot создаётся с корректными атрибутами."""
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        assert slot.id == 1
        assert slot.number == 1
        assert slot.start_time == "09:00"
        assert slot.end_time == "10:30"

    def test_timeslot_time_format(self):
        """Проверяет, что время хранится в строковом формате."""
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        assert isinstance(slot.start_time, str)
        assert isinstance(slot.end_time, str)
        assert ":" in slot.start_time
        assert ":" in slot.end_time

    def test_timeslot_repr(self):
        """Проверяет работу метода __repr__."""
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        repr_str = repr(slot)
        assert "TimeSlot" in repr_str
        assert "id=1" in repr_str
        assert "number=1" in repr_str
        assert "start_time='09:00'" in repr_str
        assert "end_time='10:30'" in repr_str


class TestWorkDay:
    """Тесты для класса WorkDay."""

    def test_workday_creation(self):
        """Проверяет, что объект WorkDay создаётся с корректными атрибутами."""
        slots = [
            TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30"),
            TimeSlot(id=2, number=2, start_time="10:40", end_time="12:10")
        ]
        work_day = WorkDay(
            date=date(2026, 3, 27),
            is_holiday=False,
            day_type="четная",
            available_slots=slots
        )
        assert work_day.date == date(2026, 3, 27)
        assert work_day.is_holiday is False
        assert work_day.day_type == "четная"
        assert len(work_day.available_slots) == 2
        assert work_day.available_slots[0].number == 1
        assert work_day.available_slots[1].number == 2

    def test_workday_empty_slots(self):
        """Проверяет создание рабочего дня без доступных слотов."""
        work_day = WorkDay(
            date=date(2026, 3, 27),
            is_holiday=True,
            day_type="праздник",
            available_slots=[]
        )
        assert work_day.available_slots == []

    def test_workday_day_type_values(self):
        """Проверяет, что day_type может принимать разные значения."""
        for day_type in ["четная", "нечетная", "обычный", "праздник"]:
            work_day = WorkDay(
                date=date(2026, 3, 27),
                is_holiday=False,
                day_type=day_type,
                available_slots=[]
            )
            assert work_day.day_type == day_type

    def test_workday_repr(self):
        """Проверяет работу метода __repr__."""
        slots = [TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")]
        work_day = WorkDay(
            date=date(2026, 3, 27),
            is_holiday=False,
            day_type="четная",
            available_slots=slots
        )
        repr_str = repr(work_day)
        assert "WorkDay" in repr_str
        assert "2026-03-27" in repr_str
        assert "is_holiday=False" in repr_str
        assert "day_type='четная'" in repr_str
        assert "available_slots_count=1" in repr_str

    def test_workday_available_slots_is_list_of_timeslots(self):
        """Проверяет, что available_slots — это список объектов TimeSlot."""
        slots = [TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")]
        work_day = WorkDay(
            date=date(2026, 3, 27),
            is_holiday=False,
            day_type="четная",
            available_slots=slots
        )
        assert isinstance(work_day.available_slots, list)
        assert all(isinstance(slot, TimeSlot) for slot in work_day.available_slots)

    def test_workday_available_slots_empty(self):
        """Проверяет, что available_slots может быть пустым списком."""
        work_day = WorkDay(
            date=date(2026, 3, 27),
            is_holiday=True,
            day_type="праздник",
            available_slots=[]
        )
        assert work_day.available_slots == []