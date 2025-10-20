def heuristic(state, goal):
    """Heurística entre dos estados (state, goal)."""
    x1, y1 = state
    x2, y2 = goal
    return abs(x2 - x1) + abs(y2 - y1)