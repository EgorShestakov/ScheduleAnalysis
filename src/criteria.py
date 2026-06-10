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


def criterion_two(graph: Dict[int, List[Any]], events: List[Any], rooms: List[Any], groups: List[Any]) -> Tuple[
    bool, List[int]]:
    """
    Проверяет наличие изолированных событий.
    Возвращает (успех, список id изолированных событий).
    При наличии изолированных строит таблицу причин конфликтов.

    :param graph: словарь смежности {event_id: [(room_id, date, slot_id), ...]}
    :param events: список событий
    :param rooms: список аудиторий
    :param groups: список групп
    :return: (True, []) если нет изолированных, (False, list_of_ids) если есть
    """
    isolated_events = []
    for event in events:
        if event.id not in graph or len(graph.get(event.id, [])) == 0:
            isolated_events.append(event)

    if not isolated_events:
        return True, []

    # Преобразуем список групп в словарь для быстрого доступа
    group_by_id = {group.id: group for group in groups}

    # Строим таблицу причин конфликтов
    print(f"\n{'=' * 140}")
    print(f"ВТОРОЙ КРИТЕРИЙ НАРУШЕН")
    print(f"Найдено изолированных событий: {len(isolated_events)}")
    print(f"{'=' * 140}\n")

    # Таблица причин конфликтов
    print("ТАБЛИЦА ПРИЧИН КОНФЛИКТОВ")
    print("-" * 140)
    print(
        f"{'Событие':<20} | {'Требуемое оснащение':<20} | {'Группа':<15} | {'Численность':<10} | {'Аудитория':<12} | {'Оснащение аудитории':<25} | {'Вместимость':<10} | {'Причина'}")
    print("-" * 140)

    for event in isolated_events:
        group = group_by_id.get(event.group_id)
        if group is None:
            print(
                f"{event.name:<20} | {'N/A':<20} | {'N/A':<15} | {'N/A':<10} | {'N/A':<12} | {'N/A':<25} | {'N/A':<10} | Группа не найдена")
            continue

        event_features = ', '.join(event.required_features) if event.required_features else "нет"
        group_name = repr(group)  # используем __repr__ для названия группы
        group_size = group.size

        for room in rooms:
            capacity_ok = group.size <= room.capacity
            equipment_ok = set(event.required_features).issubset(set(room.equipment))

            # Если оба условия выполнены, ребро должно было быть в графе
            # Это означает, что проблема не в ограничениях, а в отсутствии временных слотов
            if capacity_ok and equipment_ok:
                continue

            reasons = []
            if not capacity_ok:
                reasons.append(f"не хватает {group.size - room.capacity} мест")
            if not equipment_ok:
                missing = set(event.required_features) - set(room.equipment)
                reasons.append(f"нет: {', '.join(missing)}")

            room_features = ', '.join(room.equipment) if room.equipment else "нет"

            print(
                f"{event.name:<20} | {event_features:<20} | {group_name:<15} | {group_size:<10} | каб.{room.number:<9} | {room_features:<25} | {room.capacity:<10} | {', '.join(reasons)}")

    print("-" * 140)
    print(f"\nРЕКОМЕНДАЦИИ ДЛЯ УСТРАНЕНИЯ ИЗОЛИРОВАННЫХ СОБЫТИЙ:")
    print("  1. Добавить недостающее оборудование в указанные аудитории")
    print("  2. Увеличить вместимость указанных аудиторий")
    print("  3. Исключить события из расписания или перенести их на другие дни/временные слоты")
    print(f"{'=' * 140}\n")

    return False, [event.id for event in isolated_events]