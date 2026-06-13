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
from src.graph_builder import build_bipartite_graph, get_all_slots
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


def show_criterion_one_result(events, rooms, work_days) -> bool:
    """Проверяет первый критерий и выводит результат."""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ПЕРВОГО КРИТЕРИЯ")
    print("=" * 60)

    num_events = len(events)
    num_rooms = len(rooms)
    num_slots = sum(len(day.available_slots) for day in work_days)
    total_slots = num_rooms * num_slots

    print(f"|E| = {num_events}")
    print(f"|C|·|T| = {num_rooms} × {num_slots} = {total_slots}")

    if num_events <= total_slots:
        print("✅ Критерий выполнен. Есть смысл в дальнейшем анализе.")
        return True
    else:
        diff = num_events - total_slots
        print(f"❌ Критерий НЕ выполнен! Превышение: {diff} слотов.")
        print("\nРекомендации:")
        print(f"  1. Убрать как минимум {diff} событий")
        print(f"  2. Добавить аудиторий: примерно {diff // num_slots + 1}")
        print(f"  3. Добавить временных слотов: примерно {diff // num_rooms + 1}")
        return False


def export_students_schedule(assignment: Dict[int, Tuple], events: List, groups: List,
                              work_days: List, time_slots: List, output_path: Path):
    """
    Экспортирует расписание для студентов.
    Формат: для каждой группы отдельная таблица:
        - первая строка: номер группы
        - вторая строка: даты
        - строки 3-9: номера пар (1-7) и события
    """
    event_by_id = {e.id: e for e in events}
    group_by_id = {g.id: g for g in groups}
    slot_by_id = {s.id: s for s in time_slots}

    schedule = defaultdict(lambda: defaultdict(dict))

    for event_id, (room_id, date_str, slot_id) in assignment.items():
        event = event_by_id[event_id]
        group_id = event.group_id
        slot = slot_by_id.get(slot_id)
        if slot:
            schedule[group_id][date_str][slot.number] = event.name

    all_dates = [day.date.isoformat() for day in work_days
                 if day.day_type == "учебный" and not day.is_holiday]

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "students_schedule.csv"

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        for group_id, date_slots in schedule.items():
            group = group_by_id.get(group_id)
            group_name = f"{group.course}-{group.department}-{group.number}" if group else f"Группа {group_id}"

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


def export_teachers_schedule(assignment: Dict[int, Tuple], events: List, teachers: List,
                              work_days: List, time_slots: List, output_path: Path):
    """
    Экспортирует расписание для преподавателей.
    Формат: для каждого преподавателя отдельная таблица:
        - первая строка: ФИО преподавателя
        - вторая строка: даты
        - строки 3-9: номера пар (1-7) и события
    """
    event_by_id = {e.id: e for e in events}
    teacher_by_id = {t.id: t for t in teachers}
    slot_by_id = {s.id: s for s in time_slots}

    schedule = defaultdict(lambda: defaultdict(dict))

    for event_id, (room_id, date_str, slot_id) in assignment.items():
        event = event_by_id[event_id]
        teacher_id = event.teacher_id
        if teacher_id:
            slot = slot_by_id.get(slot_id)
            if slot:
                schedule[teacher_id][date_str][slot.number] = event.name

    all_dates = [day.date.isoformat() for day in work_days
                 if day.day_type == "учебный" and not day.is_holiday]

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "teachers_schedule.csv"

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        for teacher_id, date_slots in schedule.items():
            teacher = teacher_by_id.get(teacher_id)
            teacher_name = teacher.full_name() if teacher else f"Преподаватель {teacher_id}"

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
        events_template = data["events_template"]
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

    # Шаг 2: Проверка первого критерия
    if not criterion_one(events, rooms, work_days):
        choice = get_user_choice("Первый критерий не выполнен. Что делать?",
                                ["Завершить работу", "Продолжить анализ (диагностика)"])
        if choice == "Завершить работу":
            return

    # Шаг 3: Построение двудольного графа
    print("\n[2] Построение двудольного графа...")
    bipartite_graph = build_bipartite_graph(
        events=events,
        rooms=rooms,
        work_days=work_days,
        groups=groups,
        check_capacity=True,
        check_equipment=True
    )
    print(f"   Граф построен. Всего рёбер: {sum(len(v) for v in bipartite_graph.values())}")

    # Шаг 4: Проверка второго критерия
    print("\n[3] Проверка второго критерия...")
    success_two, isolated_ids = criterion_two(bipartite_graph, events, rooms, groups)
    if not success_two:
        choice = get_user_choice("Второй критерий не выполнен. Что делать?",
                                ["Продолжить с существующими событиями", "Завершить работу"])
        if choice == "Завершить работу":
            return

    # Шаг 5: Проверка третьего критерия (поиск совершенного паросочетания)
    print("\n[4] Поиск совершенного паросочетания...")
    perfect, matching = criterion_three(bipartite_graph, events)

    if perfect:
        print("✅ Найдено совершенное паросочетание!")

        # Преобразуем matching в прямой формат (уже в criterion_three это сделано)
        direct_matching = matching

        # Шаг 6: Проверка четвёртого критерия (мнимые расписания)
        print("\n[5] Проверка на мнимые расписания...")
        if not criterion_four(direct_matching, events):
            print("⚠️ Обнаружены мнимые конфликты (одна группа в одно время в разных аудиториях)")
            choice = get_user_choice("Что делать?",
                                    ["Решить задачу о назначениях (оптимизация)",
                                     "Принять расписание как есть",
                                     "Завершить работу"])
            if choice == "Завершить работу":
                return
            elif choice == "Решить задачу о назначениях (оптимизация)":
                all_slots = get_all_slots(rooms, work_days)
                cost_matrix = build_cost_matrix(events, all_slots, groups, rooms)
                assignment = solve_assignment(cost_matrix, events, all_slots)
                if not criterion_four(assignment, events):
                    print("ВСЁ РАВНО НЕ ВЫПОЛНЯЕТСЯ 4 КРИТЕРИЙ")
                # print_assignment_details(assignment, cost_matrix, events, all_slots, groups, rooms)

                # Экспорт расписаний
                export_students_schedule(assignment, events, groups, work_days, time_slots, OUTPUT_DIR)
                export_teachers_schedule(assignment, events, teachers, work_days, time_slots, OUTPUT_DIR)
                print("   Расписания сохранены в data/output/")
            else:
                # Принять расписание как есть
                assignment = direct_matching
                export_students_schedule(assignment, events, groups, work_days, time_slots, OUTPUT_DIR)
                export_teachers_schedule(assignment, events, teachers, work_days, time_slots, OUTPUT_DIR)
                print("   Расписания сохранены в data/output/")
        else:
            print("✅ Мнимых конфликтов нет")
            assignment = direct_matching

            # Экспорт расписаний
            export_students_schedule(assignment, events, groups, work_days, time_slots, OUTPUT_DIR)
            export_teachers_schedule(assignment, events, teachers, work_days, time_slots, OUTPUT_DIR)
            print("   Расписания сохранены в data/output/")

            # Запрос на дополнительный анализ
            if get_user_choice("Хотите провести дополнительный стратегический анализ?",
                              ["Да", "Нет"]) == "Да":
                perfect = False
            else:
                print("\n✅ Работа завершена. Расписание готово!")
                return
    else:
        print("❌ Совершенное паросочетание не найдено")

    # Шаг 7: Диагностика (если паросочетание не найдено или запрошен анализ)
    if not perfect:
        print("\n[6] Запуск стратегической диагностики (потоковая модель)...")

        modifications = [
            ("Исходная сеть", True, True),
            ("Без вместимости", False, True),
            ("Без оснащённости", True, False),
            ("Без обоих ограничений", False, False),
        ]

        flow_results = {}
        for name, check_cap, check_eq in modifications:
            print(f"\n   Построение {name}...")
            graph = build_bipartite_graph(events, rooms, work_days, groups,
                                          check_capacity=check_cap, check_equipment=check_eq)
            network, source, sink = build_flow_network(graph, events, rooms, work_days, groups)
            flow_value, flow_dist = max_flow_dinic(network, source, sink)
            flow_results[name] = flow_value
            print(f"      Максимальный поток: {flow_value}")

        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ СТРАТЕГИЧЕСКОГО АНАЛИЗА")
        print("=" * 60)
        base = flow_results.get("Исходная сеть", 0)
        no_cap = flow_results.get("Без вместимости", 0)
        no_eq = flow_results.get("Без оснащённости", 0)

        if no_cap > base and no_eq == base:
            print("📊 Вывод: Критическим фактором является НЕДОСТАТОЧНАЯ ВМЕСТИМОСТЬ")
            print("   Рекомендуется увеличить вместимость аудиторий или добавить новые")
        elif no_eq > base and no_cap == base:
            print("📊 Вывод: Критическим фактором является НЕДОСТАТОЧНОЕ ОСНАЩЕНИЕ")
            print("   Рекомендуется дооснастить аудитории недостающим оборудованием")
        elif no_cap > base and no_eq > base:
            print("📊 Вывод: Комбинированная проблема (вместимость и оснащённость)")
        else:
            print("📊 Вывод: Проблема в глобальном дефиците слотов")
            print("   Рекомендуется увеличить количество аудиторий или временных интервалов")

        print(f"\nПотенциальный выигрыш от снятия ограничений: {no_cap - base}")

    print("\n" + "=" * 70)
    print("  РАБОТА ЗАВЕРШЕНА")
    print("=" * 70)


if __name__ == "__main__":
    main()