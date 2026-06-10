"""Решение задачи о назначениях (венгерский алгоритм)."""

import numpy as np
from scipy.optimize import linear_sum_assignment
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


def solve_assignment(cost_matrix: np.ndarray, events: List[Any], all_slots: List[Tuple]) -> Dict[int, Tuple]:
    """
    Решает задачу о назначениях с помощью венгерского алгоритма.
    """
    # Проверка на пустую матрицу
    if cost_matrix.size == 0:
        return {}

    # Приводим к двумерному виду, если матрица одномерная
    if cost_matrix.ndim == 1:
        cost_matrix = cost_matrix.reshape(1, -1)

    # Если матрица не квадратная, linear_sum_assignment сам добавит фиктивные элементы
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    assignment = {}
    for i, j in zip(row_ind, col_ind):
        # Проверяем границы индексов
        if i < len(events) and j < len(all_slots):
            assignment[events[i].id] = all_slots[j]

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