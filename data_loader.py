"""Загрузка входных данных из CSV-файлов."""

from typing import List, Tuple
from data_models import Room, Teacher, TimeSlot, WorkDay, Event

# def load_resources() -> Tuple[List[Room], List[Teacher]]:
#     """Загружает аудитории и преподавателей из resources.csv."""
#     pass

def load_time_grid() -> List[TimeSlot]:
    """Загружает сетку временных слотов из time_grid.csv."""
    pass

def load_calendar() -> List[WorkDay]:
    """Загружает календарь из calendar.csv."""
    pass

def load_requirements(groups) -> List[Event]:
    """Загружает заявки на события из requirements.csv."""
    pass
