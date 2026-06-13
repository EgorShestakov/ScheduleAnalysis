"""Построение двудольного графа событие -> слот."""

from typing import List, Tuple, Dict
from collections import defaultdict
from src.data_models import Event, Room, WorkDay, Group, Teacher
from graphviz import Digraph
import networkx as nx
import matplotlib.pyplot as plt


def get_all_slots_for_day(rooms: List[Room], work_day: WorkDay) -> List[Tuple[int, int]]:
    """Возвращает список всех слотов (room_id, slot_id) для одного дня."""
    slots = []
    for room in rooms:
        for slot in work_day.available_slots:
            slots.append((room.id, slot.id))
    return slots


def build_bipartite_graph(events: List[Event], rooms: List[Room], work_day: WorkDay,
                          groups: List[Group], check_capacity: bool = True,
                          check_equipment: bool = True) -> Dict[int, List[Tuple[int, int]]]:
    """
    Строит двудольный граф для ОДНОГО дня.
    Возвращает словарь смежности: event_id -> list[(room_id, slot_id)].
    """
    all_slots = get_all_slots_for_day(rooms, work_day)  # список (room_id, slot_id)

    group_by_id = {g.id: g for g in groups}
    room_capacity = {r.id: r.capacity for r in rooms}
    room_equipment = {r.id: set(r.equipment) for r in rooms}

    graph = defaultdict(list)

    for event in events:
        group = group_by_id.get(event.group_id)
        if group is None:
            continue

        event_requirements = set(event.required_features)

        for room_id, slot_id in all_slots:
            if check_capacity and group.size > room_capacity[room_id]:
                continue
            if check_equipment and not event_requirements.issubset(room_equipment[room_id]):
                continue
            graph[event.id].append((room_id, slot_id))

    return dict(graph)


def visualize_bipartite_graph(graph, events, rooms, work_day, matching=None, output_path="graph.png"):
    """
    Визуализирует двудольный граф для ОДНОГО дня.
    Левые вершины (события) — красные, правые (слоты) — синие.
    Вершины расположены на двух параллельных линиях в строгом порядке.

    :param graph: словарь смежности {event_id: [(room_id, slot_id), ...]}
    :param events: список событий
    :param rooms: список аудиторий
    :param work_day: рабочий день (объект WorkDay)
    :param matching: опциональный словарь {event_id: (room_id, slot_id)} для выделения рёбер паросочетания
    :param output_path: путь для сохранения
    """
    import matplotlib.pyplot as plt
    import networkx as nx

    G = nx.DiGraph()

    # Сортируем события по id для фиксированного порядка
    sorted_events = sorted(events, key=lambda e: e.id)

    # Добавляем вершины левой доли (события)
    for event in sorted_events:
        label = event.name[:15]
        G.add_node(f"E{event.id}", bipartite=0, label=label)

    # Сортируем слоты для одного дня
    all_slots = []
    date_str = work_day.date.isoformat()
    sorted_rooms = sorted(rooms, key=lambda r: r.number)

    for room in sorted_rooms:
        for slot in sorted(work_day.available_slots, key=lambda s: s.number):
            label = f"{date_str}\nкаб.{room.number}\n{slot.start_time}-{slot.end_time}"
            node_id = f"{room.number}_{slot.number}"
            all_slots.append((node_id, label))
            G.add_node(node_id, bipartite=1, label=label)

    # Добавляем рёбра
    for event_id, slots in graph.items():
        for room_id, slot_id in slots:
            room = next((r for r in rooms if r.id == room_id), None)
            if room:
                node_id = f"{room.number}_{slot_id}"
                G.add_edge(f"E{event_id}", node_id)

    # Получаем списки вершин
    left_nodes = [f"E{event.id}" for event in sorted_events]
    right_nodes = [node_id for node_id, _ in all_slots]

    # Задаём координаты
    left_step = 2.5
    right_step = 2.2
    top_margin = 3.0

    pos = {}
    for i, node in enumerate(left_nodes):
        pos[node] = (0, -i * left_step + top_margin)
    for i, node in enumerate(right_nodes):
        pos[node] = (3.5, -i * right_step + top_margin)

    # Рисуем граф
    fig_height = max(len(left_nodes), len(right_nodes)) * 1.2 + 7
    plt.figure(figsize=(16, fig_height))

    nx.draw_networkx_nodes(G, pos, nodelist=left_nodes,
        node_color='red', node_size=3000, alpha=0.85,
        linewidths=1.5, edgecolors='black')
    nx.draw_networkx_nodes(G, pos, nodelist=right_nodes,
        node_color='lightblue', node_size=4000, alpha=0.85,
        linewidths=1.5, edgecolors='black')

    # Рисуем все рёбра серым цветом
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.4,
        arrows=True, arrowsize=10, width=1.0)

    # Если передано паросочетание, рисуем его рёбра красным цветом поверх
    if matching:
        matching_edges = []
        for event_id, (room_id, slot_id) in matching.items():
            room = next((r for r in rooms if r.id == room_id), None)
            if room:
                node_id = f"{room.number}_{slot_id}"
                matching_edges.append((f"E{event_id}", node_id))

        nx.draw_networkx_edges(G, pos, edgelist=matching_edges, edge_color='red', alpha=1.0,
            arrows=True, arrowsize=12, width=2.5)

    # Рисуем метки
    labels = {n: G.nodes[n]['label'] for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')

    plt.title("Двудольный граф событий и слотов", fontsize=14, fontweight='bold', pad=20)

    legend = plt.legend(
        ['События', 'Слоты'],
        loc='upper left',
        fontsize=12,
        bbox_to_anchor=(1.02, 0.9),
        frameon=True,
        fancybox=True,
        shadow=True,
        handlelength=2,
        handletextpad=1.5,
        labelspacing=2,
        markerscale=0.3
    )

    plt.axis('off')
    plt.subplots_adjust(left=0.05, right=0.85, top=0.95, bottom=0.05)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()


def get_all_teacher_slots(teachers: List[Teacher], time_slots: List[int]) -> List[Tuple[int, int]]:
    """
    Возвращает список всех возможных слотов (teacher_id, time_slot).

    :param teachers: список преподавателей
    :param time_slots: список доступных временных интервалов (номера пар)
    :return: список кортежей (teacher_id, t)
    """
    slots = []
    for teacher in teachers:
        for t in time_slots:
            slots.append((teacher.id, t))
    return slots


def build_teacher_bipartite_graph(events: List[Event], teachers: List[Teacher],
                                  time_slots: List[int], check_time: bool = True,
                                  check_specialization: bool = True) -> Dict[int, List[Tuple[int, int]]]:
    """
    Строит двудольный граф H_teacher = (E, P×T, R_teacher).
    Возвращает словарь смежности: event_id -> list[(teacher_id, t)].
    """
    all_slots = get_all_teacher_slots(teachers, time_slots)
    teacher_specialization = {teacher.id: set(teacher.specialization) for teacher in teachers}

    graph = defaultdict(list)

    for event in events:
        event_time = event.time if hasattr(event, 'time') else None

        for teacher_id, t in all_slots:
            # Проверка временного ограничения
            if check_time:
                if event_time is None or t != event_time:
                    continue

            # Проверка специализации
            if check_specialization and event.name not in teacher_specialization.get(teacher_id, set()):
                continue

            graph[event.id].append((teacher_id, t))

    return dict(graph)


def visualize_teacher_bipartite_graph(graph, events, teachers, time_slots, matching=None,
                                      output_path="teacher_graph.png"):
    """
    Визуализирует двудольный граф преподавателей.
    Левые вершины (события) — красные, правые (преподаватель, время) — синие.

    :param graph: словарь смежности {event_id: [(teacher_id, t), ...]}
    :param events: список событий
    :param teachers: список преподавателей
    :param time_slots: список временных интервалов
    :param matching: опциональный словарь {event_id: (teacher_id, t)} для выделения рёбер паросочетания
    :param output_path: путь для сохранения
    """
    import matplotlib.pyplot as plt
    import networkx as nx

    G = nx.DiGraph()

    # Сортируем события по id для фиксированного порядка
    sorted_events = sorted(events, key=lambda e: e.id)

    # Добавляем вершины левой доли (события)
    for event in sorted_events:
        label = f"{event.name[:12]}\n(t={event.time if hasattr(event, 'time') and event.time else '?'})"
        G.add_node(f"E{event.id}", bipartite=0, label=label)

    # Добавляем вершины правой доли (преподаватель, время)
    teacher_by_id = {t.id: t for t in teachers}
    sorted_teachers = sorted(teachers, key=lambda t: t.id)
    sorted_time_slots = sorted(time_slots)

    all_slots = []
    for teacher in sorted_teachers:
        for t in sorted_time_slots:
            node_id = f"P{teacher.id}_{t}"
            label = f"{teacher.surname}\n{t}-я пара"
            all_slots.append((node_id, label))
            G.add_node(node_id, bipartite=1, label=label)

    # Добавляем рёбра
    for event_id, slots in graph.items():
        for teacher_id, t in slots:
            node_id = f"P{teacher_id}_{t}"
            G.add_edge(f"E{event_id}", node_id)

    # Получаем списки вершин
    left_nodes = [f"E{event.id}" for event in sorted_events]
    right_nodes = [node_id for node_id, _ in all_slots]

    # Задаём координаты
    left_step = 2.5
    right_step = 2.2
    top_margin = 3.0

    pos = {}
    for i, node in enumerate(left_nodes):
        pos[node] = (0, -i * left_step + top_margin)
    for i, node in enumerate(right_nodes):
        pos[node] = (3.5, -i * right_step + top_margin)

    # Рисуем граф
    fig_height = max(len(left_nodes), len(right_nodes)) * 1.2 + 7
    plt.figure(figsize=(16, fig_height))

    nx.draw_networkx_nodes(G, pos, nodelist=left_nodes,
        node_color='red', node_size=3000, alpha=0.85,
        linewidths=1.5, edgecolors='black')
    nx.draw_networkx_nodes(G, pos, nodelist=right_nodes,
        node_color='lightblue', node_size=3500, alpha=0.85,
        linewidths=1.5, edgecolors='black')

    # Рисуем все рёбра серым цветом
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.4,
        arrows=True, arrowsize=10, width=1.0)

    # Если передано паросочетание, рисуем его рёбра красным цветом поверх
    if matching:
        matching_edges = []
        for event_id, (teacher_id, t) in matching.items():
            node_id = f"P{teacher_id}_{t}"
            matching_edges.append((f"E{event_id}", node_id))

        nx.draw_networkx_edges(G, pos, edgelist=matching_edges, edge_color='red', alpha=1.0,
            arrows=True, arrowsize=12, width=2.5)

    # Рисуем метки
    labels = {n: G.nodes[n]['label'] for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')

    plt.title("Двудольный граф преподавателей (события → преподаватель, время)",
        fontsize=14, fontweight='bold', pad=20)

    legend = plt.legend(
        ['События', 'Преподаватели'],
        loc='upper left',
        fontsize=12,
        bbox_to_anchor=(1.02, 0.9),
        frameon=True,
        fancybox=True,
        shadow=True,
        handlelength=2,
        handletextpad=1.5,
        labelspacing=2,
        markerscale=0.3
    )

    plt.axis('off')
    plt.subplots_adjust(left=0.05, right=0.85, top=0.95, bottom=0.05)
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