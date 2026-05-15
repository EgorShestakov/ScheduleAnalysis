"""Построение двудольного графа событие -> слот."""

from typing import List, Tuple, Dict
from data_models import Event, Room, WorkDay, Group

def build_bipartite_graph(events, rooms, work_days, groups,
                          check_capacity=True, check_features=True) -> Dict:
    """
    Строит двудольный граф H = (E, C×T, R1).
    Возвращает словарь смежности: event_id -> list[(room_id, date, slot_id)].
    """
    pass

def get_all_slots(rooms, work_days) -> List[Tuple]:
    """Возвращает список всех возможных слотов (room_id, date, slot_id)."""
    pass
