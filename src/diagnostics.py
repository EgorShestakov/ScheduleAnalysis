"""Диагностика ограничений (тактический уровень)."""

def build_graph_without_capacity(*args, **kwargs):
    """Строит граф H3 без ограничения вместимости (только оснащённость)."""
    pass

def build_graph_without_features(*args, **kwargs):
    """Строит граф H2 без ограничения оснащённости (только вместимость)."""
    pass

def build_full_graph(*args, **kwargs):
    """Строит полносвязный граф H4."""
    pass

def classify_edges(*args, **kwargs):
    """
    Классифицирует рёбра по множествам EQ, CAP, ALL.
    Возвращает (EQ, CAP, ALL).
    """
    pass

def generate_recommendations(*args, **kwargs) -> str:
    """На основе EQ, CAP, ALL формирует текстовые рекомендации."""
    pass
