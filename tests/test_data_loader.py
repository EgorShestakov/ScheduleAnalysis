"""Тесты для модуля data_loader.py.

Проверяет функции загрузки данных из CSV-файлов:
- load_rooms() — загрузка аудиторий
- load_teachers() — загрузка преподавателей
- load_events() — загрузка справочника событий
- load_time_grid() — загрузка временных слотов
- load_calendar() — загрузка календаря
- load_groups() — загрузка групп
- load_requirements() — загрузка заявок на события
- load_all() — загрузка всех данных
"""

import pytest
from src.data_loader import (
    load_rooms, load_teachers, load_events, load_time_grid,
    load_calendar, load_groups, load_requirements, load_all
)
from src.data_models import Group, Event, Room, Teacher, TimeSlot, WorkDay


class TestLoadRooms:
    """Тесты для функции load_rooms()."""

    def test_load_rooms_success(self):
        """Проверяет успешную загрузку аудиторий."""
        rooms = load_rooms()
        assert len(rooms) > 0
        assert rooms[0].id is not None
        assert rooms[0].capacity > 0
        assert isinstance(rooms[0].equipment, list)

    def test_load_rooms_parses_equipment(self):
        """Проверяет, что оборудование правильно парсится в список."""
        rooms = load_rooms()
        for room in rooms:
            assert isinstance(room.equipment, list)
            if room.equipment:
                assert all(isinstance(e, str) for e in room.equipment)


class TestLoadEvents:
    """Тесты для функции load_events()."""

    def test_load_events_success(self):
        """Проверяет успешную загрузку справочника событий."""
        events = load_events()
        assert len(events) > 0
        assert events[0].id is not None
        assert events[0].name is not None

    def test_load_events_unique_ids(self):
        """Проверяет, что ID событий уникальны."""
        events = load_events()
        ids = [e.id for e in events]
        assert len(ids) == len(set(ids))

    def test_load_events_names_not_empty(self):
        """Проверяет, что названия событий не пустые."""
        events = load_events()
        for event in events:
            assert event.name, f"Событие с id={event.id} имеет пустое название"


class TestLoadTeachers:
    """Тесты для функции load_teachers()."""

    def test_load_teachers_success(self):
        """Проверяет успешную загрузку преподавателей."""
        teachers = load_teachers()
        assert len(teachers) > 0
        assert teachers[0].id is not None
        assert teachers[0].surname is not None
        assert isinstance(teachers[0].specialization, list)

    def test_load_teachers_specialisation_parsing(self):
        """Проверяет, что специализация правильно парсится в список предметов."""
        teachers = load_teachers()
        for teacher in teachers:
            assert isinstance(teacher.specialization, list)
            if teacher.specialization:
                assert all(isinstance(s, str) for s in teacher.specialization)

    def test_load_teachers_specialization_refers_to_events(self):
        """Проверяет, что специализация преподавателей ссылается на существующие события."""
        teachers = load_teachers()
        events = load_events()
        event_names = {e.name for e in events}

        for teacher in teachers:
            for spec in teacher.specialization:
                assert spec in event_names, f"Предмет '{spec}' у преподавателя {teacher.surname} не найден в events.csv"


class TestLoadTimeGrid:
    """Тесты для функции load_time_grid()."""

    def test_load_time_grid_success(self):
        """Проверяет успешную загрузку временных слотов."""
        slots = load_time_grid()
        assert len(slots) > 0
        assert slots[0].id is not None
        assert slots[0].start_time is not None
        assert slots[0].end_time is not None

    def test_load_time_grid_count(self):
        """Проверяет, что количество слотов соответствует ожидаемому (7 пар)."""
        slots = load_time_grid()
        assert len(slots) == 7

    def test_load_time_grid_order(self):
        """Проверяет, что слоты идут по порядку."""
        slots = load_time_grid()
        for i, slot in enumerate(slots, start=1):
            assert slot.number == i, f"Ожидался номер слота {i}, получен {slot.number}"


class TestLoadGroups:
    """Тесты для функции load_groups()."""

    def test_load_groups_success(self):
        """Проверяет успешную загрузку групп."""
        groups = load_groups()
        assert len(groups) > 0
        assert groups[0].id is not None
        assert groups[0].course in [1, 2, 3, 4]
        assert groups[0].size > 0

    def test_load_groups_unique_ids(self):
        """Проверяет, что ID групп уникальны."""
        groups = load_groups()
        ids = [g.id for g in groups]
        assert len(ids) == len(set(ids))

    def test_load_groups_courses_range(self):
        """Проверяет, что курсы групп в диапазоне 1-4."""
        groups = load_groups()
        for group in groups:
            assert 1 <= group.course <= 4, f"Группа {group.id}: некорректный курс {group.course}"


class TestLoadCalendar:
    """Тесты для функции load_calendar()."""

    def test_load_calendar_success(self):
        """Проверяет успешную загрузку календаря."""
        work_days = load_calendar()
        assert len(work_days) > 0
        assert work_days[0].date is not None
        assert work_days[0].day_type in ["учебный", "выходной", "праздник"]

    def test_load_calendar_date_parsing(self):
        """Проверяет, что даты корректно преобразуются в тип date."""
        from datetime import date
        work_days = load_calendar()
        for day in work_days:
            assert isinstance(day.date, date)

    def test_load_calendar_available_slots(self):
        """Проверяет, что у учебных дней есть слоты, у выходных и праздников — нет."""
        work_days = load_calendar()
        for day in work_days:
            if day.day_type == "учебный" and not day.is_holiday:
                assert len(day.available_slots) > 0, f"Учебный день {day.date} не имеет слотов"
            else:
                assert len(day.available_slots) == 0, f"Нерабочий день {day.date} имеет слоты"


class TestLoadRequirements:
    """Тесты для функции load_requirements()."""

    def test_load_requirements_success(self):
        """Проверяет успешную загрузку заявок на события."""
        groups = load_groups()
        events_template = load_events()
        events = load_requirements(groups, events_template)

        assert len(events) > 0
        assert events[0].name is not None
        assert events[0].group_id is not None
        assert events[0].total_hours > 0
        assert isinstance(events[0].required_features, list)
        assert events[0].date is not None  # проверяем, что дата загружена
        assert isinstance(events[0].date, str)  # дата должна быть строкой

    def test_load_requirements_total_pairs_range(self):
        """Проверяет, что total_pairs в диапазоне 1-4."""
        groups = load_groups()
        events_template = load_events()
        events = load_requirements(groups, events_template)

        for event in events:
            assert 1 <= event.total_hours <= 4, f"Событие {event.id}: total_hours={event.total_hours} вне диапазона 1-4"

    def test_load_requirements_group_exists(self):
        """Проверяет, что group_id ссылается на существующую группу."""
        groups = load_groups()
        events_template = load_events()
        events = load_requirements(groups, events_template)

        group_ids = {g.id for g in groups}
        for event in events:
            assert event.group_id in group_ids, f"Событие {event.id}: group_id={event.group_id} не существует"

    def test_load_requirements_event_exists(self):
        """Проверяет, что event_id ссылается на существующее событие в справочнике."""
        groups = load_groups()
        events_template = load_events()
        events = load_requirements(groups, events_template)

        event_names = {e.name for e in events_template}
        for event in events:
            assert event.name in event_names, f"Событие {event.id}: имя '{event.name}' не найдено в events.csv"

    def test_load_requirements_required_features_parsing(self):
        """Проверяет, что required_features правильно парсится в список."""
        groups = load_groups()
        events_template = load_events()
        events = load_requirements(groups, events_template)

        for event in events:
            assert isinstance(event.required_features, list)
            for req in event.required_features:
                assert isinstance(req, str)
                assert req in ["доска", "проектор", "компьютеры"] or "доска" in req

    def test_load_requirements_date_format(self):
        """Проверяет, что дата имеет правильный формат YYYY-MM-DD."""
        groups = load_groups()
        events_template = load_events()
        events = load_requirements(groups, events_template)

        import re
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        for event in events:
            assert date_pattern.match(event.date), f"Событие {event.id}: дата '{event.date}' не в формате YYYY-MM-DD"

    def test_load_requirements_all_events_have_date(self):
        """Проверяет, что все загруженные события имеют дату."""
        groups = load_groups()
        events_template = load_events()
        events = load_requirements(groups, events_template)

        for event in events:
            assert event.date is not None, f"Событие {event.id} не имеет даты"
            assert event.date != "", f"Событие {event.id} имеет пустую дату"


class TestLoadAll:
    """Тесты для функции load_all()."""

    def test_load_all_returns_dict(self):
        """Проверяет, что load_all возвращает словарь со всеми ключами."""
        data = load_all()

        expected_keys = ["groups", "events", "events_template", "rooms", "teachers", "time_slots", "work_days"]
        for key in expected_keys:
            assert key in data, f"Отсутствует ключ '{key}' в результате load_all"

    def test_load_all_data_not_empty(self):
        """Проверяет, что все загруженные данные не пусты."""
        data = load_all()

        assert len(data["groups"]) > 0, "Группы не загружены"
        assert len(data["events"]) > 0, "События-занятия не загружены"
        assert len(data["events_template"]) > 0, "Справочник событий не загружен"
        assert len(data["rooms"]) > 0, "Аудитории не загружены"
        assert len(data["teachers"]) > 0, "Преподаватели не загружены"
        assert len(data["time_slots"]) > 0, "Временные слоты не загружены"
        assert len(data["work_days"]) > 0, "Календарь не загружен"

    def test_load_all_types(self):
        """Проверяет типы загруженных данных."""
        data = load_all()

        assert all(isinstance(g, Group) for g in data["groups"])
        assert all(isinstance(e, Event) for e in data["events"])
        assert all(isinstance(e, Event) for e in data["events_template"])
        assert all(isinstance(r, Room) for r in data["rooms"])
        assert all(isinstance(t, Teacher) for t in data["teachers"])
        assert all(isinstance(t, TimeSlot) for t in data["time_slots"])
        assert all(isinstance(w, WorkDay) for w in data["work_days"])