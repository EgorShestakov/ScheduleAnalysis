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

    def test_get_all_slots_success(self):
        """Проверяет получение всех комбинаций room_id, date, slot_id."""
        rooms = [
            Room(id=1, number="402", capacity=30, equipment=["доска"]),
            Room(id=2, number="403", capacity=20, equipment=["компьютеры"])
        ]
        slot1 = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        slot2 = TimeSlot(id=2, number=2, start_time="10:40", end_time="12:10")
        work_days = [
            WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная",
                    available_slots=[slot1, slot2]),
            WorkDay(date=date(2026, 3, 28), is_holiday=False, day_type="четная",
                    available_slots=[slot1])
        ]

        slots = get_all_slots(rooms, work_days)

        # Ожидаем: 2 комнаты * (2 слота в первый день + 1 слот во второй день) = 2 * 3 = 6
        assert len(slots) == 6

        # Проверяем, что все комбинации присутствуют
        room_ids = {s[0] for s in slots}
        assert room_ids == {1, 2}

        dates = {s[1] for s in slots}
        assert dates == {"2026-03-27", "2026-03-28"}

        slot_ids = {s[2] for s in slots}
        assert slot_ids == {1, 2}

    def test_get_all_slots_empty_rooms(self):
        """Проверяет поведение при пустом списке аудиторий."""
        rooms = []
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        work_days = [WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная",
                              available_slots=[slot])]

        slots = get_all_slots(rooms, work_days)
        assert slots == []

    def test_get_all_slots_empty_workdays(self):
        """Проверяет поведение при пустом списке рабочих дней."""
        rooms = [Room(id=1, number="402", capacity=30, equipment=["доска"])]
        work_days = []

        slots = get_all_slots(rooms, work_days)
        assert slots == []

    def test_get_all_slots_skip_holidays(self):
        """Проверяет, что выходные дни пропускаются."""
        rooms = [Room(id=1, number="402", capacity=30, equipment=["доска"])]
        slot = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        work_days = [
            WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная",
                    available_slots=[slot]),
            WorkDay(date=date(2026, 3, 28), is_holiday=True, day_type="выходной",
                    available_slots=[slot])
        ]

        slots = get_all_slots(rooms, work_days)
        # Только один день (не выходной)
        assert len(slots) == 1
        assert slots[0][1] == "2026-03-27"

    def test_get_all_slots_order(self):
        """Проверяет, что порядок слотов соответствует перебору: комнаты → дни → слоты."""
        rooms = [
            Room(id=1, number="402", capacity=30, equipment=[]),
            Room(id=2, number="403", capacity=20, equipment=[])
        ]
        slot1 = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        slot2 = TimeSlot(id=2, number=2, start_time="10:40", end_time="12:10")
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

    @pytest.fixture
    def sample_data(self):
        """Фикстура с тестовыми данными."""
        groups = [  # теперь список, а не словарь
            Group(id=1, course=1, department="ИАИТ", number="110", size=23),
            Group(id=2, course=2, department="ИАИТ", number="120", size=15)
        ]
        rooms = [
            Room(id=1, number="402", capacity=17, equipment=["доска", "компьютеры"]),
            Room(id=2, number="403", capacity=16, equipment=["доска", "принтер"])
        ]
        slot1 = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        slot2 = TimeSlot(id=2, number=2, start_time="10:40", end_time="12:10")
        work_days = [WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная",
                              available_slots=[slot1, slot2])]
        events = [
            Event(id=1, name="Матанализ", group_id=1, teacher_id=1,
                  total_hours=1, required_features=["доска"]),
            Event(id=2, name="Численные методы", group_id=1, teacher_id=2,
                  total_hours=1, required_features=["доска", "принтер"]),
            Event(id=3, name="Инф.технологии", group_id=2, teacher_id=3,
                  total_hours=1, required_features=["компьютеры"])
        ]
        return {
            "groups": groups,
            "rooms": rooms,
            "work_days": work_days,
            "events": events
        }

    def test_build_graph_with_all_checks(self, sample_data):
        """Проверяет построение графа с полной проверкой ограничений."""
        graph = build_bipartite_graph(
            events=sample_data["events"],
            rooms=sample_data["rooms"],
            work_days=sample_data["work_days"],
            groups=sample_data["groups"],
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

    def test_build_graph_without_capacity(self, sample_data):
        """Проверяет построение графа при снятом ограничении вместимости."""
        graph = build_bipartite_graph(
            events=sample_data["events"],
            rooms=sample_data["rooms"],
            work_days=sample_data["work_days"],
            groups=sample_data["groups"],
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

    def test_build_graph_without_equipment(self, sample_data):
        """Проверяет построение графа при снятом ограничении оснащённости."""
        graph = build_bipartite_graph(
            events=sample_data["events"],
            rooms=sample_data["rooms"],
            work_days=sample_data["work_days"],
            groups=sample_data["groups"],
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

    def test_build_graph_without_both_checks(self, sample_data):
        """Проверяет построение графа при снятых обоих ограничениях."""
        graph = build_bipartite_graph(
            events=sample_data["events"],
            rooms=sample_data["rooms"],
            work_days=sample_data["work_days"],
            groups=sample_data["groups"],
            check_capacity=False,
            check_equipment=False
        )

        # Все события могут идти во все комнаты во все слоты
        # 3 события * 2 комнаты * 2 слота = 12 рёбер
        total_edges = sum(len(edges) for edges in graph.values())
        assert total_edges == 12

        for event_id in [1, 2, 3]:
            assert len(graph[event_id]) == 4  # 2 комнаты * 2 слота

    def test_build_graph_empty_input(self, sample_data):
        """Проверяет поведение при пустых входных данных."""
        # Пустые события
        graph = build_bipartite_graph(
            events=[],
            rooms=sample_data["rooms"],
            work_days=sample_data["work_days"],
            groups=sample_data["groups"]
        )
        assert graph == {}

        # Пустые комнаты
        graph = build_bipartite_graph(
            events=sample_data["events"],
            rooms=[],
            work_days=sample_data["work_days"],
            groups=sample_data["groups"]
        )
        for event_id in [1, 2, 3]:
            assert len(graph.get(event_id, [])) == 0

    def test_graph_edges_correctness(self, sample_data):
        """Проверяет, что рёбра соответствуют условиям (3.1) и (3.2)."""
        graph = build_bipartite_graph(
            events=sample_data["events"],
            rooms=sample_data["rooms"],
            work_days=sample_data["work_days"],
            groups=sample_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        # Проверяем, что в графе нет рёбер, нарушающих условия
        group_by_id = sample_data["groups"]
        room_by_id = {room.id: room for room in sample_data["rooms"]}
        event_by_id = {event.id: event for event in sample_data["events"]}

        for event_id, slots in graph.items():
            event = event_by_id[event_id]
            group = group_by_id[event.group_id]

            for room_id, date_str, slot_id in slots:
                room = room_by_id[room_id]

                # Проверяем вместимость
                assert group.size <= room.capacity

                # Проверяем оснащённость
                assert set(event.required_features).issubset(set(room.equipment))

    def test_event_with_nonexistent_group(self, sample_data):
        """Проверяет, что событие с несуществующей группой игнорируется."""
        events_with_bad_group = sample_data["events"] + [
            Event(id=4, name="Без группы", group_id=999, teacher_id=1,
                  total_hours=1, required_features=[])
        ]
        graph = build_bipartite_graph(
            events=events_with_bad_group,
            rooms=sample_data["rooms"],
            work_days=sample_data["work_days"],
            groups=sample_data["groups"]
        )
        # Событие 4 не должно появиться в графе
        assert 4 not in graph


"""Тесты для примера из главы 2 (анализ критичности)."""


class TestExampleFromChapter:
    """Тесты для примера с кабинетами c1, c2, событиями e1, e2, e3."""

    @pytest.fixture
    def example_data(self):
        """Создаёт тестовые данные из примера."""
        groups = [
            Group(id=1, course=1, department="ИАИТ", number="110", size=31),
            Group(id=2, course=1, department="ИАИТ", number="120", size=15)
        ]

        rooms = [
            Room(id=1, number="c1", capacity=40, equipment=["доска", "компьютеры"]),
            Room(id=2, number="c2", capacity=30, equipment=["доска", "принтер"])
        ]

        # Временные интервалы T = {1, 2}
        slot1 = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        slot2 = TimeSlot(id=2, number=2, start_time="10:40", end_time="12:10")
        work_days = [
            WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная",
                    available_slots=[slot1, slot2])
        ]

        events = [
            Event(id=1, name="Математический анализ", group_id=1, teacher_id=1,
                  total_hours=1, required_features=["доска"]),
            Event(id=2, name="Численные методы", group_id=1, teacher_id=2,
                  total_hours=1, required_features=["доска", "принтер"]),
            Event(id=3, name="Информационные технологии", group_id=2, teacher_id=3,
                  total_hours=1, required_features=["компьютеры"])
        ]

        return {
            "groups": groups,
            "rooms": rooms,
            "work_days": work_days,
            "events": events,
            "slot1": slot1,
            "slot2": slot2
        }

    def test_original_graph_R1(self, example_data):
        """
        Проверяет построение исходного графа R1 (с учётом вместимости и оснащённости).
        Ожидаемые рёбра: e1->(c1-1), e1->(c1-2), e3->(c1-1), e3->(c1-2)
        """
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        # Событие e1: группа g1 (31 чел) -> только c1 (40 мест), в оба слота
        assert len(graph[1]) == 2
        e1_edges = graph[1]
        for room_id, date_str, slot_id in e1_edges:
            assert room_id == 1  # только c1

        # Событие e2: группа g1 (31 чел) -> c1 подходит по вместимости (40 >= 31),
        # но требует принтер, которого в c1 нет -> рёбер нет
        assert 2 not in graph or len(graph.get(2, [])) == 0

        # Событие e3: группа g2 (15 чел) -> c1 подходит по вместимости (40 >= 15),
        # требует компьютеры (есть в c1) -> 2 ребра
        assert len(graph[3]) == 2
        for room_id, date_str, slot_id in graph[3]:
            assert room_id == 1  # только c1

        # Проверяем, что рёбра e3->(c2) отсутствуют
        for room_id, date_str, slot_id in graph[3]:
            assert room_id != 2

    def test_graph_without_features_R2(self, example_data):
        """
        Проверяет построение графа R2 (снято ограничение оснащённости, только вместимость).
        Ожидаемые рёбра: e1->c1, e2->c1, e3->c1, e3->c2 (все слоты)
        """
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=False
        )

        # e1: группа g1 (31) -> только c1 (40 >= 31), c2 не подходит (30 < 31)
        assert len(graph[1]) == 2
        for room_id, date_str, slot_id in graph[1]:
            assert room_id == 1

        # e2: группа g1 (31) -> только c1
        assert len(graph[2]) == 2
        for room_id, date_str, slot_id in graph[2]:
            assert room_id == 1

        # e3: группа g2 (15) -> подходит в c1 и c2 (оба по вместимости)
        assert len(graph[3]) == 4  # 2 комнаты * 2 слота
        room_ids = {slot[0] for slot in graph[3]}
        assert room_ids == {1, 2}  # есть рёбра и в c1, и в c2

    def test_graph_without_capacity_R3(self, example_data):
        """
        Проверяет построение графа R3 (снято ограничение вместимости, только оснащённость).
        Ожидаемые рёбра: e1->c1,c2; e2->c2; e3->c1 (все слоты)
        """
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=True
        )

        # e1: требует доску (есть в c1 и c2) -> 2 комнаты * 2 слота = 4 ребра
        assert len(graph[1]) == 4
        room_ids = {slot[0] for slot in graph[1]}
        assert room_ids == {1, 2}

        # e2: требует доску+принтер (есть только в c2) -> 1 комната * 2 слота = 2 ребра
        assert len(graph[2]) == 2
        for room_id, date_str, slot_id in graph[2]:
            assert room_id == 2

        # e3: требует компьютеры (есть только в c1) -> 1 комната * 2 слота = 2 ребра
        assert len(graph[3]) == 2
        for room_id, date_str, slot_id in graph[3]:
            assert room_id == 1

    def test_full_graph_R4(self, example_data):
        """
        Проверяет построение полносвязного графа R4 (без обоих ограничений).
        Ожидаемые рёбра: все события во все комнаты во все слоты.
        """
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=False
        )

        # 3 события * 2 комнаты * 2 слота = 12 рёбер
        total_edges = sum(len(edges) for edges in graph.values())
        assert total_edges == 12

        for event_id in [1, 2, 3]:
            assert len(graph[event_id]) == 4
            room_ids = {slot[0] for slot in graph[event_id]}
            assert room_ids == {1, 2}

    def test_EQ_set(self, example_data):
        """
        Проверяет вычисление множества EQ (конфликт только по оснащённости).
        Ожидается: e2->(c1-1), e2->(c1-2), e3->(c2-1), e3->(c2-2)
        """
        # R1: исходный граф (оба ограничения)
        R1 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        # R2: граф без оснащённости
        R2 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=False
        )

        # Преобразуем множества рёбер для сравнения
        def edges_to_set(graph):
            result = set()
            for event_id, slots in graph.items():
                for room_id, date_str, slot_id in slots:
                    result.add((event_id, room_id, slot_id))
            return result

        R1_set = edges_to_set(R1)
        R2_set = edges_to_set(R2)

        EQ = R2_set - R1_set

        # Ожидаемые рёбра в EQ
        expected_EQ = {
            (2, 1, 1),  # e2 -> c1-1
            (2, 1, 2),  # e2 -> c1-2
            (3, 2, 1),  # e3 -> c2-1
            (3, 2, 2),  # e3 -> c2-2
        }

        assert EQ == expected_EQ

    def test_CAP_set(self, example_data):
        """
        Проверяет вычисление множества CAP (конфликт только по вместимости).
        Ожидается: e1->(c2-1), e1->(c2-2), e2->(c2-1), e2->(c2-2)
        """
        # R1: исходный граф (оба ограничения)
        R1 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        # R3: граф без вместимости
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

        # Ожидаемые рёбра в CAP
        expected_CAP = {
            (1, 2, 1),  # e1 -> c2-1
            (1, 2, 2),  # e1 -> c2-2
            (2, 2, 1),  # e2 -> c2-1
            (2, 2, 2),  # e2 -> c2-2
        }

        assert CAP == expected_CAP

    def test_ALL_set(self, example_data):
        """
        Проверяет вычисление множества ALL (конфликт по обоим параметрам).
        В данном примере ALL должно быть пустым.
        """
        def edges_to_set(graph):
            result = set()
            for event_id, slots in graph.items():
                for room_id, date_str, slot_id in slots:
                    result.add((event_id, room_id, slot_id))
            return result

        # R1: исходный граф
        R1 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        # R4: полносвязный граф
        R4 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=False
        )

        R1_set = edges_to_set(R1)
        R4_set = edges_to_set(R4)

        # Вычисляем EQ и CAP как в предыдущих тестах
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

        R2_set = edges_to_set(R2)
        R3_set = edges_to_set(R3)

        EQ = R2_set - R1_set
        CAP = R3_set - R1_set

        # ALL = R4 \ (R1 ∪ EQ ∪ CAP)
        ALL = R4_set - (R1_set | EQ | CAP)

        # В примере ALL пустое
        assert ALL == set()


class TestExampleVisualization:
    """Тесты визуализации графов для примера из главы 2."""

    @pytest.fixture
    def example_data(self):
        """Создаёт тестовые данные из примера."""
        groups = [
            Group(id=1, course=1, department="ИАИТ", number="110", size=31),
            Group(id=2, course=1, department="ИАИТ", number="120", size=15)
        ]

        rooms = [
            Room(id=1, number="c1", capacity=40, equipment=["доска", "компьютеры"]),
            Room(id=2, number="c2", capacity=30, equipment=["доска", "принтер"])
        ]

        slot1 = TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")
        slot2 = TimeSlot(id=2, number=2, start_time="10:40", end_time="12:10")
        work_days = [
            WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная",
                available_slots=[slot1, slot2])
        ]

        events = [
            Event(id=1, name="Математический анализ", group_id=1, teacher_id=1,
                total_hours=1, required_features=["доска"]),
            Event(id=2, name="Численные методы", group_id=1, teacher_id=2,
                total_hours=1, required_features=["доска", "принтер"]),
            Event(id=3, name="Информационные технологии", group_id=2, teacher_id=3,
                total_hours=1, required_features=["компьютеры"])
        ]

        return {
            "groups": groups,
            "rooms": rooms,
            "work_days": work_days,
            "events": events,
            "slot1": slot1,
            "slot2": slot2
        }

    @pytest.fixture
    def graphs(self, example_data):
        """Создаёт четыре модификации графа для визуализации."""
        # R1: исходный граф (оба ограничения)
        graph_r1 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        # R2: граф без оснащённости (только вместимость)
        graph_r2 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=False
        )

        # R3: граф без вместимости (только оснащённость)
        graph_r3 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=True
        )

        # R4: полносвязный граф (без обоих ограничений)
        graph_r4 = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_days=example_data["work_days"],
            groups=example_data["groups"],
            check_capacity=False,
            check_equipment=False
        )

        return {
            "R1": graph_r1,
            "R2": graph_r2,
            "R3": graph_r3,
            "R4": graph_r4
        }

    # ==================== Тесты для visualize_bipartite_graph (matplotlib) ====================

    def test_visualize_original_graph_R1(self, example_data, graphs, tmp_path):
        """Визуализирует исходный граф R1 (оба ограничения)."""
        output_path = tmp_path / "graph_R1.png"

        try:
            visualize_bipartite_graph(
                graph=graphs["R1"],
                events=example_data["events"],
                rooms=example_data["rooms"],
                work_days=example_data["work_days"],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R1 не должна вызывать исключений: {e}")

    def test_visualize_graph_without_features_R2(self, example_data, graphs, tmp_path):
        """Визуализирует граф R2 (снято ограничение оснащённости, только вместимость)."""
        output_path = tmp_path / "graph_R2.png"

        try:
            visualize_bipartite_graph(
                graph=graphs["R2"],
                events=example_data["events"],
                rooms=example_data["rooms"],
                work_days=example_data["work_days"],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R2 не должна вызывать исключений: {e}")

    def test_visualize_graph_without_capacity_R3(self, example_data, graphs, tmp_path):
        """Визуализирует граф R3 (снято ограничение вместимости, только оснащённость)."""
        output_path = tmp_path / "graph_R3.png"

        try:
            visualize_bipartite_graph(
                graph=graphs["R3"],
                events=example_data["events"],
                rooms=example_data["rooms"],
                work_days=example_data["work_days"],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R3 не должна вызывать исключений: {e}")

    def test_visualize_full_graph_R4(self, example_data, graphs, tmp_path):
        """Визуализирует полносвязный граф R4 (без ограничений)."""
        output_path = tmp_path / "graph_R4.png"

        try:
            visualize_bipartite_graph(
                graph=graphs["R4"],
                events=example_data["events"],
                rooms=example_data["rooms"],
                work_days=example_data["work_days"],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R4 не должна вызывать исключений: {e}")

    # # ==================== Тесты для visualize_bipartite_graph_graphviz (graphviz) ====================
    #
    # def test_visualize_graphviz_original_R1(self, example_data, graphs, tmp_path):
    #     """Визуализирует исходный граф R1 через Graphviz."""
    #     output_path = tmp_path / "graphviz_R1"
    #
    #     try:
    #         visualize_bipartite_graph_graphviz(
    #             graph=graphs["R1"],
    #             events=example_data["events"],
    #             rooms=example_data["rooms"],
    #             work_days=example_data["work_days"],
    #             output_path=str(output_path)
    #         )
    #     except Exception as e:
    #         # Graphviz может выдать ошибку при попытке открыть просмотрщик
    #         # или если не может записать файл
    #         pytest.skip(f"Graphviz визуализация не удалась: {e}")
    #
    #     # Проверяем только наличие исходного .gv файла
    #     assert output_path.with_suffix('.gv').exists()
    #
    # def test_visualize_graphviz_without_features_R2(self, example_data, graphs, tmp_path):
    #     """Визуализирует граф R2 через Graphviz."""
    #     output_path = tmp_path / "graphviz_R2"
    #
    #     try:
    #         visualize_bipartite_graph_graphviz(
    #             graph=graphs["R2"],
    #             events=example_data["events"],
    #             rooms=example_data["rooms"],
    #             work_days=example_data["work_days"],
    #             output_path=str(output_path)
    #         )
    #         assert output_path.with_suffix('.gv').exists()
    #         assert output_path.with_suffix('.png').exists()
    #     except Exception as e:
    #         if "not found" in str(e).lower() or "graphviz" in str(e).lower():
    #             pytest.skip("Graphviz не установлен в системе")
    #         pytest.fail(f"Визуализация R2 (graphviz) не должна вызывать исключений: {e}")
    #
    # def test_visualize_graphviz_without_capacity_R3(self, example_data, graphs, tmp_path):
    #     """Визуализирует граф R3 через Graphviz."""
    #     output_path = tmp_path / "graphviz_R3"
    #
    #     try:
    #         visualize_bipartite_graph_graphviz(
    #             graph=graphs["R3"],
    #             events=example_data["events"],
    #             rooms=example_data["rooms"],
    #             work_days=example_data["work_days"],
    #             output_path=str(output_path)
    #         )
    #         assert output_path.with_suffix('.gv').exists()
    #         assert output_path.with_suffix('.png').exists()
    #     except Exception as e:
    #         if "not found" in str(e).lower() or "graphviz" in str(e).lower():
    #             pytest.skip("Graphviz не установлен в системе")
    #         pytest.fail(f"Визуализация R3 (graphviz) не должна вызывать исключений: {e}")
    #
    # def test_visualize_graphviz_full_R4(self, example_data, graphs, tmp_path):
    #     """Визуализирует полносвязный граф R4 через Graphviz."""
    #     output_path = tmp_path / "graphviz_R4"
    #
    #     try:
    #         visualize_bipartite_graph_graphviz(
    #             graph=graphs["R4"],
    #             events=example_data["events"],
    #             rooms=example_data["rooms"],
    #             work_days=example_data["work_days"],
    #             output_path=str(output_path)
    #         )
    #         assert output_path.with_suffix('.gv').exists()
    #         assert output_path.with_suffix('.png').exists()
    #     except Exception as e:
    #         if "not found" in str(e).lower() or "graphviz" in str(e).lower():
    #             pytest.skip("Graphviz не установлен в системе")
    #         pytest.fail(f"Визуализация R4 (graphviz) не должна вызывать исключений: {e}")

    # # ==================== Интеграционный тест ====================
    #
    # def test_all_graphs_visualized(self, example_data, graphs, tmp_path):
    #     """
    #     Проверяет, что все 4 модификации графов визуализируются без ошибок.
    #     """
    #     graph_names = ["R1", "R2", "R3", "R4"]
    #
    #     for name in graph_names:
    #         # Matplotlib
    #         output_png = tmp_path / f"graph_{name}.png"
    #         visualize_bipartite_graph(
    #             graph=graphs[name],
    #             events=example_data["events"],
    #             rooms=example_data["rooms"],
    #             work_days=example_data["work_days"],
    #             output_path=str(output_png)
    #         )
    #         assert output_png.exists()
    #
    #         # Graphviz (пропускаем, если не установлен)
    #         try:
    #             output_gv = tmp_path / f"graphviz_{name}"
    #             visualize_bipartite_graph_graphviz(
    #                 graph=graphs[name],
    #                 events=example_data["events"],
    #                 rooms=example_data["rooms"],
    #                 work_days=example_data["work_days"],
    #                 output_path=str(output_gv)
    #             )
    #         except Exception as e:
    #             if "graphviz" not in str(e).lower():
    #                 raise