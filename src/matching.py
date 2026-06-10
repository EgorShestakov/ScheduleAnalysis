"""Поиск максимального паросочетания (алгоритм Куна)."""

from typing import Dict, Any, List


def max_bipartite_matching(graph: Dict[int, List[Any]], left_nodes: List[int], right_nodes: List[Any]) -> Dict[
    Any, int]:
    """
    Возвращает максимальное паросочетание в двудольном графе.
    Реализация алгоритма Куна (DFS).

    :param graph: словарь смежности {event_id: [slot_key1, slot_key2, ...]}
    :param left_nodes: список левых вершин (событий)
    :param right_nodes: список правых вершин (слотов)
    :return: словарь соответствий {right_node: left_node} (слот -> событие)
    """
    # Словарь для хранения соответствия правой вершины левой
    match_right = {}

    def dfs(left_node: int, visited: set) -> bool:
        """
        Рекурсивный поиск увеличивающей цепи.
        Возвращает True, если удалось найти свободную правую вершину или перестроить паросочетание.
        """
        for right_node in graph.get(left_node, []):
            if right_node not in visited:
                visited.add(right_node)
                # Если правая вершина свободна или можно перестроить паросочетание
                if right_node not in match_right or dfs(match_right[right_node], visited):
                    match_right[right_node] = left_node
                    return True
        return False

    # Пытаемся найти увеличивающую цепь для каждой левой вершины
    for left_node in left_nodes:
        dfs(left_node, set())

    # Возвращаем словарь {right_node: left_node}
    return match_right


def is_perfect(matching: Dict[Any, int], num_events: int) -> bool:
    """
    Проверяет, является ли паросочетание совершенным.

    :param matching: словарь соответствий {right_node: left_node}
    :param num_events: количество событий (левых вершин)
    :return: True если все левые вершины покрыты, иначе False
    """
    # Получаем множество всех левых вершин, участвующих в паросочетании
    matched_left = set(matching.values())
    # Совершенным считается паросочетание, покрывающее все левые вершины
    return len(matched_left) == num_events