"""Главный модуль оркестрации."""

import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Tuple

from src.data_loader import load_all
from src.criteria import criterion_one, criterion_two, criterion_three, criterion_four
from src.matching import max_bipartite_matching, is_perfect
from src.assignment import build_cost_matrix, solve_assignment, print_assignment_details
from src.graph_builder import build_bipartite_graph, get_all_slots_for_day
from src.flow_filter import build_flow_network, max_flow_dinic, filter_slots_by_flow
from src.output import print_schedule, write_schedule_to_csv

OUTPUT_DIR = Path("data/output")


def get_user_choice(prompt: str, options: List[str]) -> str:
    """Выводит меню и возвращает выбор пользователя."""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            choice = input("Выберите действие: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                print(f"Введите число от 1 до {len(options)}")
        except ValueError:
            print("Введите число")


def export_students_schedule(all_assignments: Dict[str, Dict[int, Tuple]],
                             events: List, groups: List, rooms: List,
                             work_days: List, time_slots: List, output_path: Path):
    """
    Экспортирует расписание для студентов.
    all_assignments: {date_str: {event_id: (room_id, slot_id)}}
    """
    event_by_id = {e.id: e for e in events}
    group_by_id = {g.id: g for g in groups}
    room_by_id = {r.id: r for r in rooms}
    slot_by_id = {s.id: s for s in time_slots}

    schedule = defaultdict(lambda: defaultdict(dict))

    for date_str, day_assignment in all_assignments.items():
        for event_id, (room_id, slot_id) in day_assignment.items():
            event = event_by_id[event_id]
            group_id = event.group_id
            room = room_by_id.get(room_id)
            slot = slot_by_id.get(slot_id)
            if slot and room:
                # Формат: "Название события (каб.XXX)"
                event_with_room = f"{event.name} (каб.{room.number})"
                schedule[group_id][date_str][slot.number] = event_with_room

    all_dates = [day.date.isoformat() for day in work_days
                 if day.day_type == "учебный" and not day.is_holiday]

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "students_schedule.csv"

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        # Сортируем группы по id для стабильного порядка
        for group in sorted(groups, key=lambda g: g.id):
            group_name = f"{group.course}-{group.department}-{group.number}"

            # Получаем расписание для этой группы
            date_slots = schedule.get(group.id, {})

            writer.writerow([])
            writer.writerow([group_name])

            dates_row = [""]
            for d in all_dates:
                dates_row.append(d)
            writer.writerow(dates_row)

            for slot_num in range(1, 8):
                row = [str(slot_num)]
                for d in all_dates:
                    event_name = date_slots.get(d, {}).get(slot_num, "")
                    row.append(event_name)
                writer.writerow(row)

    print(f"   Расписание для студентов сохранено в {output_file}")


def export_teachers_schedule(all_assignments: Dict[str, Dict[int, Tuple]],
                             events: List, teachers: List, rooms: List,
                             work_days: List, time_slots: List, output_path: Path):
    """
    Экспортирует расписание для преподавателей.
    all_assignments: {date_str: {event_id: (room_id, slot_id)}}
    """
    event_by_id = {e.id: e for e in events}
    teacher_by_id = {t.id: t for t in teachers}
    room_by_id = {r.id: r for r in rooms}
    slot_by_id = {s.id: s for s in time_slots}

    schedule = defaultdict(lambda: defaultdict(dict))

    for date_str, day_assignment in all_assignments.items():
        for event_id, (room_id, slot_id) in day_assignment.items():
            event = event_by_id[event_id]
            teacher_id = event.teacher_id
            room = room_by_id.get(room_id)
            slot = slot_by_id.get(slot_id)
            if teacher_id and slot and room:
                event_with_room = f"{event.name} (каб.{room.number})"
                schedule[teacher_id][date_str][slot.number] = event_with_room

    all_dates = [day.date.isoformat() for day in work_days
                 if day.day_type == "учебный" and not day.is_holiday]

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "teachers_schedule.csv"

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        # Сортируем преподавателей по id для стабильного порядка
        for teacher in sorted(teachers, key=lambda t: t.id):
            teacher_name = teacher.full_name()

            # Получаем расписание для этого преподавателя
            date_slots = schedule.get(teacher.id, {})

            writer.writerow([])
            writer.writerow([teacher_name])

            dates_row = [""]
            for d in all_dates:
                dates_row.append(d)
            writer.writerow(dates_row)

            for slot_num in range(1, 8):
                row = [str(slot_num)]
                for d in all_dates:
                    event_name = date_slots.get(d, {}).get(slot_num, "")
                    row.append(event_name)
                writer.writerow(row)

    print(f"   Расписание для преподавателей сохранено в {output_file}")


def build_schedule_for_day(events: List, rooms: List, work_day, groups: List,
                           teachers: List, time_slots: List, verbose: bool = False) -> Tuple[bool, Dict]:
    """
    Строит расписание для одного дня.
    Возвращает (успех, assignment).
    """
    # Построение двудольного графа для этого дня
    graph = build_bipartite_graph(
        events=events,
        rooms=rooms,
        work_day=work_day,
        groups=groups,
        check_capacity=True,
        check_equipment=True
    )

    if verbose:
        print(f"   Граф построен. Рёбер: {sum(len(v) for v in graph.values())}")

    # Проверка второго критерия (изолированные события)
    success_two, isolated_ids = criterion_two(graph, events, rooms, groups)
    if not success_two:
        if verbose:
            print(f"   ⚠️ Второй критерий не выполнен: изолированные события {isolated_ids}")
        return False, {}

    # Проверка третьего критерия (совершенное паросочетание)
    perfect, matching = criterion_three(graph, events)

    if not perfect:
        if verbose:
            print(f"   ❌ Совершенное паросочетание не найдено")
        return False, {}

    # Проверка четвёртого критерия (мнимые расписания)
    if not criterion_four(matching, events):
        if verbose:
            print(f"   ⚠️ Обнаружены мнимые конфликты")
        # Пытаемся решить задачу о назначениях
        all_slots = get_all_slots_for_day(rooms, work_day)
        cost_matrix = build_cost_matrix(events, all_slots, groups, rooms)
        assignment = solve_assignment(cost_matrix, events, all_slots)
        if assignment and criterion_four(assignment, events):
            if verbose:
                print(f"   ✅ Задача о назначениях успешно решена")
            return True, assignment
        else:
            if verbose:
                print(f"   ❌ Не удалось устранить мнимые конфликты")
            return False, {}
    else:
        if verbose:
            print(f"   ✅ Расписание найдено (без мнимых конфликтов)")
        return True, matching


def run_strategic_diagnostic(events: List, rooms: List, work_day, groups: List):
    """Запускает стратегическую диагностику для одного дня."""
    print(f"\n   Диагностика для дня {work_day.date.isoformat()}:")

    modifications = [
        ("Исходная сеть", True, True),
        ("Без вместимости", False, True),
        ("Без оснащённости", True, False),
        ("Без обоих ограничений", False, False),
    ]

    flow_results = {}
    for name, check_cap, check_eq in modifications:
        graph = build_bipartite_graph(events, rooms, work_day, groups,
                                      check_capacity=check_cap, check_equipment=check_eq)
        network, source, sink = build_flow_network(graph, events, rooms, work_day, groups)
        flow_value, _ = max_flow_dinic(network, source, sink)
        flow_results[name] = flow_value

    base = flow_results.get("Исходная сеть", 0)
    no_cap = flow_results.get("Без вместимости", 0)
    no_eq = flow_results.get("Без оснащённости", 0)

    print(f"\n   Результаты диагностики для {work_day.date.isoformat()}:")
    print(f"      Исходная сеть: {base}")
    print(f"      Без вместимости: {no_cap}")
    print(f"      Без оснащённости: {no_eq}")

    if no_cap > base and no_eq == base:
        print("   📊 Вывод: Критическим фактором является НЕДОСТАТОЧНАЯ ВМЕСТИМОСТЬ")
        print("      Рекомендуется увеличить вместимость аудиторий или добавить новые")
    elif no_eq > base and no_cap == base:
        print("   📊 Вывод: Критическим фактором является НЕДОСТАТОЧНОЕ ОСНАЩЕНИЕ")
        print("      Рекомендуется дооснастить аудитории недостающим оборудованием")
    elif no_cap > base and no_eq > base:
        print("   📊 Вывод: Комбинированная проблема (вместимость и оснащённость)")
    else:
        print("   📊 Вывод: Проблема в глобальном дефиците слотов")
        print("      Рекомендуется увеличить количество аудиторий или временных интервалов")

    print(f"   Потенциальный выигрыш от снятия ограничений: {no_cap - base}")


def main():
    """Координирует выполнение всех этапов алгоритма."""
    print("=" * 70)
    print("  СИСТЕМА АНАЛИЗА И СОСТАВЛЕНИЯ РАСПИСАНИЯ")
    print("=" * 70)

    # Шаг 1: Загрузка данных
    print("\n[1] Загрузка данных...")
    try:
        data = load_all()
        groups = data["groups"]
        events = data["events"]
        rooms = data["rooms"]
        teachers = data["teachers"]
        time_slots = data["time_slots"]
        work_days = data["work_days"]
        print(f"   Загружено: групп={len(groups)}, событий={len(events)}, "
              f"аудиторий={len(rooms)}, преподавателей={len(teachers)}, "
              f"рабочих дней={len(work_days)}")
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        return

    # Группируем события по датам
    events_by_date = defaultdict(list)
    for event in events:
        if event.date:
            events_by_date[event.date].append(event)
        else:
            print(f"⚠️ Событие {event.id} ({event.name}) не имеет даты и будет пропущено")

    if not events_by_date:
        print("❌ Нет событий с указанной датой")
        return

    print(f"\n[2] Распределение событий по дням:")
    for date_str, day_events in sorted(events_by_date.items()):
        print(f"   {date_str}: {len(day_events)} событий")

    # Словарь для хранения расписаний по дням
    all_assignments = {}
    problematic_days = []

    # Перебираем все рабочие дни
    for work_day in work_days:
        if work_day.is_holiday or work_day.day_type != "учебный":
            continue  # пропускаем выходные и праздники

        date_str = work_day.date.isoformat()
        day_events = events_by_date.get(date_str, [])

        if not day_events:
            continue  # в этот день нет событий

        print(f"\n[3] Обработка дня {date_str} ({len(day_events)} событий)...")

        # Пытаемся построить расписание для этого дня (тихо)
        success, assignment = build_schedule_for_day(
            events=day_events,
            rooms=rooms,
            work_day=work_day,
            groups=groups,
            teachers=teachers,
            time_slots=time_slots,
            verbose=False
        )

        if success:
            all_assignments[date_str] = assignment
            print(f"   ✅ Расписание для {date_str} успешно построено")
        else:
            problematic_days.append((work_day, day_events))
            print(f"   ❌ Не удалось построить расписание для {date_str}")

    # Если есть проблемные дни, запускаем интерактивную диагностику
    if problematic_days:
        print("\n" + "=" * 70)
        print("ОБНАРУЖЕНЫ ПРОБЛЕМНЫЕ ДНИ")
        print("=" * 70)

        for work_day, day_events in problematic_days:
            date_str = work_day.date.isoformat()
            print(f"\nДень: {date_str} (событий: {len(day_events)})")

            choice = get_user_choice(
                f"Что делать с днём {date_str}?",
                ["Пропустить день", "Показать диагностику", "Завершить работу"]
            )

            if choice == "Завершить работу":
                return
            elif choice == "Показать диагностику":
                run_strategic_diagnostic(day_events, rooms, work_day, groups)

                # После диагностики предлагаем ещё раз попробовать построить расписание
                retry_choice = get_user_choice(
                    "Попробовать построить расписание снова?",
                    ["Да, попробовать", "Нет, пропустить день"]
                )
                if retry_choice == "Да, попробовать":
                    success, assignment = build_schedule_for_day(
                        events=day_events,
                        rooms=rooms,
                        work_day=work_day,
                        groups=groups,
                        teachers=teachers,
                        time_slots=time_slots,
                        verbose=True  # теперь показываем подробности
                    )
                    if success:
                        all_assignments[date_str] = assignment
                        print(f"   ✅ Расписание для {date_str} успешно построено")
            # Если "Пропустить день" — просто идём дальше

    # Экспорт всех успешно построенных расписаний
    if all_assignments:
        print("\n[4] Экспорт расписаний...")
        export_students_schedule(all_assignments, events, groups, rooms, work_days, time_slots, OUTPUT_DIR)
        export_teachers_schedule(all_assignments, events, teachers, rooms, work_days, time_slots, OUTPUT_DIR)
        print(f"\n✅ Сохранено расписаний для {len(all_assignments)} дней")
    else:
        print("\n❌ Не удалось построить расписание ни для одного дня")

    print("\n" + "=" * 70)
    print("  РАБОТА ЗАВЕРШЕНА")
    print("=" * 70)


if __name__ == "__main__":
    main()