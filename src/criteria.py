"""Проверка критериев существования расписания."""

from typing import Tuple, List, Dict, Any
from collections import defaultdict


def criterion_one(events: List[Any], rooms: List[Any], work_days: List[Any]) -> bool:
    """
    Проверяет первый критерий |E| <= |C|·|T|.
    При нарушении выводит количественные рекомендации.

    :param events: список событий
    :param rooms: список аудиторий
    :param work_days: список рабочих дней (для определения |T|)
    :return: True если критерий выполнен, False если нарушен
    """
    num_events = len(events)
    num_rooms = len(rooms)

    # Вычисляем общее количество временных слотов |T|
    # Суммируем количество слотов по всем рабочим дням
    num_slots = sum(len(day.available_slots) for day in work_days)

    total_slots = num_rooms * num_slots

    if num_events <= total_slots:
        return True

    # Критерий нарушен
    diff = num_events - total_slots

    print(f"\n{'='*60}")
    print(f"ПЕРВЫЙ КРИТЕРИЙ НАРУШЕН")
    print(f"{'='*60}")
    print(f"|E| = {num_events} событий")
    print(f"|C|·|T| = {num_rooms} × {num_slots} = {total_slots} слотов")
    print(f"Превышение: {diff} слотов")

    if 0 in (num_events, num_rooms, num_slots):
        print(f"\nНУЛЕЙ НЕ МОЖЕТ БЫТЬ!")
    else:
        print(f"\nРЕКОМЕНДАЦИИ:")
        print(f"  1. Убрать как минимум {diff} событий из рассмотрения")
        print(f"  2. Увеличить количество аудиторий на {num_events // num_slots - num_rooms}")
        print(f"  3. Увеличить количество временных слотов на {num_events // num_rooms - num_slots}")
        print(f"{'='*60}\n")

    return False


def criterion_two(graph: Dict[int, List[Any]], events: List[Any]) -> Tuple[bool, List[int]]:
    """
    Проверяет наличие изолированных событий.
    Возвращает (успех, список id изолированных событий).
    При наличии изолированных строит таблицу причин конфликтов.

    :param graph: словарь смежности {event_id: [(room_id, date, slot_id), ...]}
    :param events: список событий
    :return: (True, []) если нет изолированных, (False, list_of_ids) если есть
    """
    isolated_events = []
    for event in events:
        if event.id not in graph or len(graph.get(event.id, [])) == 0:
            isolated_events.append(event.id)

    if not isolated_events:
        return True, []

    # Строим таблицу причин конфликтов
    print(f"\n{'='*60}")
    print(f"ВТОРОЙ КРИТЕРИЙ НАРУШЕН")
    print(f"Найдены изолированные события: {isolated_events}")
    print(f"{'='*60}\n")

    # Здесь мы не можем вывести таблицу без информации о комнатах и группах
    # Поэтому просто выводим сообщение и возвращаем список
    # Фактическая таблица причин должна строиться с дополнительными параметрами

    return False, isolated_events