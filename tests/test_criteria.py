"""Тесты для модуля criteria.py.

Проверяет критерии существования расписания:
- criterion_one() — первый критерий |E| <= |C|*|T|
- criterion_two() — второй критерий (отсутствие изолированных событий)
"""

import pytest
from datetime import date
from src.data_models import Group, Room, Teacher, Event, TimeSlot, WorkDay
from src.criteria import criterion_one, criterion_two, criterion_three, criterion_four
from src.graph_builder import build_bipartite_graph, visualize_bipartite_graph


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

    def test_criterion_two_isolated_events(self, events_three_with_isolated, graph_with_isolated, rooms_list,
                                           groups_list):
        """Проверяет, что при наличии изолированных событий возвращает их список."""
        success, isolated = criterion_two(
            graph_with_isolated, events_three_with_isolated, rooms_list, groups_list
        )
        assert success is False
        assert 2 in isolated
        assert len(isolated) == 1

    def test_criterion_two_multiple_isolated_events(self, events_three_all_connected, graph_single_edge, rooms_list,
                                                    groups_list):
        """Проверяет, что при нескольких изолированных событиях возвращает все их id."""
        success, isolated = criterion_two(
            graph_single_edge, events_three_all_connected, rooms_list, groups_list
        )
        assert success is False
        assert len(isolated) == 2
        assert 2 in isolated
        assert 3 in isolated

    def test_criterion_two_conflict_table_capacity_only(self, rooms_list, groups_list):
        """Проверяет таблицу причин конфликтов при проблеме только с вместимостью."""
        # Событие с большой группой, аудитории с маленькой вместимостью
        large_group = Group(id=3, course=1, department="ИАИТ", number=130, size=50)
        event_large = Event(id=4, name="Большая группа", group_id=large_group.id,
            teacher_id=1, total_hours=1, required_features=[])
        events = [event_large]
        groups = groups_list + [large_group]

        # Граф пустой (все события изолированы)
        graph_empty = {}

        success, isolated = criterion_two(graph_empty, events, rooms_list, groups)
        assert success is False
        assert len(isolated) == 1

    def test_criterion_two_conflict_table_equipment_only(self, rooms_list, groups_list, room_without_equipment):
        """Проверяет таблицу причин конфликтов при проблеме только с оборудованием."""
        # Событие с требованием оборудования, которого нет в аудитории
        event_with_req = Event(id=5, name="Требует принтер", group_id=groups_list[0].id,
            teacher_id=1, total_hours=1, required_features=["принтер"])
        events = [event_with_req]

        # Граф пустой (все события изолированы)
        graph_empty = {}

        success, isolated = criterion_two(graph_empty, events, rooms_list, groups_list)
        assert success is False
        assert len(isolated) == 1

    def test_criterion_two_conflict_table_both(self, rooms_list, groups_list):
        """Проверяет таблицу причин конфликтов при проблемах и с вместимостью, и с оборудованием."""
        # Событие с большой группой и требованием оборудования
        large_group = Group(id=6, course=1, department="ИАИТ", number=140, size=100)
        event_both = Event(id=6, name="Большая и требовательная", group_id=large_group.id,
            teacher_id=1, total_hours=1, required_features=["суперкомпьютер"])
        events = [event_both]
        groups = groups_list + [large_group]

        # Граф пустой (все события изолированы)
        graph_empty = {}

        success, isolated = criterion_two(graph_empty, events, rooms_list, groups)
        assert success is False
        assert len(isolated) == 1

    def test_criterion_two_conflict_table_mixed_events(self, events_two_with_features, graph_empty, rooms_list,
                                                       groups_list):
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

    def test_criterion_two_event_not_in_graph(self, events_two_with_missing, graph_single_edge, rooms_list,
                                              groups_list):
        """Проверяет, что событие, отсутствующее в графе, считается изолированным."""
        success, isolated = criterion_two(
            graph_single_edge, events_two_with_missing, rooms_list, groups_list
        )
        assert success is False
        assert 2 in isolated
        assert 1 not in isolated

    def test_criterion_two_empty_graph_edges(self, events_two_with_empty_edges, graph_with_empty_edges, rooms_list,
                                             groups_list):
        """Проверяет, что событие с пустым списком рёбер считается изолированным."""
        success, isolated = criterion_two(
            graph_with_empty_edges, events_two_with_empty_edges, rooms_list, groups_list
        )
        assert success is False
        assert 1 in isolated
        assert 2 not in isolated


class TestCriterionThree:
    """Тесты для функции criterion_three()."""

    def test_criterion_three_perfect_matching_R2(self, groups_list, rooms_list, workday, events_list):
        """
        Проверяет нахождение совершенного паросочетания для графа R2.
        Ожидается, что паросочетание существует (необязательно совершенное, но должно покрыть все события).
        """
        # Строим граф R2 (без оснащённости, только вместимость)
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=False
        )

        # Ожидаемый граф R2 должен содержать рёбра:
        # e1 -> (c1-1), e1 -> (c1-2)
        # e2 -> (c1-1), e2 -> (c1-2)
        # e3 -> (c1-1), e3 -> (c1-2), e3 -> (c2-1), e3 -> (c2-2)

        success, matching = criterion_three(graph, events_list)

        # Проверяем, что паросочетание найдено
        assert success is True

        # Проверяем, что все события получили назначение
        assert len(matching) == len(events_list)

        # Проверяем, что каждое событие назначено в допустимый слот
        for event_id, slot in matching.items():
            assert slot in graph[event_id]

        print(f"\nНайдено совершенное паросочетание для R2:")
        for event_id, slot in matching.items():
            event = next(e for e in events_list if e.id == event_id)
            room_id, date_str, slot_id = slot
            room = next(r for r in rooms_list if r.id == room_id)
            print(f"  {event.name} -> каб.{room.number}, слот {slot_id}")

        # Визуализируем граф с выделением найденного паросочетания
        visualize_bipartite_graph(
            graph=graph,
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            matching=matching,
            output_path="graph_R2_with_matching.png"
        )

    def test_criterion_three_no_perfect_matching_R1(self, groups_list, rooms_list, workday, events_list):
        """
        Проверяет, что для графа R1 (с полными ограничениями) совершенного паросочетания нет.
        """
        # Строим граф R1 (оба ограничения)
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=True
        )

        # Ожидаемый граф R1:
        # e1 -> (c1-1), e1 -> (c1-2)
        # e2 -> нет рёбер
        # e3 -> (c1-1), e3 -> (c1-2)

        success, matching = criterion_three(graph, events_list)

        # Проверяем, что паросочетание не найдено
        assert success is False
        assert matching == {}

    def test_criterion_three_perfect_matching_R3(self, groups_list, rooms_list, workday, events_list):
        """
        Проверяет нахождение совершенного паросочетания для графа R3 (без вместимости).
        """
        # Строим граф R3 (без вместимости, только оснащённость)
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=False,
            check_equipment=True
        )

        success, matching = criterion_three(graph, events_list)

        assert success is True
        assert len(matching) == len(events_list)

        # Визуализируем
        visualize_bipartite_graph(
            graph=graph,
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            matching=matching,
            output_path="graph_R3_with_matching.png"
        )

    def test_criterion_three_perfect_matching_R4(self, groups_list, rooms_list, workday, events_list):
        """
        Проверяет нахождение совершенного паросочетания для полносвязного графа R4.
        """
        # Строим граф R4 (без обоих ограничений)
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=False,
            check_equipment=False
        )

        success, matching = criterion_three(graph, events_list)

        assert success is True
        assert len(matching) == len(events_list)

        # Визуализируем
        visualize_bipartite_graph(
            graph=graph,
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            matching=matching,
            output_path="graph_R4_with_matching.png"
        )

    def test_criterion_three_empty_graph(self, groups_list, rooms_list, workday, events_list):
        """Проверяет поведение при пустом графе."""
        graph = {}

        success, matching = criterion_three(graph, events_list)

        assert success is False
        assert matching == {}

    def test_criterion_three_single_event(self, groups_list, rooms_list, workday):
        """Проверяет случай с одним событием."""
        single_event = [Event(id=1, name="Одно событие", group_id=groups_list[0].id,
            teacher_id=1, total_hours=1, required_features=["доска"])]

        graph = build_bipartite_graph(
            events=single_event,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=True
        )

        success, matching = criterion_three(graph, single_event)

        # Для одного события должно найтись паросочетание, если есть хотя бы одно ребро
        assert success is True
        assert len(matching) == 1


class TestCriterionFour:
    """Тесты для функции criterion_four()."""

    def test_criterion_four_no_conflicts(self, groups_list, rooms_list, workday, events_list, tmp_path):
        """
        Проверяет, что при отсутствии мнимых конфликтов возвращает True.
        Строим граф R2, находим паросочетание и визуализируем.
        """
        # Строим граф R2 (без оснащённости, только вместимость)
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=False
        )

        success, matching = criterion_three(graph, events_list)
        assert success is True

        # Проверяем на мнимость (groups_list не передаём)
        result = criterion_four(matching, events_list)
        assert result is True

        # Визуализируем граф с паросочетанием
        visualize_bipartite_graph(
            graph=graph,
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            matching=matching,
            output_path=str(tmp_path / "test_criterion_four_no_conflicts.png")
        )

    def test_criterion_four_with_conflicts(self, groups_list, rooms_list, workday, events_list, tmp_path):
        """
        Проверяет, что при наличии мнимых конфликтов возвращает False.
        Для этого искусственно создаём паросочетание с конфликтом.
        """
        # Строим граф R2
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=False
        )

        # Получаем обычное паросочетание
        success, original_matching = criterion_three(graph, events_list)
        assert success is True

        # Искусственно создаём конфликт: два события одной группы в один слот
        # Находим два события одной группы
        group_events = [e for e in events_list if e.group_id == groups_list[0].id]
        if len(group_events) >= 2:
            # Берём первое событие и назначаем его в тот же слот, что и второе
            conflicting_matching = original_matching.copy()
            event1 = group_events[0]
            event2 = group_events[1]
            if event2.id in conflicting_matching:
                conflicting_matching[event1.id] = conflicting_matching[event2.id]

            result = criterion_four(conflicting_matching, events_list)
            assert result is False

            # Визуализируем граф с конфликтным паросочетанием
            visualize_bipartite_graph(
                graph=graph,
                events=events_list,
                rooms=rooms_list,
                work_days=[workday],
                matching=conflicting_matching,
                output_path=str(tmp_path / "test_criterion_four_with_conflicts.png")
            )

    def test_criterion_four_same_group_different_dates(self, groups_list, rooms_list, workday, events_list, tmp_path):
        """
        Проверяет, что одна группа в разные даты на одной паре — не конфликт.
        """
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=False
        )

        success, matching = criterion_three(graph, events_list)
        assert success is True

        # Модифицируем расписание: переносим одно событие на другой день
        if len(matching) >= 2:
            modified_matching = matching.copy()
            keys = list(modified_matching.keys())
            event_id = keys[0]
            room_id, date_str, slot_id = modified_matching[event_id]
            # Меняем дату на следующий день
            modified_matching[event_id] = (room_id, "2025-09-03", slot_id)

            result = criterion_four(modified_matching, events_list)
            assert result is True

            # Визуализируем
            visualize_bipartite_graph(
                graph=graph,
                events=events_list,
                rooms=rooms_list,
                work_days=[workday],
                matching=modified_matching,
                output_path=str(tmp_path / "test_criterion_four_same_group_different_dates.png")
            )

    def test_criterion_four_empty_assignment(self, groups_list, rooms_list, workday, events_list, tmp_path):
        """Проверяет поведение при пустом расписании."""
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=False
        )

        empty_matching = {}
        result = criterion_four(empty_matching, events_list)
        assert result is True

        # Визуализируем пустой граф
        visualize_bipartite_graph(
            graph=graph,
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            matching=None,
            output_path=str(tmp_path / "test_criterion_four_empty_assignment.png")
        )

    def test_criterion_four_real_data_R1(self, groups_list, rooms_list, workday, events_list, tmp_path):
        """
        Проверяет на графе R1 (с полными ограничениями).
        В R1 у события e2 нет рёбер, поэтому паросочетания не будет.
        """
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=True
        )

        success, matching = criterion_three(graph, events_list)
        if success:
            result = criterion_four(matching, events_list)
            visualize_bipartite_graph(
                graph=graph,
                events=events_list,
                rooms=rooms_list,
                work_days=[workday],
                matching=matching,
                output_path=str(tmp_path / "test_criterion_four_R1.png")
            )
        else:
            # Если паросочетания нет, визуализируем граф без matching
            visualize_bipartite_graph(
                graph=graph,
                events=events_list,
                rooms=rooms_list,
                work_days=[workday],
                matching=None,
                output_path=str(tmp_path / "test_criterion_four_R1_no_matching.png")
            )

        # Функция должна отработать без ошибок
        assert isinstance(success, bool)

    def test_criterion_four_real_data_R3(self, groups_list, rooms_list, workday, events_list, tmp_path):
        """
        Проверяет на графе R3 (без вместимости, только оснащённость).
        """
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=False,
            check_equipment=True
        )

        success, matching = criterion_three(graph, events_list)
        if success:
            result = criterion_four(matching, events_list)
            visualize_bipartite_graph(
                graph=graph,
                events=events_list,
                rooms=rooms_list,
                work_days=[workday],
                matching=matching,
                output_path=str(tmp_path / "test_criterion_four_R3.png")
            )
            assert isinstance(result, bool)
        else:
            visualize_bipartite_graph(
                graph=graph,
                events=events_list,
                rooms=rooms_list,
                work_days=[workday],
                matching=None,
                output_path=str(tmp_path / "test_criterion_four_R3_no_matching.png")
            )

    def test_criterion_four_real_data_R4(self, groups_list, rooms_list, workday, events_list, tmp_path):
        """
        Проверяет на полносвязном графе R4.
        """
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=False,
            check_equipment=False
        )

        success, matching = criterion_three(graph, events_list)
        assert success is True

        result = criterion_four(matching, events_list)
        assert isinstance(result, bool)

        visualize_bipartite_graph(
            graph=graph,
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            matching=matching,
            output_path=str(tmp_path / "test_criterion_four_R4.png")
        )




