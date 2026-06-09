"""Pytest фикстуры для всех тестов.

Предоставляют предопределённые объекты для повторного использования в тестах:
- sample_group — пример учебной группы
- sample_room — пример аудитории
- sample_teacher — пример преподавателя
- sample_event — пример учебного события
- sample_timeslot — пример временного слота
- sample_workday — пример рабочего дня
- sample_assignment — пример расписания
"""

import pytest
from datetime import date
from src.data_models import Group, Room, Teacher, Event, TimeSlot, WorkDay


@pytest.fixture
def sample_group():
    """Возвращает тестовую группу с id=1, курсом 1, факультетом ИАИТ, номером 110, численностью 31."""
    return Group(id=1, course=1, department="ИАИТ", number=110, size=31)


@pytest.fixture
def sample_room():
    """Возвращает тестовую аудиторию с id=1, номером 402, вместимостью 30, оборудованием []."""
    return Room(id=1, number=402, capacity=30, equipment=[])


@pytest.fixture
def sample_teacher():
    """Возвращает тестового преподавателя с id=1, фамилией Иванов, именем Иван, отчеством Иванович,
    специализацией [], кафедрой ПМиИ."""
    return Teacher(id=1, surname="Иванов", name="Иван", patronymic="Иванович",
                   specialization=[], department="ПМиИ")


@pytest.fixture
def sample_event(sample_group):
    """Возвращает тестовое событие с id=1, названием 'Матанализ', group_id=1, teacher_id=1,
    total_hours=4, required_features=['доска', 'проектор']."""
    return Event(id=1, name="Матанализ", group_id=sample_group.id,
                 teacher_id=1, total_hours=4, required_features=["доска", "проектор"])


@pytest.fixture
def sample_timeslot():
    """Возвращает тестовый временной слот с id=1, номером 1, временем 09:00–10:30."""
    return TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")


@pytest.fixture
def sample_workday(sample_timeslot):
    """Возвращает тестовый рабочий день: 2026-03-27, не выходной, тип 'четная', один слот."""
    return WorkDay(date=date(2026, 3, 27), is_holiday=False,
                   day_type="четная", available_slots=[sample_timeslot])


@pytest.fixture
def sample_assignment(sample_event, sample_room, sample_timeslot):
    """Возвращает тестовое расписание: событие -> (комната, слот)."""
    return {sample_event.id: (sample_room.id, sample_timeslot.id)}
