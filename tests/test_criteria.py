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

    def test_criterion_one_valid(self, events_5, rooms_3, workdays_2):
        """Проверяет, что при |E| <= |C|*|T| возвращает True."""
        result = criterion_one(events_5, rooms_3, workdays_2)
        assert result is True

    def test_criterion_one_invalid(self, events_10, rooms_3, workdays_2):
        """Проверяет, что при |E| > |C|*|T| возвращает False и выводит рекомендации."""
        result = criterion_one(events_10, rooms_3, workdays_2)
        assert result is False

    def test_criterion_one_edge_case_equal(self, events_6, rooms_3, workdays_2):
        """Проверяет граничный случай |E| == |C|*|T|."""
        result = criterion_one(events_6, rooms_3, workdays_2)
        assert result is True

    def test_criterion_one_recommendations_format(self, events_15, rooms_3, workday_single):
        """Проверяет, что рекомендации содержат конкретные числа и варианты действий."""
        work_days = [workday_single]
        result = criterion_one(events_15, rooms_3, work_days)
        assert result is False

    def test_criterion_one_empty_events(self, rooms_3, workday_single):
        """Проверяет поведение при пустом списке событий."""
        result = criterion_one([], rooms_3, [workday_single])
        assert result is True

    def test_criterion_one_empty_rooms(self, event_single, workday_single):
        """Проверяет поведение при пустом списке аудиторий."""
        result = criterion_one([event_single], [], [workday_single])
        assert result is False

    def test_criterion_one_empty_workdays(self, event_single, room_single):
        """Проверяет поведение при пустом списке рабочих дней."""
        result = criterion_one([event_single], [room_single], [])
        assert result is False


class TestCriterionTwo:
    """Тесты для функции criterion_two()."""

    def test_criterion_two_all_connected(self, events_two_all_connected, graph_connected, rooms_list, groups_list):
        """Проверяет, что при отсутствии изолированных событий возвращает (True, [])."""
        success, isolated = criterion_two(
            graph_connected, events_two_all_connected, rooms_list, groups_list
        )
        assert success is True
        assert isolated == []

    def test_criterion_two_isolated_events(self, events_three_with_isolated, graph_with_isolated, rooms_list, groups_list):
        """Проверяет, что при наличии изолированных событий возвращает их список."""
        success, isolated = criterion_two(
            graph_with_isolated, events_three_with_isolated, rooms_list, groups_list
        )
        assert success is False
        assert 2 in isolated
        assert len(isolated) == 1

    def test_criterion_two_multiple_isolated_events(self, events_three_all_connected, graph_single_edge, rooms_list, groups_list):
        """Проверяет, что при нескольких изолированных событиях возвращает все их id."""
        success, isolated = criterion_two(
            graph_single_edge, events_three_all_connected, rooms_list, groups_list
        )
        assert success is False
        assert len(isolated) == 2
        assert 2 in isolated
        assert 3 in isolated

    def test_criterion_two_conflict_table(self, events_two_with_features, graph_empty, rooms_list, groups_list):
        """Проверяет, что таблица причин конфликтов формируется корректно."""
        success, isolated = criterion_two(
            graph_empty, events_two_with_features, rooms_list, groups_list
        )
        assert success is False
        assert len(isolated) == 2

    def test_criterion_two_empty_graph(self, events_two_all_connected, graph_empty, rooms_list, groups_list):
        """Проверяет поведение при пустом графе (все события изолированы)."""
        success, isolated = criterion_two(
            graph_empty, events_two_all_connected, rooms_list, groups_list
        )
        assert success is False
        assert len(isolated) == 2

    def test_criterion_two_empty_events(self, graph_single_edge, rooms_list, groups_list):
        """Проверяет поведение при пустом списке событий."""
        success, isolated = criterion_two(graph_single_edge, [], rooms_list, groups_list)
        assert success is True
        assert isolated == []

    def test_criterion_two_event_not_in_graph(self, events_two_with_missing, graph_single_edge, rooms_list, groups_list):
        """Проверяет, что событие, отсутствующее в графе, считается изолированным."""
        success, isolated = criterion_two(
            graph_single_edge, events_two_with_missing, rooms_list, groups_list
        )
        assert success is False
        assert 2 in isolated
        assert 1 not in isolated

    def test_criterion_two_empty_graph_edges(self, events_two_with_empty_edges, graph_with_empty_edges, rooms_list, groups_list):
        """Проверяет, что событие с пустым списком рёбер считается изолированным."""
        success, isolated = criterion_two(
            graph_with_empty_edges, events_two_with_empty_edges, rooms_list, groups_list
        )
        assert success is False
        assert 1 in isolated
        assert 2 not in isolated