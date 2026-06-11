"""Вывод расписания и рекомендаций."""
import csv
from typing import List, Dict, Tuple, Any


def print_schedule(assignment: Dict[int, Tuple], events: List[Any], rooms: List[Any],
                   groups: List[Any], teachers: List[Any], work_days: List[Any]) -> None:
    """
    Печатает расписание в консоль.
    """
    event_by_id = {e.id: e for e in events}
    room_by_id = {r.id: r for r in rooms}
    group_by_id = {g.id: g for g in groups}
    teacher_by_id = {t.id: t for t in teachers}

    slot_by_id = {}
    for day in work_days:
        for slot in day.available_slots:
            slot_by_id[slot.id] = slot

    schedule = {}

    for event_id, (room_id, date_str, slot_id) in assignment.items():
        event = event_by_id[event_id]
        group = group_by_id[event.group_id]
        room = room_by_id[room_id]
        teacher = teacher_by_id.get(event.teacher_id)
        slot = slot_by_id.get(slot_id)

        if slot is None:
            continue

        if date_str not in schedule:
            schedule[date_str] = {}
        if slot_id not in schedule[date_str]:
            schedule[date_str][slot_id] = []

        schedule[date_str][slot_id].append({
            "event": event.name,
            "group": group,
            "room": room.number,
            "teacher": teacher.full_name() if teacher else "Не назначен",
            "size": group.size,
            "capacity": room.capacity,
            "start_time": slot.start_time,
            "end_time": slot.end_time
        })

    print("\n" + "=" * 120)
    print("РАСПИСАНИЕ ЗАНЯТИЙ")
    print("=" * 120)

    for date_str in sorted(schedule.keys()):
        print(f"\nДата: {date_str}")
        print("-" * 100)

        for slot_id in sorted(schedule[date_str].keys()):
            items = schedule[date_str][slot_id]
            slot_info = f"Пара {slot_id} ({items[0]['start_time']} - {items[0]['end_time']})"
            print(f"\n  {slot_info}:")
            for item in items:
                print(f"    - {item['event']} | {item['group']} | каб.{item['room']} | {item['teacher']} "
                      f"(вместимость: {item['capacity']}, студентов: {item['size']})")

    print("\n" + "=" * 120 + "\n")


def prepare_schedule_rows(assignment: Dict[int, Tuple], events: List[Any], rooms: List[Any],
                          teachers: List[Any], work_days: List[Any]) -> List[Dict]:
    """
    Формирует список строк для CSV-экспорта.

    :param assignment: словарь {event_id: (room_id, date_str, slot_id)}
    :param events: список событий
    :param rooms: список аудиторий
    :param teachers: список преподавателей
    :param work_days: список рабочих дней
    :return: список словарей для CSV
    """
    event_by_id = {e.id: e for e in events}
    room_by_id = {r.id: r for r in rooms}
    teacher_by_id = {t.id: t for t in teachers}

    # Группируем для удобства (может понадобиться, если два события в один слот — ошибка)
    rows = []

    for event_id, (room_id, date_str, slot_id) in assignment.items():
        event = event_by_id[event_id]
        room = room_by_id[room_id]
        teacher = teacher_by_id.get(event.teacher_id)

        row = {
            "date": date_str,
            "slot_number": slot_id,
            "event_name": event.name,
            "room_number": room.number,
            "teacher_name": teacher.full_name() if teacher else "Не назначен",
            "group_id": event.group_id,
            "room_capacity": room.capacity,
            "conflict": ""  # можно заполнить позже, если есть мнимые конфликты
        }
        rows.append(row)

    # Сортируем по дате, затем по слоту
    rows.sort(key=lambda x: (x["date"], x["slot_number"]))

    return rows


def write_schedule_to_csv(assignment: Dict[int, Tuple], events: List[Any], rooms: List[Any],
                          teachers: List[Any], work_days: List[Any], output_path: str) -> None:
    """
    Сохраняет расписание в CSV-файл.
    """
    rows = prepare_schedule_rows(assignment, events, rooms, teachers, work_days)

    if not rows:
        print("Нет данных для сохранения")
        return

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["date", "slot_number", "event_name", "room_number",
                      "teacher_name", "group_id", "room_capacity", "conflict"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Расписание сохранено в {output_path}")