from collections import deque


def bfs(graph_adjacency: dict, start: tuple, end: tuple) -> list[tuple] | None:
    """
    Поиск кратчайшего пути алгоритмом обхода графа вширь.

    Принимает словарь смежности (session_adjacency из Graph), стартовый и конечный узлы.

    Возвращает список узлов от start до end включительно или None если пути нет.
    """
    if start == end:
        return [start]

    # came_from[node] = откуда пришли в node
    # Одновременно служит множеством посещённых узлов
    came_from: dict[tuple, tuple | None] = {start: None}

    queue: deque[tuple] = deque([start])

    while queue:
        current = queue.popleft()

        for neighbor in graph_adjacency.get(current, []):
            if neighbor in came_from:
                continue  # уже посещали

            came_from[neighbor] = current
            queue.append(neighbor)

            if neighbor == end:
                # Нашли финиш
                return _reconstruct_path(came_from, start, end)

    return None  # путь не существует


def _reconstruct_path(came_from: dict, start: tuple, end: tuple) -> list[tuple]:
    """Восстановить путь от end к start по словарю came_from."""
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path
