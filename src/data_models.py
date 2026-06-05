"""Модели данных для системы планирования расписания."""

from datetime import date
from typing import List, Optional

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

class Room:
    """Аудитория."""
    def __init__(self, id: int, number: str, capacity: int, type: str):
        """
        :param id: уникальный идентификатор
        :param number: номер аудитории
        :param capacity: вместимость
        :param type: тип (лекционная, лабораторная, компьютерная)
        """
        self.id = id
        self.number = number
        self.capacity = capacity
        self.type = type

class Teacher:
    """Преподаватель."""
    def __init__(self, id: int, name: str, department: Optional[str] = None):
        """
        :param id: уникальный идентификатор
        :param name: ФИО
        :param department: кафедра (опционально)
        """
        self.id = id
        self.name = name
        self.department = department

class Event:
    """Учебное событие (занятие)."""
    def __init__(self, id: int, name: str, group_id: int, teacher_id: int,
                 total_hours: int, required_features: str):
        """
        :param id: уникальный идентификатор
        :param name: название занятия
        :param group_id: идентификатор группы
        :param teacher_id: идентификатор преподавателя
        :param total_hours: сколько раз провести
        :param required_features: требуемое оборудование
        """
        self.id = id
        self.name = name
        self.group_id = group_id
        self.teacher_id = teacher_id
        self.total_hours = total_hours
        self.required_features = required_features

class TimeSlot:
    """Временной слот (пара)."""
    def __init__(self, id: int, number: int, start_time: str, end_time: str):
        """
        :param id: уникальный идентификатор
        :param number: номер пары
        :param start_time: время начала
        :param end_time: время окончания
        """
        self.id = id
        self.number = number
        self.start_time = start_time
        self.end_time = end_time

class WorkDay:
    """Рабочий день с доступными слотами."""
    def __init__(self, date: date, is_holiday: bool, day_type: str,
                 available_slots: List[TimeSlot]):
        """
        :param date: конкретная дата
        :param is_holiday: выходной?
        :param day_type: тип дня (четная/нечетная неделя)
        :param available_slots: список доступных слотов
        """
        self.date = date
        self.is_holiday = is_holiday
        self.day_type = day_type
        self.available_slots = available_slots
