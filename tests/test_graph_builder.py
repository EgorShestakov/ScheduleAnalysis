"""Тесты для модуля graph_builder.py.

Проверяет построение двудольного графа:
- build_bipartite_graph() — построение графа с/без проверки ограничений
- get_all_slots() — получение всех возможных слотов
"""

import pytest
from datetime import date
from src.data_models import Group, Room, Teacher, Event, TimeSlot, WorkDay
from src.graph_builder import build_bipartite_graph, get_all_slots
from src.graph_builder import visualize_bipartite_graph, visualize_bipartite_graph_graphviz
from graphviz import Digraph


class TestGetAllSlots:
    """Тесты для функции get_all_slots()."""

    def test_get_all_slots_success(self, rooms_two_for_slots, workdays_two_for_slots):
        """Проверяет получение всех комбинаций room_id, date, slot_id."""
        slots = get_all_slots(rooms_two_for_slots, workdays_two_for_slots)

        # Ожидаем: 2 комнаты * (2 слота в первый день + 1 слот во второй день) = 2 * 3 = 6
        assert len(slots) == 6

        # Проверяем, что все комбинации присутствуют
        room_ids = {s[0] for s in slots}
        assert room_ids == {1, 2}

        dates = {s[1] for s in slots}
        assert dates == {"2026-03-27", "2026-03-28"}

        slot_ids = {s[2] for s in slots}
        assert slot_ids == {1, 2}

    def test_get_all_slots_empty_rooms(self, workday_single):
        """Проверяет поведение при пустом списке аудиторий."""
        slots = get_all_slots([], [workday_single])
        assert slots == []

    def test_get_all_slots_empty_workdays(self, room):
        """Проверяет поведение при пустом списке рабочих дней."""
        slots = get_all_slots([room], [])
        assert slots == []

    def test_get_all_slots_skip_holidays(self, room, workday_with_holiday):
        """Проверяет, что выходные дни пропускаются."""
        slots = get_all_slots([room], workday_with_holiday)
        # Только один день (не выходной)
        assert len(slots) == 1
        assert slots[0][1] == "2026-03-27"

    def test_get_all_slots_order(self, slot1, slot2, room, room_small):
        """Проверяет, что порядок слотов соответствует перебору: комнаты → дни → слоты."""
        rooms = [room, room_small]
        work_days = [WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная",
                              available_slots=[slot1, slot2])]

        slots = get_all_slots(rooms, work_days)

        # Ожидаемый порядок: комната1, день1, слот1; комната1, день1, слот2;
        # комната2, день1, слот1; комната2, день1, слот2
        assert slots[0][0] == 1 and slots[0][2] == 1
        assert slots[1][0] == 1 and slots[1][2] == 2
        assert slots[2][0] == 2 and slots[2][2] == 1
        assert slots[3][0] == 2 and slots[3][2] == 2


class TestBuildBipartiteGraph:
    """Тесты для функции build_bipartite_graph()."""

    def test_build_graph_with_all_checks(self, groups_list, rooms_list, workday, events_list):
        """Проверяет построение графа с полной проверкой ограничений."""
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=True
        )

        # Событие 1: группа 1 (23 чел), требует доску. Может пойти в комнаты 1 и 2 (доска есть),
        # но вместимость комнаты 2 = 16 < 23 → только комната 1.
        # 2 временных слота → 2 ребра
        assert len(graph[1]) == 2
        for slot in graph[1]:
            assert slot[0] == 1  # room_id = 1

        # Событие 2: требует доску и принтер. Принтер есть только в комнате 2.
        # Вместимость комнаты 2 = 16 < 23 → не подходит! → рёбер нет
        assert len(graph.get(2, [])) == 0

        # Событие 3: группа 2 (15 чел), требует компьютеры. Компьютеры есть в комнате 1.
        # Вместимость комнаты 1 = 17 >= 15 → подходит. 2 слота → 2 ребра
        assert len(graph[3]) == 2
        for slot in graph[3]:
            assert slot[0] == 1

    def test_build_graph_without_capacity(self, groups_list, rooms_list, workday, events_list):
        """Проверяет построение графа при снятом ограничении вместимости."""
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=False,
            check_equipment=True
        )

        # Без вместимости: событие 1 и 2 могут идти в свои комнаты по оборудованию
        # Событие 1: доска есть в комнатах 1 и 2 → 2 комнаты * 2 слота = 4 ребра
        assert len(graph[1]) == 4

        # Событие 2: доска+принтер есть только в комнате 2 → 2 ребра
        assert len(graph[2]) == 2
        for slot in graph[2]:
            assert slot[0] == 2

        # Событие 3: компьютеры есть в комнате 1 → 2 ребра
        assert len(graph[3]) == 2
        for slot in graph[3]:
            assert slot[0] == 1

    def test_build_graph_without_equipment(self, groups_list, rooms_list, workday, events_list):
        """Проверяет построение графа при снятом ограничении оснащённости."""
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=False
        )

        # Без проверки оборудования: все события могут идти во все комнаты,
        # но вместимость ограничивает
        # Событие 1 и 2: группа 1 (23 чел) > 16 (комната 2) → только комната 1
        # 2 комнаты, но комната 2 не подходит по вместимости → 2 слота
        assert len(graph[1]) == 2
        assert len(graph[2]) == 2
        for slot in graph[1]:
            assert slot[0] == 1
        for slot in graph[2]:
            assert slot[0] == 1

        # Событие 3: группа 2 (15 чел) подходит по вместимости в обе комнаты
        # 2 комнаты * 2 слота = 4 ребра
        assert len(graph[3]) == 4

    def test_build_graph_without_both_checks(self, groups_list, rooms_list, workday, events_list):
        """Проверяет построение графа при снятых обоих ограничениях."""
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=False,
            check_equipment=False
        )

        # Все события могут идти во все комнаты во все слоты
        # 3 события * 2 комнаты * 2 слота = 12 рёбер
        total_edges = sum(len(edges) for edges in graph.values())
        assert total_edges == 12

        for event_id in [1, 2, 3]:
            assert len(graph[event_id]) == 4  # 2 комнаты * 2 слота

    def test_build_graph_empty_events(self, groups_list, rooms_list, workday):
        """Проверяет поведение при пустом списке событий."""
        graph = build_bipartite_graph(
            events=[],
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list
        )
        assert graph == {}

    def test_build_graph_empty_rooms(self, groups_list, workday, events_list):
        """Проверяет поведение при пустом списке аудиторий."""
        graph = build_bipartite_graph(
            events=events_list,
            rooms=[],
            work_days=[workday],
            groups=groups_list
        )
        for event_id in [1, 2, 3]:
            assert len(graph.get(event_id, [])) == 0

    def test_graph_edges_correctness(self, groups_list, rooms_list, workday, events_list):
        """Проверяет, что рёбра соответствуют условиям (3.1) и (3.2)."""
        graph = build_bipartite_graph(
            events=events_list,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list,
            check_capacity=True,
            check_equipment=True
        )

        group_by_id = {group.id: group for group in groups_list}
        room_by_id = {room.id: room for room in rooms_list}
        event_by_id = {event.id: event for event in events_list}

        for event_id, slots in graph.items():
            event = event_by_id[event_id]
            group = group_by_id[event.group_id]

            for room_id, date_str, slot_id in slots:
                room = room_by_id[room_id]

                assert group.size <= room.capacity
                assert set(event.required_features).issubset(set(room.equipment))

    def test_event_with_nonexistent_group(self, groups_list, rooms_list, workday, events_list):
        """Проверяет, что событие с несуществующей группой игнорируется."""
        events_with_bad_group = events_list + [
            Event(id=4, name="Без группы", group_id=999, teacher_id=1,
                  total_hours=1, required_features=[])
        ]
        graph = build_bipartite_graph(
            events=events_with_bad_group,
            rooms=rooms_list,
            work_days=[workday],
            groups=groups_list
        )
        assert 4 not in graph


class TestExampleFromChapter:
    """Тесты для примера с кабинетами c1, c2, событиями e1, e2, e3."""

    def test_original_graph_R1(self, example_data):
        """Проверяет построение исходного графа R1."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        assert len(graph[1]) == 2
        for slot in graph[1]:
            assert slot[0] == 1

        assert len(graph.get(2, [])) == 0

        assert len(graph[3]) == 2
        for slot in graph[3]:
            assert slot[0] == 1
            assert slot[0] != 2

    def test_graph_without_features_R2(self, example_data):
        """Проверяет построение графа R2 (снято ограничение оснащённости)."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=False
        )

        assert len(graph[1]) == 2
        for slot in graph[1]:
            assert slot[0] == 1

        assert len(graph[2]) == 2
        for slot in graph[2]:
            assert slot[0] == 1

        assert len(graph[3]) == 4
        room_ids = {slot[0] for slot in graph[3]}
        assert room_ids == {1, 2}

    def test_graph_without_capacity_R3(self, example_data):
        """Проверяет построение графа R3 (снято ограничение вместимости)."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=True
        )

        assert len(graph[1]) == 4
        room_ids_1 = {slot[0] for slot in graph[1]}
        assert room_ids_1 == {1, 2}

        assert len(graph[2]) == 2
        for slot in graph[2]:
            assert slot[0] == 2

        assert len(graph[3]) == 2
        for slot in graph[3]:
            assert slot[0] == 1

    def test_full_graph_R4(self, example_data):
        """Проверяет построение полносвязного графа R4."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=False
        )

        total_edges = sum(len(edges) for edges in graph.values())
        assert total_edges == 12

        for event_id in [1, 2, 3]:
            assert len(graph[event_id]) == 4
            room_ids = {slot[0] for slot in graph[event_id]}
            assert room_ids == {1, 2}

    def test_EQ_set(self, example_data):
        """Проверяет вычисление множества EQ."""
        R1 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        R2 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=False
        )

        def edges_to_set(graph):
            result = set()
            for event_id, slots in graph.items():
                for room_id, date_str, slot_id in slots:
                    result.add((event_id, room_id, slot_id))
            return result

        R1_set = edges_to_set(R1)
        R2_set = edges_to_set(R2)

        EQ = R2_set - R1_set

        expected_EQ = {
            (2, 1, 1), (2, 1, 2),
            (3, 2, 1), (3, 2, 2),
        }

        assert EQ == expected_EQ

    def test_CAP_set(self, example_data):
        """Проверяет вычисление множества CAP."""
        R1 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        R3 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=True
        )

        def edges_to_set(graph):
            result = set()
            for event_id, slots in graph.items():
                for room_id, date_str, slot_id in slots:
                    result.add((event_id, room_id, slot_id))
            return result

        R1_set = edges_to_set(R1)
        R3_set = edges_to_set(R3)

        CAP = R3_set - R1_set

        expected_CAP = {
            (1, 2, 1), (1, 2, 2),
            (2, 2, 1), (2, 2, 2),
        }

        assert CAP == expected_CAP

    def test_ALL_set(self, example_data):
        """Проверяет вычисление множества ALL."""
        def edges_to_set(graph):
            result = set()
            for event_id, slots in graph.items():
                for room_id, date_str, slot_id in slots:
                    result.add((event_id, room_id, slot_id))
            return result

        R1 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        R4 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=False
        )

        R2 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=False
        )

        R3 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=True
        )

        R1_set = edges_to_set(R1)
        R4_set = edges_to_set(R4)
        R2_set = edges_to_set(R2)
        R3_set = edges_to_set(R3)

        EQ = R2_set - R1_set
        CAP = R3_set - R1_set

        ALL = R4_set - (R1_set | EQ | CAP)

        assert ALL == set()


class TestExampleVisualization:
    """Тесты визуализации графов для примера из главы 2."""

    def test_visualize_original_graph_R1(self, example_data, tmp_path):
        """Визуализирует исходный граф R1 (оба ограничения)."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )
        output_path = tmp_path / "graph_R1.png"

        try:
            visualize_bipartite_graph(
                graph=graph,
                events=example_data["events"],
                rooms=example_data["rooms"],
                work_days=example_data["work_days"],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R1 не должна вызывать исключений: {e}")

    def test_visualize_graph_without_features_R2(self, example_data, tmp_path):
        """Визуализирует граф R2 (снято ограничение оснащённости, только вместимость)."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=False
        )
        output_path = tmp_path / "graph_R2.png"

        try:
            visualize_bipartite_graph(
                graph=graph,
                events=example_data["events"],
                rooms=example_data["rooms"],
                work_days=example_data["work_days"],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R2 не должна вызывать исключений: {e}")

    def test_visualize_graph_without_capacity_R3(self, example_data, tmp_path):
        """Визуализирует граф R3 (снято ограничение вместимости, только оснащённость)."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=True
        )
        output_path = tmp_path / "graph_R3.png"

        try:
            visualize_bipartite_graph(
                graph=graph,
                events=example_data["events"],
                rooms=example_data["rooms"],
                work_days=example_data["work_days"],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R3 не должна вызывать исключений: {e}")

    def test_visualize_full_graph_R4(self, example_data, tmp_path):
        """Визуализирует полносвязный граф R4 (без ограничений)."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=False
        )
        output_path = tmp_path / "graph_R4.png"

        try:
            visualize_bipartite_graph(
                graph=graph,
                events=example_data["events"],
                rooms=example_data["rooms"],
                work_days=example_data["work_days"],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R4 не должна вызывать исключений: {e}")