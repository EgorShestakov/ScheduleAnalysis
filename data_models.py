from datetime import date
from typing import List, Optional

class Group:
    def __init__(self, id: int, course: int, department: str, number: str, size: int):
        self.id = id
        self.course = course
        self.department = department
        self.number = number
        self.size = size

class Room:
    def __init__(self, id: int, number: str, capacity: int, type: str):
        self.id = id
        self.number = number
        self.capacity = capacity
        self.type = type

class Teacher:
    def __init__(self, id: int, name: str, department: Optional[str] = None):
        self.id = id
        self.name = name
        self.department = department

class Event:
    def __init__(self, id: int, name: str, group_id: int, teacher_id: int,
                 total_hours: int, required_features: str):
        self.id = id
        self.name = name
        self.group_id = group_id
        self.teacher_id = teacher_id
        self.total_hours = total_hours
        self.required_features = required_features

class TimeSlot:
    def __init__(self, id: int, number: int, start_time: str, end_time: str):
        self.id = id
        self.number = number
        self.start_time = start_time
        self.end_time = end_time

class WorkDay:
    def __init__(self, date: date, is_holiday: bool, day_type: str,
                 available_slots: List[TimeSlot]):
        self.date = date
        self.is_holiday = is_holiday
        self.day_type = day_type
        self.available_slots = available_slots
