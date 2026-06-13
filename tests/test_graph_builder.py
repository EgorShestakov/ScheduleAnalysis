"""Тесты для модуля graph_builder.py.

Проверяет построение двудольного графа:
- build_bipartite_graph() — построение графа с/без проверки ограничений
- get_all_slots() — получение всех возможных слотов
"""

import pytest
from datetime import date
from src.data_models import Group, Room, Teacher, Event, TimeSlot, WorkDay
from src.graph_builder import build_bipartite_graph, get_all_slots_for_day, get_all_teacher_slots, \
    build_teacher_bipartite_graph, visualize_teacher_bipartite_graph
from src.graph_builder import visualize_bipartite_graph, visualize_bipartite_graph_graphviz
from graphviz import Digraph


class TestGetAllSlotsForDay:
    """Тесты для функции get_all_slots_for_day()."""

    def test_get_all_slots_success(self, room, room_small, workday):
        """Проверяет получение всех комбинаций room_id, slot_id для одного дня."""
        rooms = [room, room_small]  # room.id=1, room_small.id=2
        slots = get_all_slots_for_day(rooms, workday)

        # Ожидаем: 2 комнаты * 2 слота = 4
        assert len(slots) == 4

        # Проверяем, что все комбинации присутствуют
        room_ids = {s[0] for s in slots}
        assert room_ids == {1, 2}

        slot_ids = {s[1] for s in slots}
        assert slot_ids == {1, 2}

    def test_get_all_slots_empty_rooms(self, workday):
        """Проверяет поведение при пустом списке аудиторий."""
        slots = get_all_slots_for_day([], workday)
        assert slots == []

    def test_get_all_slots_holiday(self, room, workday_holiday):
        """Проверяет, что в выходной день слотов нет."""
        slots = get_all_slots_for_day([room], workday_holiday)
        assert slots == []

    def test_get_all_slots_order(self, room, room_small, workday):
        """Проверяет, что порядок слотов: комнаты → слоты."""
        rooms = [room, room_small]
        slots = get_all_slots_for_day(rooms, workday)

        # Ожидаемый порядок: комната1, слот1; комната1, слот2; комната2, слот1; комната2, слот2
        assert slots[0][0] == 1 and slots[0][1] == 1
        assert slots[1][0] == 1 and slots[1][1] == 2
        assert slots[2][0] == 2 and slots[2][1] == 1
        assert slots[3][0] == 2 and slots[3][1] == 2


class TestBuildBipartiteGraph:
    """Тесты для функции build_bipartite_graph()."""

    @pytest.fixture
    def test_data(self, groups_list, rooms_list, workday, events_list):
        return {
            "groups": groups_list,
            "rooms": rooms_list,
            "work_day": workday,
            "events": events_list
        }

    def test_build_graph_with_all_checks(self, test_data):
        """Проверяет построение графа с полной проверкой ограничений."""
        graph = build_bipartite_graph(
            events=test_data["events"],
            rooms=test_data["rooms"],
            work_day=test_data["work_day"],
            groups=test_data["groups"],
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

    def test_build_graph_without_capacity(self, test_data):
        """Проверяет построение графа при снятом ограничении вместимости."""
        graph = build_bipartite_graph(
            events=test_data["events"],
            rooms=test_data["rooms"],
            work_day=test_data["work_day"],
            groups=test_data["groups"],
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

    def test_build_graph_without_equipment(self, test_data):
        """Проверяет построение графа при снятом ограничении оснащённости."""
        graph = build_bipartite_graph(
            events=test_data["events"],
            rooms=test_data["rooms"],
            work_day=test_data["work_day"],
            groups=test_data["groups"],
            check_capacity=True,
            check_equipment=False
        )

        # Без проверки оборудования: все события могут идти во все комнаты,
        # но вместимость ограничивает
        # Событие 1 и 2: группа 1 (23 чел) > 16 (комната 2) → только комната 1
        assert len(graph[1]) == 2
        assert len(graph[2]) == 2
        for slot in graph[1]:
            assert slot[0] == 1
        for slot in graph[2]:
            assert slot[0] == 1

        # Событие 3: группа 2 (15 чел) подходит по вместимости в обе комнаты
        assert len(graph[3]) == 4

    def test_build_graph_without_both_checks(self, test_data):
        """Проверяет построение графа при снятых обоих ограничениях."""
        graph = build_bipartite_graph(
            events=test_data["events"],
            rooms=test_data["rooms"],
            work_day=test_data["work_day"],
            groups=test_data["groups"],
            check_capacity=False,
            check_equipment=False
        )

        # 3 события * 2 комнаты * 2 слота = 12 рёбер
        total_edges = sum(len(edges) for edges in graph.values())
        assert total_edges == 12

        for event_id in [1, 2, 3]:
            assert len(graph[event_id]) == 4

    def test_build_graph_empty_events(self, test_data):
        """Проверяет поведение при пустом списке событий."""
        graph = build_bipartite_graph(
            events=[],
            rooms=test_data["rooms"],
            work_day=test_data["work_day"],
            groups=test_data["groups"]
        )
        assert graph == {}

    def test_build_graph_empty_rooms(self, test_data):
        """Проверяет поведение при пустом списке аудиторий."""
        graph = build_bipartite_graph(
            events=test_data["events"],
            rooms=[],
            work_day=test_data["work_day"],
            groups=test_data["groups"]
        )
        for event_id in [1, 2, 3]:
            assert len(graph.get(event_id, [])) == 0

    def test_event_with_nonexistent_group(self, test_data):
        """Проверяет, что событие с несуществующей группой игнорируется."""
        events_with_bad_group = test_data["events"] + [
            Event(id=4, name="Без группы", group_id=999, teacher_id=1,
                  total_hours=1, required_features=[])
        ]
        graph = build_bipartite_graph(
            events=events_with_bad_group,
            rooms=test_data["rooms"],
            work_day=test_data["work_day"],
            groups=test_data["groups"]
        )
        assert 4 not in graph


class TestExampleFromChapter:
    """Тесты для примера с кабинетами c1, c2, событиями e1, e2, e3."""

    @pytest.fixture
    def example_data(self, groups_list, rooms_list, workday):
        """Создаёт тестовые данные из примера."""
        events = [
            Event(id=1, name="Математический анализ", group_id=groups_list[0].id,
                  teacher_id=1, total_hours=1, required_features=["доска"]),
            Event(id=2, name="Численные методы", group_id=groups_list[0].id,
                  teacher_id=2, total_hours=1, required_features=["доска", "принтер"]),
            Event(id=3, name="Информационные технологии", group_id=groups_list[1].id,
                  teacher_id=3, total_hours=1, required_features=["компьютеры"]),
        ]
        return {
            "groups": groups_list,
            "rooms": rooms_list,
            "work_day": workday,
            "events": events
        }

    def test_original_graph_R1(self, example_data):
        """Проверяет построение исходного графа R1."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_day=example_data["work_day"],
            groups=example_data["groups"],
            check_capacity=True,
            check_equipment=True
        )

        assert len(graph[1]) == 2
        for slot in graph[1]:
            assert slot[0] == 1  # c1

        assert len(graph.get(2, [])) == 0

        assert len(graph[3]) == 2
        for slot in graph[3]:
            assert slot[0] == 1

    def test_graph_without_features_R2(self, example_data):
        """Проверяет построение графа R2 (снято ограничение оснащённости)."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_day=example_data["work_day"],
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
            work_day=example_data["work_day"],
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
            work_day=example_data["work_day"],
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


class TestExampleVisualization:
    """Тесты визуализации графов для примера из главы 2."""

    def test_visualize_original_graph_R1(self, example_data, tmp_path):
        """Визуализирует исходный граф R1."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_day=example_data["work_days"][0],  # берём первый день
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
                work_day=example_data["work_days"][0],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R1 не должна вызывать исключений: {e}")

    def test_visualize_graph_without_features_R2(self, example_data, tmp_path):
        """Визуализирует граф R2."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_day=example_data["work_days"][0],
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
                work_day=example_data["work_days"][0],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R2 не должна вызывать исключений: {e}")

    def test_visualize_graph_without_capacity_R3(self, example_data, tmp_path):
        """Визуализирует граф R3."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_day=example_data["work_days"][0],
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
                work_day=example_data["work_days"][0],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R3 не должна вызывать исключений: {e}")

    def test_visualize_full_graph_R4(self, example_data, tmp_path):
        """Визуализирует полносвязный граф R4."""
        graph = build_bipartite_graph(
            events=example_data["events"],
            rooms=example_data["rooms"],
            work_day=example_data["work_days"][0],
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
                work_day=example_data["work_days"][0],
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация R4 не должна вызывать исключений: {e}")


class TestGetAllTeacherSlots:
    """Тесты для функции get_all_teacher_slots()."""

    def test_get_all_teacher_slots_success(self, teacher, teacher_2, teacher_3):
        """Проверяет получение всех комбинаций (teacher_id, t)."""
        teachers = [teacher, teacher_2, teacher_3]
        time_slots = [1, 2]

        slots = get_all_teacher_slots(teachers, time_slots)

        # Ожидаем: 3 преподавателя * 2 временных слота = 6
        assert len(slots) == 6

        # Проверяем, что все комбинации присутствуют
        teacher_ids = {s[0] for s in slots}
        assert teacher_ids == {1, 2, 3}

        time_slots_set = {s[1] for s in slots}
        assert time_slots_set == {1, 2}

    def test_get_all_teacher_slots_empty_teachers(self):
        """Проверяет поведение при пустом списке преподавателей."""
        time_slots = [1, 2]
        slots = get_all_teacher_slots([], time_slots)
        assert slots == []

    def test_get_all_teacher_slots_empty_time_slots(self, teacher):
        """Проверяет поведение при пустом списке временных слотов."""
        slots = get_all_teacher_slots([teacher], [])
        assert slots == []


class TestTeacherExampleFromChapter:
    """Тесты для примера с преподавателями p1, p2, p3 и событиями e1, e2, e3."""

    @pytest.fixture
    def teacher_data(self, teacher, teacher_2, teacher_3):
        """Создаёт тестовых преподавателей с нужной специализацией."""
        # Переопределяем специализацию для примера
        teacher.specialization = ["Инф.технологии", "Математический анализ"]
        teacher_2.specialization = ["Численные методы", "Инф.технологии"]
        teacher_3.specialization = ["Математический анализ", "Численные методы"]
        return [teacher, teacher_2, teacher_3]

    @pytest.fixture
    def teacher_events(self):
        """Создаёт тестовые события с назначенным временем."""
        return [
            Event(id=1, name="Математический анализ", group_id=1, teacher_id=None,
                total_hours=1, required_features=[], time=1),
            Event(id=2, name="Численные методы", group_id=1, teacher_id=None,
                total_hours=1, required_features=[], time=2),
            Event(id=3, name="Инф.технологии", group_id=2, teacher_id=None,  # ← исправлено
                total_hours=1, required_features=[], time=1),
        ]

    def test_original_graph_with_time_and_spec(self, teacher_data, teacher_events, tmp_path):
        """Проверяет построение исходного графа (с учётом времени и специализации)."""
        time_slots = [1, 2]

        graph = build_teacher_bipartite_graph(
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            check_time=True,
            check_specialization=True
        )

        # e1 (Мат.анализ, t=1) могут вести: p1, p3
        assert len(graph[1]) == 2
        assert (1, 1) in graph[1]  # p1, t=1
        assert (3, 1) in graph[1]  # p3, t=1

        # e2 (Численные методы, t=2) могут вести: p2, p3
        assert len(graph[2]) == 2
        assert (2, 2) in graph[2]  # p2, t=2
        assert (3, 2) in graph[2]  # p3, t=2

        # e3 (Инф.технологии, t=1) могут вести: p1, p2
        assert len(graph[3]) == 2
        assert (1, 1) in graph[3]  # p1, t=1
        assert (2, 1) in graph[3]  # p2, t=1

        # Визуализация
        output_path = tmp_path / "teacher_graph_original.png"
        visualize_teacher_bipartite_graph(
            graph=graph,
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            output_path=str(output_path)
        )

    def test_graph_without_specialization(self, teacher_data, teacher_events, tmp_path):
        """Проверяет построение графа без ограничения специализации (только время)."""
        time_slots = [1, 2]

        graph = build_teacher_bipartite_graph(
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            check_time=True,
            check_specialization=False
        )

        # Без специализации все преподаватели могут вести любые предметы
        # e1 (t=1) может вести любой преподаватель в t=1
        assert len(graph[1]) == 3  # p1, p2, p3 в t=1
        assert (1, 1) in graph[1]
        assert (2, 1) in graph[1]
        assert (3, 1) in graph[1]

        # e2 (t=2) может вести любой преподаватель в t=2
        assert len(graph[2]) == 3  # p1, p2, p3 в t=2
        assert (1, 2) in graph[2]
        assert (2, 2) in graph[2]
        assert (3, 2) in graph[2]

        # e3 (t=1) может вести любой преподаватель в t=1
        assert len(graph[3]) == 3  # p1, p2, p3 в t=1

        # Визуализация
        output_path = tmp_path / "teacher_graph_without_spec.png"
        visualize_teacher_bipartite_graph(
            graph=graph,
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            output_path=str(output_path)
        )

    def test_graph_without_time(self, teacher_data, teacher_events, tmp_path):
        """Проверяет построение графа без временного ограничения (только специализация)."""
        time_slots = [1, 2]

        graph = build_teacher_bipartite_graph(
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            check_time=False,
            check_specialization=True
        )

        # e1 (Мат.анализ) могут вести p1, p3, на любом временном слоте
        assert len(graph[1]) == 4  # p1,t=1; p1,t=2; p3,t=1; p3,t=2
        assert (1, 1) in graph[1]
        assert (1, 2) in graph[1]
        assert (3, 1) in graph[1]
        assert (3, 2) in graph[1]

        # e2 (Численные методы) могут вести p2, p3, на любом временном слоте
        assert len(graph[2]) == 4
        assert (2, 1) in graph[2]
        assert (2, 2) in graph[2]
        assert (3, 1) in graph[2]
        assert (3, 2) in graph[2]

        # e3 (Инф.технологии) могут вести p1, p2, на любом временном слоте
        assert len(graph[3]) == 4
        assert (1, 1) in graph[3]
        assert (1, 2) in graph[3]
        assert (2, 1) in graph[3]
        assert (2, 2) in graph[3]

        # Визуализация
        output_path = tmp_path / "teacher_graph_without_time.png"
        visualize_teacher_bipartite_graph(
            graph=graph,
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            output_path=str(output_path)
        )

    def test_graph_without_both_checks(self, teacher_data, teacher_events, tmp_path):
        """Проверяет построение полносвязного графа (без времени и без специализации)."""
        time_slots = [1, 2]

        graph = build_teacher_bipartite_graph(
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            check_time=False,
            check_specialization=False
        )

        # 3 события * 3 преподавателя * 2 временных слота = 18
        total_edges = sum(len(edges) for edges in graph.values())
        assert total_edges == 18

        for event_id in [1, 2, 3]:
            assert len(graph[event_id]) == 6  # 3 преподавателя * 2 слота

        # Визуализация
        output_path = tmp_path / "teacher_graph_full.png"
        visualize_teacher_bipartite_graph(
            graph=graph,
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            output_path=str(output_path)
        )

    def test_teacher_graph_without_event_time(self, teacher_data, tmp_path):
        """Проверяет, что события без времени не получают рёбер при check_time=True."""
        events_without_time = [
            Event(id=1, name="Математический анализ", group_id=1, teacher_id=None,
                  total_hours=1, required_features=[], time=None),
        ]
        time_slots = [1, 2]

        graph = build_teacher_bipartite_graph(
            events=events_without_time,
            teachers=teacher_data,
            time_slots=time_slots,
            check_time=True,
            check_specialization=True
        )

        # Должно быть 0 рёбер, так как время не задано
        assert len(graph.get(1, [])) == 0

        # Визуализация пустого графа
        output_path = tmp_path / "teacher_graph_no_time.png"
        visualize_teacher_bipartite_graph(
            graph=graph,
            events=events_without_time,
            teachers=teacher_data,
            time_slots=time_slots,
            output_path=str(output_path)
        )

    def test_teacher_graph_without_teachers(self, teacher_events, tmp_path):
        """Проверяет поведение при пустом списке преподавателей."""
        time_slots = [1, 2]

        graph = build_teacher_bipartite_graph(
            events=teacher_events,
            teachers=[],
            time_slots=time_slots,
            check_time=True,
            check_specialization=True
        )

        for event_id in [1, 2, 3]:
            assert len(graph.get(event_id, [])) == 0

        # Визуализация графа без преподавателей
        output_path = tmp_path / "teacher_graph_no_teachers.png"
        visualize_teacher_bipartite_graph(
            graph=graph,
            events=teacher_events,
            teachers=[],
            time_slots=time_slots,
            output_path=str(output_path)
        )


class TestTeacherVisualization:
    """Тесты визуализации графа преподавателей."""

    @pytest.fixture
    def teacher_data(self, teacher, teacher_2, teacher_3):
        """Создаёт тестовых преподавателей с нужной специализацией."""
        # Переопределяем специализацию для примера
        teacher.specialization = ["Инф.технологии", "Математический анализ"]
        teacher_2.specialization = ["Численные методы", "Инф.технологии"]
        teacher_3.specialization = ["Математический анализ", "Численные методы"]
        return [teacher, teacher_2, teacher_3]

    @pytest.fixture
    def teacher_events(self):
        """Создаёт тестовые события с назначенным временем."""
        return [
            Event(id=1, name="Математический анализ", group_id=1, teacher_id=None,
                total_hours=1, required_features=[], time=1),
            Event(id=2, name="Численные методы", group_id=1, teacher_id=None,
                total_hours=1, required_features=[], time=2),
            Event(id=3, name="Инф.технологии", group_id=2, teacher_id=None,  # ← исправлено
                total_hours=1, required_features=[], time=1),
        ]

    def test_visualize_teacher_graph(self, teacher_data, teacher_events, tmp_path):
        """Проверяет визуализацию графа преподавателей."""
        time_slots = [1, 2]

        graph = build_teacher_bipartite_graph(
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            check_time=True,
            check_specialization=True
        )

        output_path = tmp_path / "teacher_graph.png"

        try:
            visualize_teacher_bipartite_graph(
                graph=graph,
                events=teacher_events,
                teachers=teacher_data,
                time_slots=time_slots,
                output_path=str(output_path)
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            pytest.fail(f"Визуализация графа преподавателей не должна вызывать исключений: {e}")

    def test_visualize_teacher_graph_with_matching(self, teacher_data, teacher_events, tmp_path):
        from src.matching import max_bipartite_matching

        time_slots = [1, 2]

        graph = build_teacher_bipartite_graph(
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            check_time=True,
            check_specialization=True
        )

        left_nodes = [event.id for event in teacher_events]
        right_nodes = get_all_teacher_slots(teacher_data, time_slots)

        # matching в формате {right_node: left_node}
        matching_reverse = max_bipartite_matching(graph, left_nodes, right_nodes)

        # Преобразуем в прямой формат {event_id: (teacher_id, t)}
        matching = {}
        for slot, event_id in matching_reverse.items():
            teacher_id, t = slot
            matching[event_id] = (teacher_id, t)

        output_path = tmp_path / "teacher_graph_with_matching.png"

        visualize_teacher_bipartite_graph(
            graph=graph,
            events=teacher_events,
            teachers=teacher_data,
            time_slots=time_slots,
            matching=matching,  # передаём прямой формат
            output_path=str(output_path)
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0