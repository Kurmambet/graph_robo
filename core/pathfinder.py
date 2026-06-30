from collections import deque
from dataclasses import dataclass


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


@dataclass
class BFSState:
    queue: deque
    came_from: dict
    visited: set
    current: tuple | None
    phase: str  # "search" | "reconstruct" | "done" | "no_path"
    path: list  # заполняется в фазе reconstruct


def bfs_step_by_step(graph_adjacency: dict, start: tuple, end: tuple):
    """
    Генератор: каждый yield - одна итерация BFS.
    Вызывающий код делает next() и получает BFSState.
    """
    state = BFSState(
        queue=deque([start]),
        came_from={start: None},
        visited=set(),
        current=None,
        phase="search",
        path=[],
    )
    yield state  # начальное состояние до первого шага

    # --- фаза поиска ---
    while state.queue:
        current = state.queue.popleft()
        state.current = current
        state.visited.add(current)

        if current == end:
            state.phase = "reconstruct"
            yield state
            # --- фаза восстановления пути ---
            node = end
            while node is not None:
                state.path.append(node)
                node = state.came_from[node]
            state.path.reverse()
            # отдаём по одному узлу пути
            for i in range(1, len(state.path) + 1):
                state.current = state.path[i - 1]
                yield state  # path[:i] уже в state.path, но рисуем до i
            state.phase = "done"
            state.current = None
            yield state
            return

        for neighbor in graph_adjacency.get(current, []):
            if neighbor not in state.came_from:
                state.came_from[neighbor] = current
                state.queue.append(neighbor)

        yield state

    # дошли сюда - пути нет
    state.phase = "no_path"
    state.current = None
    yield state
