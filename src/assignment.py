"""Решение задачи о назначениях (венгерский алгоритм)."""

import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import Dict

def build_cost_matrix(events, slots, groups, rooms, alpha, beta, gamma) -> np.array:
    """Строит матрицу штрафов размера |E| × (|C|·|T|)."""
    pass

def solve_assignment(cost_matrix, events, slots) -> Dict:
    """
    Решает задачу о назначениях.
    Возвращает словарь event_id -> slot_key.
    """
    pass
