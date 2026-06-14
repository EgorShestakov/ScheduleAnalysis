"""Визуализация исходных данных и результатов."""

import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import List

# Добавляем путь к src для импорта модулей
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import load_all


def export_subjects_distribution(events: List, groups: List, work_days: List, output_path: Path):
    """
    Экспортирует исходное распределение предметов по дням (без кабинетов и временных интервалов).
    Формат: для каждой группы отдельная таблица:
        - первая строка: номер группы
        - вторая строка: даты
        - строки 3-9: номера пар (остаются пустыми, так как время не назначено)
        - в ячейках на пересечении даты и пары — предметы, которые запланированы на этот день
          (предметы перечисляются через запятую)

    :param events: список событий
    :param groups: список групп
    :param work_days: список рабочих дней
    :param output_path: путь для сохранения CSV-файла
    """
    group_by_id = {g.id: g for g in groups}

    # Группируем события: группа -> дата -> список предметов
    schedule = defaultdict(lambda: defaultdict(list))

    for event in events:
        if event.date is None:
            continue
        group = group_by_id.get(event.group_id)
        if group is None:
            continue
        schedule[group.id][event.date].append(event.name)

    # Все учебные даты
    all_dates = [day.date.isoformat() for day in work_days
                 if day.day_type == "учебный" and not day.is_holiday]

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "subjects_distribution.csv"

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        for group_id, date_subjects in sorted(schedule.items()):
            group = group_by_id.get(group_id)
            group_name = f"{group.course}-{group.department}-{group.number}" if group else f"Группа {group_id}"

            # Пустая строка между группами
            writer.writerow([])

            # Название группы
            writer.writerow([group_name])

            # Строка с датами
            dates_row = [""]
            for d in all_dates:
                dates_row.append(d)
            writer.writerow(dates_row)

            # Строки с 1 по 7 пару (все пустые, кроме ячеек с предметами)
            # Предметы выводятся в первой строке (пара 1) для соответствующей даты
            for slot_num in range(1, 8):
                row = [str(slot_num)]
                for d in all_dates:
                    subjects = date_subjects.get(d, [])
                    if subjects and slot_num == 1:
                        # Если есть предметы, выводим их в первой строке
                        row.append(", ".join(sorted(subjects)))
                    else:
                        row.append("")
                writer.writerow(row)


def main():
    """Запускает визуализацию исходного распределения предметов."""
    print("=" * 70)
    print("  ВИЗУАЛИЗАЦИЯ ИСХОДНОГО РАСПРЕДЕЛЕНИЯ ПРЕДМЕТОВ")
    print("=" * 70)

    # Загрузка данных
    print("\n[1] Загрузка данных...")
    try:
        data = load_all()
        groups = data["groups"]
        events = data["events"]
        work_days = data["work_days"]
        print(f"   Загружено: групп={len(groups)}, событий={len(events)}, "
              f"рабочих дней={len(work_days)}")
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        return

    # Экспорт распределения предметов
    print("\n[2] Экспорт распределения предметов...")
    output_dir = Path(__file__).parent / "output"
    export_subjects_distribution(events, groups, work_days, output_dir)

    print(f"\n✅ Файл subjects_distribution.csv сохранён в {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()