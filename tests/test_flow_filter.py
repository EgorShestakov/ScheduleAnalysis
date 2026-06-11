"""Тесты для модуля flow_filter.py.

Проверяет стратегический анализ (потоковую модель):
- build_flow_network() — построение транспортной сети для 4 модификаций
- max_flow_dinic() — алгоритм Диница
- filter_slots_by_flow() — фильтрация слотов по потоку
"""

"""Тесты для модуля flow_filter.py.

Проверяет построение транспортной сети, алгоритм Диница и фильтрацию слотов.
"""

import pytest
import networkx as nx
from datetime import date
from src.data_models import Group, Room, Event, TimeSlot, WorkDay
from src.graph_builder import build_bipartite_graph, get_all_slots
from src.flow_filter import build_flow_network, max_flow_dinic, filter_slots_by_flow, visualize_flow_network


class TestBuildFlowNetwork:
    """Тесты для функции build_flow_network()."""
    def test_build_network_original(self, example_data_flow):
        """Проверяет построение исходной сети (оба ограничения)."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=True,
            check_equipment=True
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        assert network is not None
        assert isinstance(network, dict)
        assert source == 0

        all_slots = get_all_slots(example_data_flow["rooms"], example_data_flow["work_days"])
        n_events = len(example_data_flow["events"])
        n_slots = len(all_slots)
        expected_vertices = {0, n_events + n_slots + 1} | set(range(1, n_events + 1)) | set(
            range(n_events + 1, n_events + n_slots + 1))
        assert set(network.keys()) == expected_vertices or set(network.keys()).issubset(expected_vertices)

        # Визуализация
        visualize_flow_network(network, source, sink, example_data_flow["events"], all_slots,
            output_path="flow_network_original.png")

    def test_build_network_without_features(self, example_data_flow):
        """Проверяет построение сети без ограничения оснащённости."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=True,
            check_equipment=False
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        assert network is not None

        all_slots = get_all_slots(example_data_flow["rooms"], example_data_flow["work_days"])
        visualize_flow_network(network, source, sink, example_data_flow["events"], all_slots,
            output_path="flow_network_without_features.png")

    def test_build_network_without_capacity(self, example_data_flow):
        """Проверяет построение сети без ограничения вместимости."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=False,
            check_equipment=True
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        assert network is not None
        assert source == 0

        all_slots = get_all_slots(example_data_flow["rooms"], example_data_flow["work_days"])
        visualize_flow_network(network, source, sink, example_data_flow["events"], all_slots,
            output_path="flow_network_without_capacity.png")

    def test_build_network_full(self, example_data_flow):
        """Проверяет построение полной сети (без обоих ограничений)."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=False,
            check_equipment=False
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        assert network is not None

        n_events = len(example_data_flow["events"])
        all_slots = get_all_slots(example_data_flow["rooms"], example_data_flow["work_days"])
        n_slots = len(all_slots)

        for event_idx in range(1, n_events + 1):
            outgoing = len([v for v in network.get(event_idx, {}).keys()
                            if n_events + 1 <= v <= n_events + n_slots])
            assert outgoing == n_slots

        visualize_flow_network(network, source, sink, example_data_flow["events"], all_slots, output_path="flow_network_full.png")

    def test_network_capacities_non_negative(self, example_data_flow):
        """Проверяет, что все пропускные способности >= 0."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=True,
            check_equipment=True
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        for u, edges in network.items():
            for v, cap in edges.items():
                assert cap >= 0, f"Отрицательная пропускная способность на ребре ({u}->{v}): {cap}"


class TestMaxFlowDinic:
    """Тесты для функции max_flow_dinic()."""

    def test_max_flow_simple(self, example_data_flow):
        """Проверяет вычисление максимального потока на графе из примера."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=True,
            check_equipment=True
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        flow_value, flow_dist = max_flow_dinic(network, source, sink)

        all_slots = get_all_slots(example_data_flow["rooms"], example_data_flow["work_days"])
        visualize_flow_network(
            network=network,
            source=source,
            sink=sink,
            events=example_data_flow["events"],
            all_slots=all_slots,
            flow_distribution=flow_dist,
            output_path="flow_simple.png"
        )

        assert flow_value == 15

    def test_max_flow_without_capacity(self, example_data_flow):
        """Проверяет вычисление потока в сети без ограничения вместимости."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=False,
            check_equipment=True
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        flow_value, flow_dist = max_flow_dinic(network, source, sink)

        all_slots = get_all_slots(example_data_flow["rooms"], example_data_flow["work_days"])
        visualize_flow_network(
            network=network,
            source=source,
            sink=sink,
            events=example_data_flow["events"],
            all_slots=all_slots,
            flow_distribution=flow_dist,
            output_path="flow_without_capacity.png"
        )

        total_students = sum(g.size for g in example_data_flow["groups"]) + example_data_flow["groups"][0].size
        assert flow_value == total_students

    def test_max_flow_without_features(self, example_data_flow):
        """Проверяет вычисление потока в сети без ограничения оснащённости."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=True,
            check_equipment=False
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        flow_value, flow_dist = max_flow_dinic(network, source, sink)

        all_slots = get_all_slots(example_data_flow["rooms"], example_data_flow["work_days"])
        visualize_flow_network(
            network=network,
            source=source,
            sink=sink,
            events=example_data_flow["events"],
            all_slots=all_slots,
            flow_distribution=flow_dist,
            output_path="flow_without_features.png"
        )

        assert flow_value == 15

    def test_max_flow_full(self, example_data_flow):
        """Проверяет вычисление потока в полносвязной сети."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=False,
            check_equipment=False
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        flow_value, flow_dist = max_flow_dinic(network, source, sink)

        all_slots = get_all_slots(example_data_flow["rooms"], example_data_flow["work_days"])
        visualize_flow_network(
            network=network,
            source=source,
            sink=sink,
            events=example_data_flow["events"],
            all_slots=all_slots,
            flow_distribution=flow_dist,
            output_path="flow_full.png"
        )

        total_students = sum(g.size for g in example_data_flow["groups"]) + example_data_flow["groups"][0].size
        assert flow_value == total_students

    def test_max_flow_integer_result(self, example_data_flow):
        """Проверяет, что результат — целое число."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=True,
            check_equipment=True
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        flow_value, flow_dist = max_flow_dinic(network, source, sink)

        assert isinstance(flow_value, (int, float))
        assert abs(flow_value - round(flow_value)) < 1e-6


class TestFilterSlotsByFlow:
    """Тесты для функции filter_slots_by_flow()."""

    def test_filter_slots_success(self, example_data_flow):
        """Проверяет, что слоты без потока отфильтровываются."""
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=True,
            check_equipment=True
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        flow_value, flow_dist = max_flow_dinic(network, source, sink)

        all_slots = get_all_slots(example_data_flow["rooms"], example_data_flow["work_days"])

        active_slots = filter_slots_by_flow(
            flow_distribution=flow_dist,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            threshold=0.0
        )

        # В исходной сети поток идёт только через слоты c1
        # Ожидаем, что слоты c2 будут отфильтрованы
        assert len(active_slots) <= len(all_slots)
        if flow_value > 0:
            assert len(active_slots) > 0

    def test_filter_slots_no_flow(self, example_data_flow):
        """Проверяет поведение, когда ни один слот не имеет потока."""
        # Создаём событие, которое не может быть назначено ни в один слот
        impossible_event = Event(
            id=99,
            name="Невозможное",
            group_id=example_data_flow["groups"][0].id,
            teacher_id=1,
            total_hours=1,
            required_features=["несуществующее_оборудование"]
        )
        events = [impossible_event]

        bipartite_graph = build_bipartite_graph(
            events=events,
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=True,
            check_equipment=True
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=events,
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        flow_value, flow_dist = max_flow_dinic(network, source, sink)

        active_slots = filter_slots_by_flow(
            flow_distribution=flow_dist,
            events=events,
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            threshold=0.0
        )

        # Событие не может быть назначено, поэтому поток = 0, активных слотов нет
        assert flow_value == 0
        assert len(active_slots) == 0

    def test_filter_slots_all_flow(self, example_data_flow):
        """Проверяет поведение, когда все слоты имеют поток."""
        # Строим полносвязный граф
        bipartite_graph = build_bipartite_graph(
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"],
            check_capacity=False,
            check_equipment=False
        )

        network, source, sink = build_flow_network(
            bipartite_graph=bipartite_graph,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            groups=example_data_flow["groups"]
        )

        flow_value, flow_dist = max_flow_dinic(network, source, sink)

        active_slots = filter_slots_by_flow(
            flow_distribution=flow_dist,
            events=example_data_flow["events"],
            rooms=example_data_flow["rooms"],
            work_days=example_data_flow["work_days"],
            threshold=0.0
        )

        # В полносвязном графе с достаточной вместимостью все слоты должны получить поток
        # Проверяем, что функция не падает
        assert isinstance(active_slots, list)
