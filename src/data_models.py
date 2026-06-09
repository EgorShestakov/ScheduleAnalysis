"""Модели данных для системы планирования расписания."""

from datetime import date
from typing import List


class Group:
    """Учебная группа."""

    def __init__(self, id: int, course: int, department: str, number: str, size: int):
        """
        :param id: уникальный идентификатор
        :param course: курс обучения
        :param department: факультет
        :param number: номер группы
        :param size: численность группы
        """
        self.id = id
        self.course = course
        self.department = department
        self.number = number
        self.size = size

    def __repr__(self) -> str:
        return f"Group(id={self.id}, course={self.course}, department='{self.department}', number='{self.number}', size={self.size})"


class Room:
    """Аудитория."""

    def __init__(self, id: int, number: int, capacity: int, equipment: List[str]):
        """
        :param id: уникальный идентификатор
        :param number: номер аудитории
        :param capacity: вместимость
        :param equipment: список оборудования (например, ["доска", "компьютеры"])
        """
        self.id = id
        self.number = number
        self.capacity = capacity
        self.equipment = equipment

    def __repr__(self) -> str:
        return f"Room(id={self.id}, number='{self.number}', capacity={self.capacity}, equipment={self.equipment})"


class Teacher:
    """Преподаватель."""

    def __init__(self, id: int, surname: str, name: str, patronymic: str,
                 specialization: List[str], department: str):
        """
        :param id: уникальный идентификатор
        :param surname: фамилия
        :param name: имя
        :param patronymic: отчество
        :param specialization: список предметов, которые может вести
        :param department: кафедра
        """
        self.id = id
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.specialization = specialization
        self.department = department

    def full_name(self) -> str:
        """
        Возвращает полное ФИО в формате 'Фамилия И.О.'.
        Например: "Иванов И.И."
        """
        name_initial = self.name[0] + "." if self.name else ""
        patronymic_initial = self.patronymic[0] + "." if self.patronymic else ""
        return f"{self.surname} {name_initial}{patronymic_initial}".strip()

    def __repr__(self) -> str:
        return (f"Teacher(id={self.id}, full_name='{self.full_name()}', "
                f"specialization={self.specialization}, department='{self.department}')")


class Event:
    """Учебное событие (занятие)."""

    def __init__(self, id: int, name: str, group_id: int, teacher_id: int,
                 total_hours: int, required_features: List[str]):
        """
        :param id: уникальный идентификатор
        :param name: название занятия
        :param group_id: идентификатор группы
        :param teacher_id: идентификатор преподавателя
        :param total_hours: сколько раз провести (количество пар)
        :param required_features: список требуемого оборудования
        """
        self.id = id
        self.name = name
        self.group_id = group_id
        self.teacher_id = teacher_id
        self.total_hours = total_hours
        self.required_features = required_features

    def __repr__(self) -> str:
        return (f"Event(id={self.id}, name='{self.name}', group_id={self.group_id}, "
                f"teacher_id={self.teacher_id}, total_hours={self.total_hours}, "
                f"required_features={self.required_features})")


class TimeSlot:
    """Временной слот (пара)."""

    def __init__(self, id: int, number: int, start_time: str, end_time: str):
        """
        :param id: уникальный идентификатор
        :param number: номер пары
        :param start_time: время начала (формат "HH:MM")
        :param end_time: время окончания (формат "HH:MM")
        """
        self.id = id
        self.number = number
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self) -> str:
        return f"TimeSlot(id={self.id}, number={self.number}, start_time='{self.start_time}', end_time='{self.end_time}')"


class WorkDay:
    """Рабочий день с доступными слотами."""

    def __init__(self, date: date, is_holiday: bool, day_type: str,
                 available_slots: List[TimeSlot]):
        """
        :param date: конкретная дата
        :param is_holiday: выходной?
        :param day_type: тип дня ("четная", "нечетная", "обычный")
        :param available_slots: список доступных слотов
        """
        self.date = date
        self.is_holiday = is_holiday
        self.day_type = day_type
        self.available_slots = available_slots

    def __repr__(self) -> str:
        return (f"WorkDay(date={self.date.isoformat()}, is_holiday={self.is_holiday}, "
                f"day_type='{self.day_type}', available_slots_count={len(self.available_slots)})")