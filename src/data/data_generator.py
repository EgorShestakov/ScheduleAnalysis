import csv
import random
from datetime import date, timedelta
from pathlib import Path

# Константы
START_DATE = date(2025, 9, 1)
END_DATE = date(2025, 12, 31)

# Соответствие факультетов и номеров групп
GROUP_NUMBERS = {
    "ПМИ": 110,
    "ИВТ": 106,
    "ПИ": 116,
}

# Список возможных предметов по кафедрам
SUBJECTS = {
    "ПМИ": [
        "Математический анализ",
        "Линейная алгебра",
        "Дифференциальные уравнения",
        "Теория вероятностей",
        "Математическая статистика",
        "Дискретная математика",
        "Численные методы",
        "Методы оптимизации",
        "Дифференциальная геометрия",
        "Функциональный анализ",
        "Теория графов",
        "Математическая логика",
    ],
    "ИВТ": [
        "Программирование",
        "Алгоритмы и структуры данных",
        "Базы данных",
        "Операционные системы",
        "Компьютерные сети",
        "Системы искусственного интеллекта",
        "Машинное обучение",
        "Анализ данных",
        "Веб-технологии",
        "Информационная безопасность",
        "Объектно-ориентированное программирование",
        "Архитектура ЭВМ",
    ],
    "ПИ": [
        "Технологии программирования",
        "Проектирование информационных систем",
        "Управление проектами",
        "Тестирование программного обеспечения",
        "Разработка мобильных приложений",
        "Кроссплатформенное программирование",
        "Базы данных в информационных системах",
        "Web-программирование",
        "Облачные технологии",
        "DevOps практики",
        "Микросервисная архитектура",
        "UI/UX проектирование",
    ],
}

# Фамилии
SURNAMES = [
    "Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Попов", "Васильев",
    "Соколов", "Михайлов", "Новиков", "Фёдоров", "Морозов", "Волков", "Алексеев",
    "Лебедев", "Семёнов", "Егоров", "Павлов", "Козлов", "Степанов", "Николаев"
]

# Имена
NAMES = [
    "Александр", "Дмитрий", "Максим", "Сергей", "Андрей", "Алексей", "Евгений",
    "Владимир", "Игорь", "Олег", "Павел", "Роман", "Михаил", "Николай", "Виктор"
]

# Отчества
PATRONYMS = [
    "Александрович", "Дмитриевич", "Максимович", "Сергеевич", "Андреевич",
    "Алексеевич", "Евгеньевич", "Владимирович", "Игоревич", "Олегович",
    "Павлович", "Романович", "Михайлович", "Николаевич", "Викторович"
]


def is_weekend(d: date) -> bool:
    """Проверяет, является ли день выходным (воскресенье)."""
    return d.weekday() == 6


def is_holiday(d: date) -> bool:
    """Проверяет, является ли день праздничным."""
    holidays = [
        date(2025, 9, 1),
        date(2025, 11, 4),
    ]
    return d in holidays


def generate_calendar(output_dir: Path):
    """Генерирует calendar.csv на семестр."""
    calendar = []
    current = START_DATE
    while current <= END_DATE:
        is_hol = is_holiday(current) or is_weekend(current)
        if is_weekend(current):
            day_type = "выходной"
        elif is_holiday(current):
            day_type = "праздник"
        else:
            day_type = "учебный"
        calendar.append({
            "date": current.isoformat(),
            "is_holiday": "True" if is_hol else "False",
            "day_type": day_type
        })
        current += timedelta(days=1)

    with open(output_dir / "calendar.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "is_holiday", "day_type"])
        writer.writeheader()
        writer.writerows(calendar)

    return calendar


def generate_events(output_dir: Path):
    """Генерирует events.csv со списком всех возможных событий (предметов)."""
    events = []
    event_id = 1

    all_subjects = set()
    for subjects in SUBJECTS.values():
        all_subjects.update(subjects)

    for subject in sorted(all_subjects):
        events.append({
            "id": event_id,
            "name": subject
        })
        event_id += 1

    with open(output_dir / "events.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name"])
        writer.writeheader()
        writer.writerows(events)

    return events


def get_group_size(faculty: str, course: int) -> int:
    """Возвращает численность группы."""
    if faculty == "ПМИ":
        min_size, max_size = 15, 25
    else:
        min_size, max_size = 20, 30

    if course == 1:
        return max_size
    elif course == 4:
        return min_size
    else:
        size = max_size - (max_size - min_size) * (course - 1) / 3
        return int(round(size))


def generate_groups(output_dir: Path):
    """Генерирует groups.csv."""
    groups = []
    group_id = 1

    faculties = ["ПМИ", "ИВТ", "ПИ"]

    for faculty in faculties:
        group_number = GROUP_NUMBERS[faculty]
        for course in range(1, 5):
            groups.append({
                "id": group_id,
                "course": course,
                "department": "ИАИТ",
                "number": group_number,
                "size": get_group_size(faculty, course)
            })
            group_id += 1

    with open(output_dir / "groups.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "course", "department", "number", "size"])
        writer.writeheader()
        writer.writerows(groups)


def generate_time_grid(output_dir: Path):
    """Генерирует time_grid.csv (7 пар)."""
    slots = [
        (8 * 60, 8 * 60 + 95),
        (9 * 60 + 45, 9 * 60 + 140),
        (11 * 60 + 50, 11 * 60 + 145),
        (13 * 60 + 35, 13 * 60 + 130),
        (15 * 60 + 40, 15 * 60 + 155),
        (17 * 60 + 25, 17 * 60 + 120),
        (19 * 60, 19 * 60 + 95),
    ]

    time_slots = []
    for slot_id, (start, end) in enumerate(slots, start=1):
        start_hour = start // 60
        start_min = start % 60
        end_hour = end // 60
        end_min = end % 60

        time_slots.append({
            "slot_id": slot_id,
            "start_time": f"{start_hour:02d}:{start_min:02d}",
            "end_time": f"{end_hour:02d}:{end_min:02d}"
        })

    with open(output_dir / "time_grid.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["slot_id", "start_time", "end_time"])
        writer.writeheader()
        writer.writerows(time_slots)


def get_room_capacity() -> int:
    """Возвращает вместимость аудитории."""
    capacity = int(random.gauss(25, 8))
    return max(15, min(50, capacity))


def get_room_equipment() -> str:
    """Возвращает оснащение аудитории.
    Распределение:
    - 40% только доска
    - 40% доска, проектор
    - 20% доска, компьютеры
    """
    r = random.random()
    if r < 0.4:
        return "доска"
    elif r < 0.8:
        return "доска, проектор"
    else:
        return "доска, компьютеры"


def generate_rooms(output_dir: Path):
    """Генерирует rooms.csv."""
    rooms = []
    room_id = 1

    for floor in range(1, 6):
        base_number = floor * 100
        for room_num in range(1, 16):
            number = base_number + room_num
            capacity = get_room_capacity()
            equipment = get_room_equipment()

            rooms.append({
                "id": room_id,
                "capacity": capacity,
                "equipment": equipment,
                "number": number
            })
            room_id += 1

    rooms.sort(key=lambda x: x["number"])

    with open(output_dir / "rooms.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "capacity", "equipment", "number"])
        writer.writeheader()
        writer.writerows(rooms)


def load_events(event_file: Path) -> dict:
    """Загружает события и возвращает словари {id: name} и {name: id}."""
    events_by_id = {}
    events_by_name = {}
    with open(event_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            event_id = int(row["id"])
            name = row["name"]
            events_by_id[event_id] = name
            events_by_name[name] = event_id
    return events_by_id, events_by_name


def get_teacher_specialization(events_by_name: dict, department: str) -> list:
    """Возвращает список ID предметов для преподавателя."""
    num_subjects = min(6, max(3, int(-random.random() * 3) + 3))
    subjects = SUBJECTS.get(department, SUBJECTS["ПМИ"])
    selected = random.sample(subjects, min(num_subjects, len(subjects)))
    return [events_by_name[name] for name in selected]


def generate_teachers(output_dir: Path, events_by_name: dict):
    """Генерирует teachers.csv."""
    teachers = []
    teacher_id = 1
    departments = ["ПМИ", "ИВТ", "ПИ"]

    for department in departments:
        for _ in range(20):
            surname = random.choice(SURNAMES)
            name = random.choice(NAMES)
            patronymic = random.choice(PATRONYMS)
            specialization_ids = get_teacher_specialization(events_by_name, department)

            teachers.append({
                "id": teacher_id,
                "surname": surname,
                "name": name,
                "patronymic": patronymic,
                "specialisation": ", ".join(map(str, specialization_ids)),
                "department": department
            })
            teacher_id += 1

    with open(output_dir / "teachers.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "surname", "name", "patronymic", "specialisation"])
        writer.writeheader()
        for teacher in teachers:
            writer.writerow({
                "id": teacher["id"],
                "surname": teacher["surname"],
                "name": teacher["name"],
                "patronymic": teacher["patronymic"],
                "specialisation": teacher["specialisation"]
            })


def get_requirement_by_subject(subject_name: str) -> str:
    """
    Определяет требуемое оборудование для предмета.
    - Чистая математика -> всегда "доска"
    - Остальное: 40% "доска", 20% "доска, проектор", 40% "доска, компьютеры"
    """
    math_keywords = ["Математический", "Алгебра", "Дифференциальные", "Теория вероятностей",
                     "Статистика", "Дискретная", "Геометрия", "Функциональный", "Графов", "Логика"]

    for kw in math_keywords:
        if kw in subject_name:
            return "доска"

    r = random.random()
    if r < 0.4:
        return "доска"
    elif r < 0.6:
        return "доска, проектор"
    else:
        return "доска, компьютеры"


def generate_requirements(output_dir: Path, calendar: list, events_by_id: dict, groups: list):
    """Генерирует requirements.csv."""
    requirements = []

    event_id_by_name = {name: eid for eid, name in events_by_id.items()}

    print(f"События: {len(event_id_by_name)}")
    print(f"Первые 5 событий: {list(event_id_by_name.items())[:5]}")

    groups_by_faculty = {}
    for group in groups:
        faculty = None
        for f, num in GROUP_NUMBERS.items():
            if group["number"] == num:
                faculty = f
                break
        if faculty:
            groups_by_faculty.setdefault(faculty, []).append(group)
        else:
            print(f"Группа {group['number']} не сопоставлена ни с одним факультетом")

    print(f"Групп по факультетам: {[(f, len(g)) for f, g in groups_by_faculty.items()]}")

    study_days = [day for day in calendar
                  if day["is_holiday"] != "True" and day["day_type"] != "выходной"]
    print(f"Учебных дней: {len(study_days)}")

    for day in study_days:
        date_str = day["date"]

        r = random.random()
        if r < 0.2:
            num_pairs = 2
        elif r < 0.6:
            num_pairs = 3
        else:
            num_pairs = 4

        for faculty, faculty_groups in groups_by_faculty.items():
            subjects_for_faculty = SUBJECTS.get(faculty, SUBJECTS["ПМИ"])

            if len(subjects_for_faculty) < num_pairs:
                selected_subjects = subjects_for_faculty.copy()
            else:
                selected_subjects = random.sample(subjects_for_faculty, num_pairs)

            num_groups = min(len(selected_subjects), len(faculty_groups))
            if num_groups == 0:
                continue

            selected_groups = random.sample(faculty_groups, num_groups)

            for i, group in enumerate(selected_groups):
                subject = selected_subjects[i]
                event_id = event_id_by_name.get(subject)
                if event_id is None:
                    continue

                total_pairs = random.choices([1, 2, 3, 4], weights=[0.1, 0.3, 0.4, 0.2])[0]
                requirement = get_requirement_by_subject(subject)

                requirements.append({
                    "date": date_str,
                    "group_id": group["id"],
                    "event_id": event_id,
                    "total_pairs": total_pairs,
                    "requirement": requirement
                })

    print(f"\nСгенерировано в цикле: {len(requirements)} заявок")

    if not requirements:
        print("ВНИМАНИЕ: Не сгенерировано ни одной заявки! Добавляю тестовые...")
        # аварийная вставка
        test_date = study_days[0]["date"] if study_days else "2025-09-02"
        for group in groups[:3]:
            for event_id in [19, 26, 36]:
                requirements.append({
                    "date": test_date,
                    "group_id": group["id"],
                    "event_id": event_id,
                    "total_pairs": 2,
                    "requirement": "доска, компьютеры"
                })

    if requirements:
        with open(output_dir / "requirements.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "group_id", "event_id", "total_pairs", "requirement"])
            writer.writeheader()
            for req in requirements:
                writer.writerow(req)


def generate(output_dir: Path = Path("input")):
    """Генерирует все CSV-файлы в указанную директорию."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Генерация calendar.csv...")
    calendar = generate_calendar(output_dir)

    print("Генерация events.csv...")
    events = generate_events(output_dir)

    print("Генерация groups.csv...")
    generate_groups(output_dir)

    print("Генерация time_grid.csv...")
    generate_time_grid(output_dir)

    print("Генерация rooms.csv...")
    generate_rooms(output_dir)

    events_by_id, events_by_name = load_events(output_dir / "events.csv")

    print("Генерация teachers.csv...")
    generate_teachers(output_dir, events_by_name)

    # Загружаем группы для генерации требований, преобразуя number в int
    groups = []
    with open(output_dir / "groups.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            groups.append({
                "id": int(row["id"]),
                "course": int(row["course"]),
                "department": row["department"],
                "number": int(row["number"]),  # преобразуем в int
                "size": int(row["size"])
            })

    print("Генерация requirements.csv...")
    generate_requirements(output_dir, calendar, events_by_id, groups)

    print(f"\nДанные успешно сгенерированы в {output_dir}")
    print(f"  - calendar.csv: {len(calendar)} дней")
    print(f"  - events.csv: {len(events)} событий")
    print(f"  - groups.csv: 12 групп")
    print(f"  - time_grid.csv: 7 пар")
    print(f"  - rooms.csv: 75 аудиторий")
    print(f"  - teachers.csv: 60 преподавателей")
    print(f"  - requirements.csv: сгенерирован")


if __name__ == "__main__":
    generate()