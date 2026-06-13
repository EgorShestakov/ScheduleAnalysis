"""Загрузка входных данных из CSV-файлов."""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
from src.data_models import Room, Teacher, TimeSlot, WorkDay, Event, Group

# Путь к папке с входными данными
INPUT_DIR = Path(__file__).parent.parent / "src" / "data" / "input"


def load_rooms() -> List[Room]:
    """Загружает аудитории из rooms.csv."""
    rooms = []
    with open(INPUT_DIR / "rooms.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # equipment хранится как строка, например "доска, компьютеры"
            equipment = [e.strip() for e in row["equipment"].split(",")]
            room = Room(
                id=int(row["id"]),
                number=int(row["number"]),
                capacity=int(row["capacity"]),
                equipment=equipment
            )
            rooms.append(room)
    return rooms


def load_teachers() -> List[Teacher]:
    """Загружает преподавателей из teachers.csv."""
    teachers = []
    # Сначала загружаем события, чтобы преобразовать ID в названия
    events = load_events()
    event_id_to_name = {e.id: e.name for e in events}

    with open(INPUT_DIR / "teachers.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # specialisation хранится как "5,12,18"
            specialization_ids = [int(x.strip()) for x in row["specialisation"].split(",")]
            # Преобразуем ID в названия предметов
            specialization_names = [event_id_to_name[eid] for eid in specialization_ids if eid in event_id_to_name]

            teacher = Teacher(
                id=int(row["id"]),
                surname=row["surname"],
                name=row["name"],
                patronymic=row["patronymic"],
                specialization=specialization_names,
                department=""  # department не хранится в teachers.csv
            )
            teachers.append(teacher)
    return teachers


def load_events() -> List[Event]:
    """Загружает события из events.csv (справочник предметов)."""
    events = []
    with open(INPUT_DIR / "events.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Для событий teacher_id и time пока None, они будут заполнены позже
            event = Event(
                id=int(row["id"]),
                name=row["name"],
                group_id=-1,  # временное значение, будет заменено при загрузке requirements
                teacher_id=None,
                total_hours=1,  # временное значение
                required_features=[]
            )
            events.append(event)
    return events


def load_time_grid() -> List[TimeSlot]:
    """Загружает сетку временных слотов из time_grid.csv."""
    time_slots = []
    with open(INPUT_DIR / "time_grid.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slot = TimeSlot(
                id=int(row["slot_id"]),
                number=int(row["slot_id"]),
                start_time=row["start_time"],
                end_time=row["end_time"]
            )
            time_slots.append(slot)
    return time_slots


def load_calendar() -> List[WorkDay]:
    """Загружает календарь из calendar.csv."""
    work_days = []
    time_slots = load_time_grid()

    with open(INPUT_DIR / "calendar.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = datetime.strptime(row["date"], "%Y-%m-%d").date()
            is_holiday = row["is_holiday"] == "True"
            day_type = row["day_type"]

            # Для учебных дней доступны все временные слоты
            # Для выходных и праздников слотов нет
            available_slots = time_slots if not is_holiday and day_type == "учебный" else []

            work_day = WorkDay(
                date=date,
                is_holiday=is_holiday,
                day_type=day_type,
                available_slots=available_slots
            )
            work_days.append(work_day)
    return work_days


def load_groups() -> List[Group]:
    """Загружает группы из groups.csv."""
    groups = []
    with open(INPUT_DIR / "groups.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            group = Group(
                id=int(row["id"]),
                course=int(row["course"]),
                department=row["department"],
                number=int(row["number"]),
                size=int(row["size"])
            )
            groups.append(group)
    return groups


def load_requirements(groups: List[Group], events: List[Event]) -> List[Event]:
    """
    Загружает заявки на события из requirements.csv и создаёт события-занятия.

    :param groups: список групп (для получения численности)
    :param events: список событий-шаблонов (справочник)
    :return: список событий-занятий (каждая строка requirements -> одно событие)
    """
    # Словари для быстрого доступа
    group_by_id = {g.id: g for g in groups}
    event_template_by_id = {e.id: e for e in events}
    event_template_by_name = {e.name: e for e in events}

    result_events = []
    event_id = 1

    with open(INPUT_DIR / "requirements.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            group_id = int(row["group_id"])
            event_template_id = int(row["event_id"])
            total_pairs = int(row["total_pairs"])
            required_features_str = row["requirement"]

            group = group_by_id.get(group_id)
            event_template = event_template_by_id.get(event_template_id)

            if group is None or event_template is None:
                continue

            # required_features из строки "доска, компьютеры" в список
            required_features = [f.strip() for f in required_features_str.split(",")]

            # Создаём событие
            event = Event(
                id=event_id,
                name=event_template.name,
                group_id=group.id,
                teacher_id=None,  # пока не назначен
                total_hours=total_pairs,
                required_features=required_features
            )
            result_events.append(event)
            event_id += 1

    return result_events


def load_all() -> Dict:
    """
    Загружает все данные и возвращает словарь с ними.
    """
    groups = load_groups()
    events_template = load_events()
    rooms = load_rooms()
    teachers = load_teachers()
    time_slots = load_time_grid()
    work_days = load_calendar()
    events = load_requirements(groups, events_template)

    return {
        "groups": groups,
        "events": events,
        "events_template": events_template,
        "rooms": rooms,
        "teachers": teachers,
        "time_slots": time_slots,
        "work_days": work_days
    }