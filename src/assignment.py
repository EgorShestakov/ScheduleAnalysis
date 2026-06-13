"""Решение задачи о назначениях (венгерский алгоритм)."""

import numpy as np
from scipy.optimize import linear_sum_assignment, milp, LinearConstraint, Bounds
from typing import Dict, List, Tuple, Any
from src.data_models import Event


def build_cost_matrix(events: List[Any], all_slots: List[Tuple], groups: List[Any], rooms: List[Any],
                      alpha: float = 1.0, beta: float = 1000.0, M: float = 1e6) -> np.ndarray:
    """
    Строит матрицу штрафов размера |E| × (|C|·|T|).

    Для каждого события e и каждого слота (c, t) вычисляется штраф:
        w = alpha * |s(e) - cap(c)| + beta * eq_penalty
    где eq_penalty = 0, если оборудование подходит, иначе M.

    :param events: список событий
    :param all_slots: список всех слотов (room_id, date_str, slot_id)
    :param groups: список групп
    :param rooms: список аудиторий
    :param alpha: коэффициент штрафа за несоответствие вместимости
    :param beta: коэффициент штрафа за отсутствие оборудования
    :param M: большое число (штраф за недопустимое назначение)
    :return: матрица штрафов numpy array
    """
    # Создаём словари для быстрого доступа
    group_by_id = {g.id: g for g in groups}
    room_by_id = {r.id: r for r in rooms}

    n_events = len(events)
    n_slots = len(all_slots)

    # Инициализируем матрицу большим числом (все назначения запрещены)
    cost_matrix = np.full((n_events, n_slots), M, dtype=np.float64)

    # Словарь для отображения события -> индекс в матрице
    event_to_idx = {event.id: i for i, event in enumerate(events)}

    # Строим матрицу штрафов
    for event in events:
        group = group_by_id.get(event.group_id)
        if group is None:
            continue  # группа не найдена, оставляем M

        event_idx = event_to_idx[event.id]
        event_req = set(event.required_features)

        for slot_idx, (room_id, date_str, slot_id) in enumerate(all_slots):
            room = room_by_id.get(room_id)
            if room is None:
                continue

            # Проверка оборудования
            equipment_ok = event_req.issubset(set(room.equipment))
            if not equipment_ok:
                continue  # оставляем M (недопустимо)

            # Вычисляем штраф за несоответствие вместимости
            size_penalty = abs(group.size - room.capacity)

            # Итоговый штраф
            w = alpha * size_penalty  # beta * eq_penalty = 0, так как оборудование подходит

            cost_matrix[event_idx, slot_idx] = w

    return cost_matrix


def solve_assignment(cost_matrix, events, all_slots):
    """
    Решает задачу о назначениях с ограничением (4.4).
    """
    n_events = len(events)
    n_slots = len(all_slots)
    n_vars = n_events * n_slots

    # Целевая функция
    c = cost_matrix.flatten()

    # Ограничения (4.1): каждое событие — ровно один слот
    A_eq = []
    b_eq = []
    for e in range(n_events):
        row = np.zeros(n_vars)
        row[e * n_slots:(e + 1) * n_slots] = 1
        A_eq.append(row)
        b_eq.append(1)

    # Ограничения (4.2): каждый слот — не более одного события
    for s in range(n_slots):
        row = np.zeros(n_vars)
        row[s::n_slots] = 1
        A_eq.append(row)  # тоже равенство, потому что должно быть <= 1? Нет, это неравенство
        b_eq.append(1)
    # НО! Это неравенство (<= 1), а не равенство. Нужно использовать A_ub.

    # Правильно: (4.2) — неравенство sum <= 1
    A_ub = []
    b_ub = []
    for s in range(n_slots):
        row = np.zeros(n_vars)
        row[s::n_slots] = 1
        A_ub.append(row)
        b_ub.append(1)

    # (4.1) — равенство sum = 1
    A_eq = []
    b_eq = []
    for e in range(n_events):
        row = np.zeros(n_vars)
        row[e * n_slots:(e + 1) * n_slots] = 1
        A_eq.append(row)
        b_eq.append(1)

    # Ограничение (4.4): одна группа в одном временном слоте — не более одного события
    from collections import defaultdict
    group_time_events = defaultdict(list)
    for i, event in enumerate(events):
        for j, slot in enumerate(all_slots):
            room_id, date_str, slot_id = slot
            group_time_events[(event.group_id, date_str, slot_id)].append((i, j))

    for (group_id, date_str, slot_id), event_slot_pairs in group_time_events.items():
        if len(event_slot_pairs) > 1:
            row = np.zeros(n_vars)
            for i, j in event_slot_pairs:
                row[i * n_slots + j] = 1
            A_ub.append(row)
            b_ub.append(1)

    # Целочисленность
    integrality = np.ones(n_vars, dtype=np.uint8)

    # Границы переменных (0 или 1)
    bounds = Bounds(lb=0, ub=1)

    # Решение
    result = milp(c=c, constraints=LinearConstraint(A_eq, b_eq, b_eq),
                  integrality=integrality, bounds=bounds)

    if result is None or result.status != 0:
        print(f"Решение не найдено. Статус: {result.status if result else 'None'}")
        return {}

    # Извлекаем решение
    assignment = {}
    for e in range(n_events):
        for s in range(n_slots):
            if result.x[e * n_slots + s] > 0.5:
                assignment[events[e].id] = all_slots[s]
                break

    return assignment


def print_assignment_details(assignment: Dict[int, Tuple], cost_matrix: np.ndarray,
                             events: List[Any], all_slots: List[Tuple],
                             groups: List[Any], rooms: List[Any],
                             alpha: float = 1.0, beta: float = 1000.0):
    """
    Печатает подробную информацию о назначении:
    - какие события назначены в какие слоты
    - какой штраф за каждое назначение и из чего он складывается
    - суммарный штраф
    """
    group_by_id = {g.id: g for g in groups}
    room_by_id = {r.id: r for r in rooms}

    # Сопоставляем индексы событий и слотов
    event_to_idx = {e.id: i for i, e in enumerate(events)}
    slot_to_idx = {slot: i for i, slot in enumerate(all_slots)}

    total_penalty = 0
    total_size_penalty = 0
    total_eq_penalty = 0

    print("\n" + "=" * 100)
    print("РЕЗУЛЬТАТ РЕШЕНИЯ ЗАДАЧИ О НАЗНАЧЕНИЯХ")
    print("=" * 100)

    for event_id, slot in assignment.items():
        event = next(e for e in events if e.id == event_id)
        group = group_by_id[event.group_id]
        room_id, date_str, slot_id = slot
        room = room_by_id[room_id]

        # Получаем штраф из матрицы
        i = event_to_idx[event_id]
        j = slot_to_idx[slot]
        total = cost_matrix[i, j]

        # Вычисляем составляющие
        size_penalty = abs(group.size - room.capacity)
        equipment_ok = set(event.required_features).issubset(set(room.equipment))
        eq_penalty = 0 if equipment_ok else 1e6

        # С учётом коэффициентов (если они отличаются от 1)
        actual_size_penalty = alpha * size_penalty
        actual_eq_penalty = beta * eq_penalty if not equipment_ok else 0

        total_penalty += total
        total_size_penalty += actual_size_penalty
        total_eq_penalty += actual_eq_penalty

        print(f"\n{event.name} (группа {group}, {group.size} чел)")
        print(f"  -> каб.{room.number} (вместимость {room.capacity}, оснащение: {room.equipment or 'нет'})")
        print(f"     дата: {date_str}, слот: {slot_id}")
        print(f"  Штраф: {total:.2f}")
        print(
            f"    - за вместимость: {actual_size_penalty:.2f} (|{group.size} - {room.capacity}| = {size_penalty}) × α={alpha}")
        if not equipment_ok:
            missing = set(event.required_features) - set(room.equipment)
            print(f"    - за оборудование: {actual_eq_penalty:.2f} (нет: {', '.join(missing)}) × β={beta}")
        else:
            print(f"    - за оборудование: 0 (всё есть)")

    print("\n" + "-" * 100)
    print(f"ИТОГОВЫЙ ШТРАФ: {total_penalty:.2f}")
    print(f"  из них за вместимость: {total_size_penalty:.2f}")
    print(f"  за оборудование: {total_eq_penalty:.2f}")
    print("=" * 100 + "\n")