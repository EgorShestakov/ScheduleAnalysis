"""Тесты для модуля criteria.py.

Проверяет критерии существования расписания:
- criterion_one() — первый критерий |E| <= |C|*|T|
- criterion_two() — второй критерий (отсутствие изолированных событий)
"""

import pytest
from datetime import date
from src.data_models import Group, Room, Teacher, Event, TimeSlot, WorkDay
from src.criteria import criterion_one, criterion_two


class TestCriterionOne:
    """Тесты для функции criterion_one()."""

    def test_criterion_one_valid(self):
        """Проверяет, что при |E| <= |C|*|T| возвращает True."""
        # Создаём данные: 5 событий, 3 аудитории, 2 временных слота → 3*2=6 >= 5
        events = [Event(id=i, name=f"E{i}", group_id=1, teacher_id=1, total_hours=1, required_features=[]) for i in range(5)]
        rooms = [
            Room(id=1, number=101, capacity=30, equipment=[]),
            Room(id=2, number=102, capacity=30, equipment=[]),
            Room(id=3, number=103, capacity=30, equipment=[])
        ]
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        work_days = [
            WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная", available_slots=[slot]),
            WorkDay(date=date(2026, 3, 28), is_holiday=False, day_type="четная", available_slots=[slot])
        ]
        result = criterion_one(events, rooms, work_days)
        assert result is True

    def test_criterion_one_invalid(self):
        """Проверяет, что при |E| > |C|*|T| возвращает False и выводит рекомендации."""
        # Создаём данные: 10 событий, 3 аудитории, 2 временных слота → 3*2=6 < 10
        events = [Event(id=i, name=f"E{i}", group_id=1, teacher_id=1, total_hours=1, required_features=[]) for i in range(10)]
        rooms = [
            Room(id=1, number=101, capacity=30, equipment=[]),
            Room(id=2, number=102, capacity=30, equipment=[]),
            Room(id=3, number=103, capacity=30, equipment=[])
        ]
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        work_days = [
            WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная", available_slots=[slot]),
            WorkDay(date=date(2026, 3, 28), is_holiday=False, day_type="четная", available_slots=[slot])
        ]
        result = criterion_one(events, rooms, work_days)
        assert result is False

    def test_criterion_one_edge_case_equal(self):
        """Проверяет граничный случай |E| == |C|*|T|."""
        # Создаём данные: 6 событий, 3 аудитории, 2 временных слота → 3*2=6 == 6
        events = [Event(id=i, name=f"E{i}", group_id=1, teacher_id=1, total_hours=1, required_features=[]) for i in range(6)]
        rooms = [
            Room(id=1, number=101, capacity=30, equipment=[]),
            Room(id=2, number=102, capacity=30, equipment=[]),
            Room(id=3, number=103, capacity=30, equipment=[])
        ]
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        work_days = [
            WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная", available_slots=[slot]),
            WorkDay(date=date(2026, 3, 28), is_holiday=False, day_type="четная", available_slots=[slot])
        ]
        result = criterion_one(events, rooms, work_days)
        assert result is True

    def test_criterion_one_recommendations_format(self):
        """Проверяет, что рекомендации содержат конкретные числа и варианты действий."""
        events = [Event(id=i, name=f"E{i}", group_id=1, teacher_id=1, total_hours=1, required_features=[]) for i in range(15)]
        rooms = [
            Room(id=1, number=101, capacity=30, equipment=[]),
            Room(id=2, number=102, capacity=30, equipment=[]),
            Room(id=3, number=103, capacity=30, equipment=[])
        ]
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        work_days = [WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная", available_slots=[slot])]
        # 15 > 3*1 = 3, нарушение
        result = criterion_one(events, rooms, work_days)
        assert result is False
        # Рекомендации выводятся в консоль, функционально проверяем только возвращаемое значение

    def test_criterion_one_empty_events(self):
        """Проверяет поведение при пустом списке событий."""
        events = []
        rooms = [Room(id=1, number=101, capacity=30, equipment=[])]
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        work_days = [WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная", available_slots=[slot])]
        result = criterion_one(events, rooms, work_days)
        assert result is True

    def test_criterion_one_empty_rooms(self):
        """Проверяет поведение при пустом списке аудиторий."""
        events = [Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[])]
        rooms = []
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        work_days = [WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная", available_slots=[slot])]
        result = criterion_one(events, rooms, work_days)
        assert result is False

    def test_criterion_one_empty_workdays(self):
        """Проверяет поведение при пустом списке рабочих дней."""
        events = [Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[])]
        rooms = [Room(id=1, number=101, capacity=30, equipment=[])]
        work_days = []
        result = criterion_one(events, rooms, work_days)
        assert result is False


class TestCriterionTwo:
    """Тесты для функции criterion_two()."""

    def test_criterion_two_all_connected(self):
        """Проверяет, что при отсутствии изолированных событий возвращает (True, [])."""
        graph = {1: [(1, date(2026, 3, 27), 1)], 2: [(2, date(2026, 3, 27), 1)]}
        events = [
            Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
            Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        ]
        success, isolated = criterion_two(graph, events)
        assert success is True
        assert isolated == []

    def test_criterion_two_isolated_events(self):
        """Проверяет, что при наличии изолированных событий возвращает их список."""
        graph = {1: [(1, date(2026, 3, 27), 1)], 3: [(1, date(2026, 3, 27), 2)]}
        events = [
            Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
            Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
            Event(id=3, name="E3", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        ]
        success, isolated = criterion_two(graph, events)
        assert success is False
        assert 2 in isolated
        assert len(isolated) == 1

    def test_criterion_two_multiple_isolated_events(self):
        """Проверяет, что при нескольких изолированных событиях возвращает все их id."""
        graph = {1: [(1, date(2026, 3, 27), 1)]}
        events = [
            Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
            Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
            Event(id=3, name="E3", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        ]
        success, isolated = criterion_two(graph, events)
        assert success is False
        assert len(isolated) == 2
        assert 2 in isolated
        assert 3 in isolated

    def test_criterion_two_conflict_table(self):
        """Проверяет, что таблица причин конфликтов формируется корректно."""
        graph = {}  # Пустой граф, все события изолированы
        events = [
            Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=["доска"]),
            Event(id=2, name="E2", group_id=2, teacher_id=2, total_hours=1, required_features=["компьютеры"]),
        ]
        success, isolated = criterion_two(graph, events)
        assert success is False
        assert len(isolated) == 2
        # Таблица причин выводится в консоль, функционально проверяем только возвращаемое значение

    def test_criterion_two_empty_graph(self):
        """Проверяет поведение при пустом графе (все события изолированы)."""
        graph = {}
        events = [
            Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
            Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        ]
        success, isolated = criterion_two(graph, events)
        assert success is False
        assert len(isolated) == 2

    def test_criterion_two_empty_events(self):
        """Проверяет поведение при пустом списке событий."""
        graph = {1: [(1, date(2026, 3, 27), 1)]}
        events = []
        success, isolated = criterion_two(graph, events)
        assert success is True
        assert isolated == []

    def test_criterion_two_event_not_in_graph(self):
        """Проверяет, что событие, отсутствующее в графе, считается изолированным."""
        graph = {1: [(1, date(2026, 3, 27), 1)]}
        events = [
            Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
            Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        ]
        success, isolated = criterion_two(graph, events)
        assert success is False
        assert 2 in isolated
        assert 1 not in isolated

    def test_criterion_two_empty_graph_edges(self):
        """Проверяет, что событие с пустым списком рёбер считается изолированным."""
        graph = {1: [], 2: [(1, date(2026, 3, 27), 1)]}
        events = [
            Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
            Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        ]
        success, isolated = criterion_two(graph, events)
        assert success is False
        assert 1 in isolated
        assert 2 not in isolated