"""Тесты для модуля assignment.py.

Проверяет решение задачи о назначениях:
- build_cost_matrix() — построение матрицы штрафов
- solve_assignment() — венгерский алгоритм
"""

import numpy as np
from src.assignment import build_cost_matrix, solve_assignment
from src.data_models import Group, Room, Event, TimeSlot, WorkDay


class TestBuildCostMatrix:
    """Тесты для функции build_cost_matrix()."""

    def test_build_cost_matrix_success(self, events_list, rooms_list, workday, groups_list):
        """Проверяет успешное построение матрицы штрафов."""
        from src.graph_builder import get_all_slots

        all_slots = get_all_slots(rooms_list, [workday])

        cost_matrix = build_cost_matrix(
            events=events_list,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms_list,
            alpha=1.0,
            beta=1000.0
        )

        assert cost_matrix is not None
        assert isinstance(cost_matrix, np.ndarray)

    def test_build_cost_matrix_shape(self, events_list, rooms_list, workday, groups_list):
        """Проверяет, что матрица имеет размерность |E| x (|C|*|T|)."""
        from src.graph_builder import get_all_slots

        all_slots = get_all_slots(rooms_list, [workday])
        n_events = len(events_list)
        n_slots = len(all_slots)

        cost_matrix = build_cost_matrix(
            events=events_list,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms_list
        )

        assert cost_matrix.shape == (n_events, n_slots)

    def test_build_cost_matrix_with_penalties(self, group, room, slot1, workday):
        """Проверяет, что штрафы за вместимость правильно вычисляются."""
        from src.graph_builder import get_all_slots

        groups = [group]
        rooms = [room]
        work_days = [workday]
        all_slots = get_all_slots(rooms, work_days)

        events = [
            Event(id=1, name="Тест", group_id=group.id, teacher_id=1,
                total_hours=1, required_features=[])
        ]

        cost_matrix = build_cost_matrix(
            events=events,
            all_slots=all_slots,
            groups=groups,
            rooms=rooms,
            alpha=1.0,
            beta=1000.0
        )

        # Штраф = |size - capacity| = |31 - 40| = 9
        expected_penalty = abs(group.size - room.capacity)
        assert cost_matrix[0, 0] == expected_penalty

    def test_build_cost_matrix_large_m_penalty(self, group, room_small, slot1, workday, groups_list):
        """Проверяет, что недопустимые назначения получают большой штраф M."""
        from src.graph_builder import get_all_slots

        # Событие с требованием, которого нет в аудитории
        event_with_req = Event(id=10, name="Требовательное", group_id=group.id,
            teacher_id=1, total_hours=1, required_features=["суперкомпьютер"])
        events = [event_with_req]

        rooms = [room_small]
        work_days = [workday]
        all_slots = get_all_slots(rooms, work_days)

        cost_matrix = build_cost_matrix(
            events=events,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms,
            M=1e6
        )

        # Недопустимое назначение должно получить штраф M
        assert cost_matrix[0, 0] == 1e6

    def test_build_cost_matrix_with_custom_alpha_beta(self, group, room, slot1, workday):
        """Проверяет, что коэффициенты alpha и beta влияют на штраф."""
        from src.graph_builder import get_all_slots

        groups = [group]
        rooms = [room]
        work_days = [workday]
        all_slots = get_all_slots(rooms, work_days)

        events = [
            Event(id=1, name="Тест", group_id=group.id, teacher_id=1,
                total_hours=1, required_features=[])
        ]

        size_penalty = abs(group.size - room.capacity)  # 31 - 40 = 9

        # alpha=2.0, штраф должен быть 2 * 9 = 18
        cost_matrix_alpha2 = build_cost_matrix(
            events=events,
            all_slots=all_slots,
            groups=groups,
            rooms=rooms,
            alpha=2.0,
            beta=1000.0
        )
        assert cost_matrix_alpha2[0, 0] == 18

        # alpha=0.5, штраф должен быть 0.5 * 9 = 4.5
        cost_matrix_alpha05 = build_cost_matrix(
            events=events,
            all_slots=all_slots,
            groups=groups,
            rooms=rooms,
            alpha=0.5,
            beta=1000.0
        )
        assert cost_matrix_alpha05[0, 0] == 4.5

    def test_build_cost_matrix_group_not_found(self, room, slot1, workday, groups_list):
        """Проверяет, что событие с несуществующей группой получает штраф M."""
        from src.graph_builder import get_all_slots

        events = [
            Event(id=99, name="Без группы", group_id=999, teacher_id=1,
                total_hours=1, required_features=[])
        ]

        rooms = [room]
        work_days = [workday]
        all_slots = get_all_slots(rooms, work_days)

        cost_matrix = build_cost_matrix(
            events=events,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms,
            M=1e6
        )

        assert cost_matrix[0, 0] == 1e6


class TestSolveAssignment:
    """Тесты для функции solve_assignment()."""

    def test_solve_assignment_success(self, events_list, rooms_list, workday, groups_list):
        """Проверяет успешное решение задачи о назначениях."""
        from src.graph_builder import get_all_slots

        all_slots = get_all_slots(rooms_list, [workday])

        cost_matrix = build_cost_matrix(
            events=events_list,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms_list
        )

        assignment = solve_assignment(cost_matrix, events_list, all_slots)

        assert len(assignment) == len(events_list)
        assert all(event.id in assignment for event in events_list)

    # def test_solve_assignment_empty(self):
    #     #     """Проверяет поведение при пустой матрице."""
    #     #     empty_matrix = np.array([])
    #     #     events = []
    #     #     all_slots = []
    #     #
    #     #     assignment = solve_assignment(empty_matrix, events, all_slots)
    #     #
    #     #     assert assignment == {}

    def test_solve_assignment_rectangular(self, events_list, rooms_list, workday, groups_list):
        """Проверяет решение для прямоугольной матрицы (больше слотов, чем событий)."""
        from src.graph_builder import get_all_slots

        all_slots = get_all_slots(rooms_list, [workday])
        events = events_list[:2]  # только 2 события, а слотов больше

        cost_matrix = build_cost_matrix(
            events=events,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms_list
        )

        assignment = solve_assignment(cost_matrix, events, all_slots)

        assert len(assignment) == len(events)

    def test_solve_assignment_returns_dict(self, events_list, rooms_list, workday, groups_list):
        """Проверяет, что возвращается словарь event_id -> slot_key."""
        from src.graph_builder import get_all_slots

        all_slots = get_all_slots(rooms_list, [workday])

        cost_matrix = build_cost_matrix(
            events=events_list,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms_list
        )

        assignment = solve_assignment(cost_matrix, events_list, all_slots)

        assert isinstance(assignment, dict)
        for event_id, slot in assignment.items():
            assert isinstance(event_id, int)
            assert isinstance(slot, tuple)
            assert len(slot) == 3  # (room_id, date_str, slot_id)

    def test_solve_assignment_no_feasible_solution(self, group, room_small, slot1, workday, groups_list):
        """Проверяет поведение при отсутствии допустимого решения."""
        from src.graph_builder import get_all_slots

        # Создаём событие, которое не может быть назначено ни в один слот
        impossible_event = Event(id=99, name="Невозможное", group_id=group.id,
            teacher_id=1, total_hours=1, required_features=["невозможное_оборудование"])
        events = [impossible_event]

        rooms = [room_small]
        work_days = [workday]
        all_slots = get_all_slots(rooms, work_days)

        cost_matrix = build_cost_matrix(
            events=events,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms,
            M=1e6
        )

        # Даже с M задача о назначениях найдет какое-то решение
        # (назначит в слот с минимальным штрафом, который может быть M)
        assignment = solve_assignment(cost_matrix, events, all_slots)

        assert len(assignment) == 1

    def test_solve_assignment_with_details(self, events_list, rooms_list, workday, groups_list):
        from src.graph_builder import get_all_slots
        from src.assignment import build_cost_matrix, solve_assignment, print_assignment_details

        all_slots = get_all_slots(rooms_list, [workday])

        alpha, beta = 1.0, 1000.0

        cost_matrix = build_cost_matrix(
            events=events_list,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms_list,
            alpha=alpha,
            beta=beta
        )

        assignment = solve_assignment(cost_matrix, events_list, all_slots)

        # Печатаем подробности
        print_assignment_details(
            assignment=assignment,
            cost_matrix=cost_matrix,
            events=events_list,
            all_slots=all_slots,
            groups=groups_list,
            rooms=rooms_list,
            alpha=alpha,
            beta=beta
        )

        assert len(assignment) == len(events_list)
