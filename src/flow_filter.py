"""Потоковая модель (стратегический анализ)."""

import networkx as nx
from matplotlib import pyplot as plt

from src.graph_builder import get_all_slots_for_day
from typing import Dict, List, Tuple, Any
from collections import defaultdict


def build_flow_network(bipartite_graph: Dict[int, List[Tuple]], events: List[Any],
                       rooms: List[Any], work_day: Any, groups: List[Any]) -> Tuple[Dict[int, Dict[int, float]], int, int]:
    """
    Превращает двудольный граф в транспортную сеть для алгоритма Диница.
    Работает для ОДНОГО дня.

    Нумерация вершин:
        0 - источник (source)
        1..|E| - события (events)
        |E|+1 .. |E|+|C*T| - слоты (slots)
        |E|+|C*T|+1 - сток (sink)

    :param bipartite_graph: словарь {event_id: [(room_id, slot_id), ...]}
                            (слоты уже без даты, так как день фиксирован)
    :param events: список событий для ЭТОГО дня
    :param rooms: список аудиторий
    :param work_day: рабочий день (один)
    :param groups: список групп (нужен для получения численности группы)
    :return: (граф, источник, сток)
             граф - словарь {u: {v: capacity}}
    """
    # Получаем все слоты для этого дня (room_id, slot_id)
    all_slots = get_all_slots_for_day(rooms, work_day)

    # Создаём словари для быстрого доступа
    event_by_id = {e.id: e for e in events}
    room_by_id = {r.id: r for r in rooms}
    group_by_id = {g.id: g for g in groups}

    # Сопоставляем слотам индексы
    slot_to_idx = {slot: i for i, slot in enumerate(all_slots)}

    n_events = len(events)
    n_slots = len(all_slots)

    source = 0
    sink = n_events + n_slots + 1

    # Инициализируем граф
    graph = defaultdict(dict)

    # Рёбра от источника к событиям (используем численность группы)
    for i, event in enumerate(events, start=1):
        group = group_by_id.get(event.group_id)
        if group:
            graph[source][i] = float(group.size)  # s(e) - численность группы
        else:
            graph[source][i] = 0.0  # группа не найдена

    # Рёбра от слотов к стоку
    for i, slot in enumerate(all_slots, start=n_events + 1):
        room_id, slot_id = slot
        room = room_by_id[room_id]
        graph[i][sink] = float(room.capacity)

    # Рёбра от событий к слотам
    for event_id, slots in bipartite_graph.items():
        event = event_by_id[event_id]
        event_idx = next(i for i, e in enumerate(events, start=1) if e.id == event_id)
        group = group_by_id.get(event.group_id)

        if not group:
            continue

        for slot in slots:
            room_id, slot_id = slot  # теперь слот без даты
            room = room_by_id[room_id]
            slot_idx = n_events + 1 + slot_to_idx[(room_id, slot_id)]

            # Пропускная способность = min(численность группы, вместимость)
            capacity = min(float(group.size), float(room.capacity))
            graph[event_idx][slot_idx] = capacity

    return dict(graph), source, sink


def max_flow_dinic(network: Dict[int, Dict[int, float]], source: int, sink: int):
    """
    Вычисляет максимальный поток с помощью networkx.
    """
    G = nx.DiGraph()
    for u, edges in network.items():
        for v, cap in edges.items():
            if cap > 0:  # Добавляем только положительные пропускные способности
                G.add_edge(u, v, capacity=cap)

    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    return flow_value, flow_dict


def filter_slots_by_flow(flow_distribution: Dict[int, Dict[int, float]],
                         events: List[Any], rooms: List[Any], work_day: Any,
                         threshold: float = 0.0) -> List[Tuple]:
    """
    Фильтрует слоты на основе распределения потока для ОДНОГО дня.

    :param flow_distribution: словарь {u: {v: flow}} после выполнения max_flow_dinic
    :param events: список событий для этого дня
    :param rooms: список аудиторий
    :param work_day: рабочий день (один)
    :param threshold: минимальный поток для сохранения слота
    :return: отфильтрованный список слотов (room_id, slot_id)
    """
    all_slots = get_all_slots_for_day(rooms, work_day)
    n_events = len(events)
    slot_to_idx = {slot: i for i, slot in enumerate(all_slots)}

    active_slots = []
    for slot in all_slots:
        slot_idx = n_events + 1 + slot_to_idx[slot]
        inflow = 0.0
        for u in flow_distribution:
            if slot_idx in flow_distribution[u]:
                inflow += flow_distribution[u][slot_idx]

        if inflow > threshold:
            active_slots.append(slot)

    return active_slots


def visualize_flow_network(network: Dict[int, Dict[int, float]], source: int, sink: int,
                           events: List[Any], all_slots: List[Tuple],
                           flow_distribution: Dict[int, Dict[int, float]] = None,
                           output_path: str = "flow_network.png"):
    """
    Визуализирует транспортную сеть для ОДНОГО дня.

    :param network: словарь {u: {v: capacity}}
    :param source: источник
    :param sink: сток
    :param events: список событий (для подписей)
    :param all_slots: список слотов (room_id, slot_id) для этого дня
    :param flow_distribution: распределение потока {u: {v: flow}} (опционально)
    :param output_path: путь для сохранения
    """
    G = nx.DiGraph()
    labels = {}

    # Источник
    G.add_node(source)
    labels[source] = "s"

    # События
    n_events = len(events)
    for i, event in enumerate(events, start=1):
        G.add_node(i)
        labels[i] = event.name[:10]

    # Слоты
    for j, slot in enumerate(all_slots, start=n_events + 1):
        room_id, slot_id = slot
        G.add_node(j)
        labels[j] = f"каб.{room_id}:{slot_id}"

    # Сток
    G.add_node(sink)
    labels[sink] = "t"

    # Добавляем рёбра
    for u, edges in network.items():
        for v, cap in edges.items():
            if cap > 0:
                G.add_edge(u, v, capacity=cap)

    # Позиции вершин
    pos = {}
    pos[source] = (-2, -1)

    n_events = len(events)
    for i, event in enumerate(events, start=1):
        pos[i] = (0, -i * 1.5 + n_events * 0.75)

    n_slots = len(all_slots)
    for j, slot in enumerate(all_slots, start=n_events + 1):
        pos[j] = (2, -j * 1.5 + (n_events + n_slots + 3) * 0.75)

    pos[sink] = (4, -1)

    # Рисуем
    plt.figure(figsize=(14, 10))

    nx.draw_networkx_nodes(G, pos, nodelist=[source], node_color='green', node_size=800)
    nx.draw_networkx_nodes(G, pos, nodelist=list(range(1, n_events + 1)),
        node_color='red', node_size=500, label='События')
    nx.draw_networkx_nodes(G, pos, nodelist=list(range(n_events + 1, n_events + n_slots + 1)),
        node_color='blue', node_size=400, label='Слоты')
    nx.draw_networkx_nodes(G, pos, nodelist=[sink], node_color='orange', node_size=800)

    # Рисуем рёбра
    if flow_distribution:
        for u, v, cap in G.edges(data='capacity'):
            flow = flow_distribution.get(u, {}).get(v, 0)
            if flow > 0:
                width = 1 + flow / max(1, cap) * 3
                nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color='red',
                    arrows=True, arrowsize=15, width=width)
            else:
                nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color='gray',
                    arrows=True, arrowsize=15, width=1)
    else:
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15)

    # Подписи вершин
    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    # Подписи рёбер
    if flow_distribution:
        edge_labels = {}
        for u, v, cap in G.edges(data='capacity'):
            flow = flow_distribution.get(u, {}).get(v, 0)
            edge_labels[(u, v)] = f"{flow:.0f}/{cap:.0f}"
    else:
        edge_labels = {(u, v): f"{cap:.0f}" for u, v, cap in G.edges(data='capacity')}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    title = "Транспортная сеть"
    if flow_distribution:
        title += " (красные рёбра — поток, серые — без потока)"
    plt.title(title, fontsize=14)
    plt.legend(scatterpoints=1, loc='upper left', bbox_to_anchor=(1, 1))
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()