"""Построение двудольного графа событие -> слот."""

from typing import List, Tuple, Dict
from collections import defaultdict
from src.data_models import Event, Room, WorkDay, Group
from graphviz import Digraph
import networkx as nx
import matplotlib.pyplot as plt


def get_all_slots(rooms: List[Room], work_days: List[WorkDay]) -> List[Tuple[int, str, int]]:
    """
    Возвращает список всех возможных слотов (room_id, date, timeslot_id).
    """
    slots = []

    for room in rooms:
        for work_day in work_days:
            if work_day.is_holiday:
                continue  # пропускаем выходные дни
            for timeslot in work_day.available_slots:
                slots.append((room.id, work_day.date.isoformat(), timeslot.id))

    return slots


def build_bipartite_graph(events: List[Event], rooms: List[Room], work_days: List[WorkDay],
                          groups: List[Group], check_capacity: bool = True,
                          check_equipment: bool = True) -> Dict[int, List[Tuple[int, str, int]]]:
    """
    Строит двудольный граф H = (E, C×T, R1).
    Возвращает словарь смежности: event_id -> list[(room_id, date, timeslot_id)].

    :param events: список событий
    :param rooms: список аудиторий
    :param work_days: список рабочих дней
    :param groups: словарь групп {group_id: Group}
    :param check_capacity: учитывать ли ограничение вместимости
    :param check_equipment: учитывать ли ограничение оснащённости
    :return: словарь смежности event_id -> список слотов
    """
    # Получаем все возможные слоты
    all_slots = get_all_slots(rooms, work_days)

    # Создаём словари для быстрого доступа
    group_by_id = {group.id: group for group in groups}
    room_capacity = {room.id: room.capacity for room in rooms}
    room_equipment = {room.id: set(room.equipment) for room in rooms}

    graph = defaultdict(list)

    for event in events:
        group = group_by_id.get(event.group_id)
        if group is None:
            continue

        event_requirements = set(event.required_features)

        for room_id, date_str, timeslot_id in all_slots:
            # Проверка вместимости
            if check_capacity and group.size > room_capacity[room_id]:
                continue

            # Проверка оборудования
            if check_equipment and not event_requirements.issubset(room_equipment[room_id]):
                continue

            graph[event.id].append((room_id, date_str, timeslot_id))

    return dict(graph)


def visualize_bipartite_graph(graph, events, rooms, work_days, output_path="graph.png"):
    """
    Визуализирует двудольный граф.
    Левые вершины (события) — красные, правые (слоты) — синие.
    Вершины расположены на двух параллельных линиях.
    """
    G = nx.DiGraph()

    # Добавляем вершины левой доли (события)
    for event in events:
        G.add_node(f"E{event.id}", bipartite=0, label=event.name[:10])

    # Добавляем вершины правой доли (слоты)
    for room in rooms:
        for day in work_days:
            for slot in day.available_slots:
                node_id = f"{room.number}_{day.date}_{slot.number}"
                G.add_node(node_id, bipartite=1, label=node_id)

    # Добавляем рёбра
    for event_id, slots in graph.items():
        for room_id, date_str, slot_id in slots:
            # Находим комнату по id
            room = next((r for r in rooms if r.id == room_id), None)
            if room:
                node_id = f"{room.number}_{date_str}_{slot_id}"
                G.add_edge(f"E{event_id}", node_id)

    # Получаем списки вершин каждой доли
    left_nodes = [n for n in G.nodes if G.nodes[n]['bipartite'] == 0]
    right_nodes = [n for n in G.nodes if G.nodes[n]['bipartite'] == 1]

    # Используем специальное расположение для двудольных графов
    # Параметры: scale - расстояние между долями, center - центр графика
    pos = nx.bipartite_layout(G, left_nodes, align='vertical', scale=2)

    # Альтернативный вариант - горизонтальное расположение (доли слева и справа)
    # pos = bipartite_layout(G, left_nodes, align='horizontal', scale=2)

    # Рисуем граф
    plt.figure(figsize=(12, 8))

    nx.draw_networkx_nodes(G, pos, nodelist=left_nodes,
        node_color='red', node_size=500, alpha=0.8, label='События')
    nx.draw_networkx_nodes(G, pos, nodelist=right_nodes,
        node_color='blue', node_size=300, alpha=0.8, label='Слоты')
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.5,
        arrows=True, arrowsize=10, connectionstyle='arc3,rad=0.1')

    # Рисуем метки с небольшим смещением для читаемости
    nx.draw_networkx_labels(G, pos, {n: G.nodes[n]['label'] for n in G.nodes},
        font_size=8, font_weight='bold')

    plt.title("Двудольный граф событий и слотов", fontsize=14, fontweight='bold')
    plt.legend(scatterpoints=1, loc='upper right', fontsize=10)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()


def visualize_bipartite_graph_graphviz(graph, events, rooms, work_days, output_path="graph.gv"):
    """Визуализирует двудольный граф с иерархической раскладкой."""
    dot = Digraph(comment='Bipartite Graph', format='png')
    dot.attr(rankdir='LR')  # слева направо

    # Вершины левой доли (события) — слева
    for event in events:
        dot.node(f"E{event.id}", f"{event.name[:15]}", shape='box', style='filled',
            fillcolor='lightcoral', fontname='Arial')

    # Группируем правые вершины (слоты) по датам
    with dot.subgraph() as s:
        s.attr(rank='same')
        for day in work_days:
            day_label = day.date.isoformat()
            for room in rooms:
                for slot in day.available_slots:
                    node_id = f"{room.number}_{day.date}_{slot.number}"
                    s.node(node_id, f"{room.number}\n{slot.start_time}",
                        shape='ellipse', style='filled', fillcolor='lightblue')

    # Добавляем рёбра
    for event_id, slots in graph.items():
        for room_id, date_str, slot_id in slots:
            room = next((r for r in rooms if r.id == room_id), None)
            if room:
                dot.edge(f"E{event_id}", f"{room.number}_{date_str}_{slot_id}")

    dot.render(output_path, view=False)