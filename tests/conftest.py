import pytest
from datetime import date
from src.data_models import Group, Room, Teacher, Event, TimeSlot, WorkDay


# ==================== Фикстуры событий ====================

@pytest.fixture
def event(group, teacher):
    """Возвращает тестовое событие e1 (Матанализ)."""
    return Event(id=1, name="Матанализ", group_id=group.id,
                 teacher_id=teacher.id, total_hours=4,
                 required_features=["доска"])


@pytest.fixture
def event_single():
    """Возвращает одно тестовое событие."""
    return Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[])


@pytest.fixture
def event_2(group, teacher_2):
    """Возвращает тестовое событие e2 (Численные методы)."""
    return Event(id=2, name="Численные методы", group_id=group.id,
                 teacher_id=teacher_2.id, total_hours=2,
                 required_features=["доска", "принтер"])


@pytest.fixture
def event_3(group_small, teacher_3):
    """Возвращает тестовое событие e3 (Информационные технологии)."""
    return Event(id=3, name="Информационные технологии", group_id=group_small.id,
                 teacher_id=teacher_3.id, total_hours=3,
                 required_features=["компьютеры"])


@pytest.fixture
def events_list(event, event_2, event_3):
    """Возвращает список всех тестовых событий."""
    return [event, event_2, event_3]


@pytest.fixture
def events_5():
    """Возвращает 5 простых событий для тестирования критериев."""
    return [Event(id=i, name=f"E{i}", group_id=1, teacher_id=1, total_hours=1, required_features=[]) for i in range(1, 6)]


@pytest.fixture
def events_6():
    """Возвращает 6 простых событий для тестирования критериев."""
    return [Event(id=i, name=f"E{i}", group_id=1, teacher_id=1, total_hours=1, required_features=[]) for i in range(1, 7)]


@pytest.fixture
def events_10():
    """Возвращает 10 простых событий для тестирования критериев."""
    return [Event(id=i, name=f"E{i}", group_id=1, teacher_id=1, total_hours=1, required_features=[]) for i in range(1, 11)]


@pytest.fixture
def events_15():
    """Возвращает 15 простых событий для тестирования критериев."""
    return [Event(id=i, name=f"E{i}", group_id=1, teacher_id=1, total_hours=1, required_features=[]) for i in range(1, 16)]


@pytest.fixture
def events_two_connected():
    """Возвращает два события, оба должны быть в графе."""
    return [
        Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[])
    ]


@pytest.fixture
def events_three_with_isolated():
    """Возвращает три события, где событие 2 изолировано."""
    return [
        Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        Event(id=3, name="E3", group_id=1, teacher_id=1, total_hours=1, required_features=[])
    ]


@pytest.fixture
def events_three_all_connected():
    """Возвращает три события."""
    return [
        Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        Event(id=3, name="E3", group_id=1, teacher_id=1, total_hours=1, required_features=[])
    ]


@pytest.fixture
def events_two_with_features():
    """Возвращает два события с разными требованиями."""
    return [
        Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=["доска"]),
        Event(id=2, name="E2", group_id=2, teacher_id=2, total_hours=1, required_features=["компьютеры"])
    ]


@pytest.fixture
def events_two_with_missing():
    """Возвращает два события, где событие 2 отсутствует в графе."""
    return [
        Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[])
    ]


@pytest.fixture
def events_two_with_empty_edges():
    """Возвращает два события, где событие 1 имеет пустой список рёбер."""
    return [
        Event(id=1, name="E1", group_id=1, teacher_id=1, total_hours=1, required_features=[]),
        Event(id=2, name="E2", group_id=1, teacher_id=1, total_hours=1, required_features=[])
    ]


@pytest.fixture
def event_empty_features():
    """Возвращает тестовое событие без требований к оборудованию."""
    return Event(id=2, name="Лекция", group_id=1, teacher_id=1,
                 total_hours=2, required_features=[])


@pytest.fixture
def event_zero_hours():
    """Возвращает тестовое событие с нулевым количеством часов."""
    return Event(id=3, name="Факультатив", group_id=1, teacher_id=1,
                 total_hours=0, required_features=[])


# ==================== Фикстуры аудиторий ====================

@pytest.fixture
def room():
    """Возвращает тестовую аудиторию."""
    return Room(id=1, number=402, capacity=40, equipment=["доска", "компьютеры"])


@pytest.fixture
def room_small():
    """Возвращает тестовую аудиторию с маленькой вместимостью."""
    return Room(id=2, number=403, capacity=16, equipment=["доска", "принтер"])


@pytest.fixture
def room_without_equipment():
    """Возвращает тестовую аудиторию с маленькой вместимостью."""
    return Room(id=2, number=403, capacity=16, equipment=[])


@pytest.fixture
def rooms_3():
    """Возвращает три тестовые аудитории."""
    return [
        Room(id=1, number=101, capacity=30, equipment=[]),
        Room(id=2, number=102, capacity=30, equipment=[]),
        Room(id=3, number=103, capacity=30, equipment=[])
    ]


@pytest.fixture
def room_single():
    """Возвращает одну тестовую аудиторию."""
    return Room(id=1, number=101, capacity=30, equipment=[])


@pytest.fixture
def rooms_list(room, room_small):
    """Возвращает список всех тестовых аудиторий."""
    return [room, room_small]


# ==================== Фикстуры групп ====================

@pytest.fixture
def group():
    """Возвращает тестовую группу."""
    return Group(id=1, course=1, department="ИАИТ", number=110, size=31)


@pytest.fixture
def group_small():
    """Возвращает тестовую группу с маленькой численностью."""
    return Group(id=2, course=1, department="ИАИТ", number=120, size=15)


@pytest.fixture
def groups_list(group, group_small):
    """Возвращает список всех тестовых групп."""
    return [group, group_small]


# ==================== Фикстуры временных слотов ====================

@pytest.fixture
def slot1():
    """Возвращает временной слот 1 (09:00-10:30)."""
    return TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")


@pytest.fixture
def slot2():
    """Возвращает временной слот 2 (10:40-12:10)."""
    return TimeSlot(id=2, number=2, start_time="10:40", end_time="12:10")


@pytest.fixture
def slot_single():
    """Возвращает один временной слот."""
    return TimeSlot(id=1, number=1, start_time="09:00", end_time="10:30")


@pytest.fixture
def slots(slot1, slot2):
    """Возвращает список временных слотов."""
    return [slot1, slot2]


# ==================== Фикстуры рабочих дней ====================

@pytest.fixture
def workday(slot1, slot2):
    """Возвращает тестовый рабочий день с двумя слотами."""
    return WorkDay(date=date(2026, 3, 27), is_holiday=False,
                   day_type="четная", available_slots=[slot1, slot2])


@pytest.fixture
def workday_single(slot_single):
    """Возвращает тестовый рабочий день с одним слотом."""
    return WorkDay(date=date(2026, 3, 28), is_holiday=False,
                   day_type="четная", available_slots=[slot_single])


@pytest.fixture
def workday_holiday(slot1):
    """Возвращает тестовый выходной день."""
    return WorkDay(date=date(2026, 3, 29), is_holiday=True,
                   day_type="воскресенье", available_slots=[])


@pytest.fixture
def workdays_2(slot_single):
    """Возвращает два рабочих дня с одним слотом каждый."""
    return [
        WorkDay(date=date(2026, 3, 27), is_holiday=False, day_type="четная", available_slots=[slot_single]),
        WorkDay(date=date(2026, 3, 28), is_holiday=False, day_type="четная", available_slots=[slot_single])
    ]


@pytest.fixture
def workdays_list(workday):
    """Возвращает список рабочих дней."""
    return [workday]


# ==================== Фикстуры преподавателей ====================

@pytest.fixture
def teacher():
    """Возвращает тестового преподавателя."""
    return Teacher(id=1, surname="Иванов", name="Иван", patronymic="Иванович",
                   specialization=["Матанализ"], department="ПМиИ")


@pytest.fixture
def teacher_2():
    """Возвращает второго тестового преподавателя."""
    return Teacher(id=2, surname="Петров", name="Петр", patronymic="Петрович",
                   specialization=["Численные методы"], department="ПМиИ")


@pytest.fixture
def teacher_3():
    """Возвращает третьего тестового преподавателя."""
    return Teacher(id=3, surname="Сидоров", name="Сидор", patronymic="Сидорович",
                   specialization=["Информационные технологии"], department="ИВТ")


@pytest.fixture
def teacher_no_patron():
    """Возвращает тестового преподавателя без отчества."""
    return Teacher(id=2, surname="Петров", name="Петр", patronymic="",
                   specialization=[], department="ПМиИ")


@pytest.fixture
def teacher_no_name():
    """Возвращает тестового преподавателя без имени и отчества."""
    return Teacher(id=3, surname="Сидоров", name="", patronymic="",
                   specialization=[], department="ПМиИ")


# ==================== Фикстуры графа ====================

@pytest.fixture
def graph_connected():
    """Возвращает граф, где оба события имеют рёбра."""
    return {1: [(1, date(2026, 3, 27), 1)], 2: [(2, date(2026, 3, 27), 1)]}


@pytest.fixture
def graph_with_isolated():
    """Возвращает граф, где событие 2 отсутствует."""
    return {1: [(1, date(2026, 3, 27), 1)], 3: [(1, date(2026, 3, 27), 2)]}


@pytest.fixture
def graph_single_edge():
    """Возвращает граф только с одним ребром для события 1."""
    return {1: [(1, date(2026, 3, 27), 1)]}


@pytest.fixture
def graph_empty():
    """Возвращает пустой граф."""
    return {}


@pytest.fixture
def graph_with_empty_edges():
    """Возвращает граф, где событие 1 имеет пустой список рёбер."""
    return {1: [], 2: [(1, date(2026, 3, 27), 1)]}


# ==================== Составные фикстуры для примеров ====================

@pytest.fixture
def example_data(groups_list, rooms_list, workday, events_list):
    """Возвращает полный набор данных для примера из главы 2."""
    return {
        "groups": groups_list,
        "rooms": rooms_list,
        "work_days": [workday],
        "events": events_list
    }


@pytest.fixture
def assignment(event, room, slot1):
    """Возвращает тестовое расписание: событие -> (комната, слот)."""
    return {event.id: (room.id, slot1.id)}