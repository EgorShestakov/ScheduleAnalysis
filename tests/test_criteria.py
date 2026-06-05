"""Тесты для модуля criteria.py.

Проверяет критерии существования расписания:
- criterion_one() — первый критерий |E| <= |C|*|T|
- criterion_two() — второй критерий (отсутствие изолированных событий)
"""

import pytest
from src.criteria import criterion_one, criterion_two


class TestCriterionOne:
    """Тесты для функции criterion_one()."""

    def test_criterion_one_valid(self):
        """Проверяет, что при |E| <= |C|*|T| возвращает True."""
        pass

    def test_criterion_one_invalid(self):
        """Проверяет, что при |E| > |C|*|T| возвращает False и выводит рекомендации."""
        pass

    def test_criterion_one_edge_case_equal(self):
        """Проверяет граничный случай |E| == |C|*|T|."""
        pass

    def test_criterion_one_recommendations_format(self):
        """Проверяет, что рекомендации содержат конкретные числа и варианты действий."""
        pass


class TestCriterionTwo:
    """Тесты для функции criterion_two()."""

    def test_criterion_two_all_connected(self):
        """Проверяет, что при отсутствии изолированных событий возвращает True."""
        pass

    def test_criterion_two_isolated_events(self):
        """Проверяет, что при наличии изолированных событий возвращает их список."""
        pass

    def test_criterion_two_conflict_table(self):
        """Проверяет, что таблица причин конфликтов формируется корректно."""
        pass

    def test_criterion_two_empty_graph(self):
        """Проверяет поведение при пустом графе (все события изолированы)."""
        pass
