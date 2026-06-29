import json
import os
import random
from collections import deque

ROWS = 12
COLS = 15

START = [0, 0]  # стартовый узел [row, col]
END = [ROWS - 1, COLS - 1]  # финишный узел  [row, col]
START_DIR = "east"  # начальное направление робота
# ("north" | "south" | "east" | "west")

# Вероятность того, что ребро между соседними узлами СУЩЕСТВУЕТ (0.0 – 1.0)
# При 1.0 — полная сетка
EDGE_PROB = 0.75

# Гарантировать существование пути от START до END?
# Если True — после генерации проверяем BFS и при необходимости
# досыпаем рёбра вдоль одного из кратчайших путей
ENSURE_PATH = True

# Вероятность того, что узел сетки вообще существует (0.0 – 1.0)
# При 1.0 — все клетки сетки заняты узлами
# START и END всегда существуют независимо от этого параметра
NODE_PROB = 0.90

OUTPUT_FILE = "maps/generated.json"  # куда сохранить результат

RANDOM_SEED = None  # int для воспроизводимости, None — каждый раз новая карта

# ============================================================

random.seed(RANDOM_SEED)

# ------------------------------------------------------------------
# 1. Генерация узлов
# ------------------------------------------------------------------
all_coords = [(r, c) for r in range(ROWS) for c in range(COLS)]

nodes = set()
for coord in all_coords:
    if coord == tuple(START) or coord == tuple(END):
        nodes.add(coord)  # старт и финиш всегда есть
    elif random.random() < NODE_PROB:
        nodes.add(coord)


# ------------------------------------------------------------------
# 2. Генерация рёбер
# ------------------------------------------------------------------
def neighbors_of(r, c):
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if (nr, nc) in nodes:
            yield (nr, nc)


edges_set = set()

for node in nodes:
    for nb in neighbors_of(*node):
        key = tuple(sorted([node, nb]))
        if key in edges_set:
            continue
        if random.random() < EDGE_PROB:
            edges_set.add(key)

# ------------------------------------------------------------------
# 3. Убираем изолированные узлы (кроме старта и финиша)
# ------------------------------------------------------------------
adjacency = {n: [] for n in nodes}
for a, b in edges_set:
    adjacency[a].append(b)
    adjacency[b].append(a)

isolated = {
    n for n in nodes if len(adjacency[n]) == 0 and n != tuple(START) and n != tuple(END)
}
nodes -= isolated
for n in isolated:
    del adjacency[n]


# ------------------------------------------------------------------
# 4. BFS для проверки/восстановления пути
# ------------------------------------------------------------------
def bfs(adj, start, end):
    start, end = tuple(start), tuple(end)
    if start not in adj:
        return None
    came_from = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        if cur == end:
            path, node = [], end
            while node is not None:
                path.append(node)
                node = came_from[node]
            return list(reversed(path))
        for nb in adj.get(cur, []):
            if nb not in came_from:
                came_from[nb] = cur
                queue.append(nb)
    return None


def add_edge(adj, a, b):
    edges_set.add(tuple(sorted([a, b])))
    adj[a].append(b)
    adj[b].append(a)


# ------------------------------------------------------------------
# 5. Гарантия пути (если ENSURE_PATH)
# ------------------------------------------------------------------
if ENSURE_PATH:
    path = bfs(adjacency, START, END)
    if path is None:
        # Прокладываем путь по прямой: сначала по строкам, потом по столбцам
        sr, sc = START
        er, ec = END
        waypoints = []
        r, c = sr, sc
        while r != er:
            r += 1 if er > sr else -1
            wp = (r, c)
            if wp not in nodes:
                nodes.add(wp)
                adjacency[wp] = []
            waypoints.append(wp)
        while c != ec:
            c += 1 if ec > sc else -1
            wp = (r, c)
            if wp not in nodes:
                nodes.add(wp)
                adjacency[wp] = []
            waypoints.append(wp)

        route = [tuple(START)] + waypoints
        for i in range(len(route) - 1):
            a, b = route[i], route[i + 1]
            if b not in adjacency[a]:
                add_edge(adjacency, a, b)

        print("  [!] Путь не найден — проложен принудительный маршрут")
    else:
        print(
            f"  [ok] Путь существует, длина {len(path) - 1} хопов: "
            f"{' -> '.join(str(n) for n in path)}"
        )

# ------------------------------------------------------------------
# 6. Сборка JSON
# ------------------------------------------------------------------
edges_list = [list(map(list, edge)) for edge in sorted(edges_set)]
nodes_list = sorted(map(list, nodes))

data = {
    "rows": ROWS,
    "cols": COLS,
    "start": START,
    "end": END,
    "start_direction": START_DIR,
    "nodes": nodes_list,
    "edges": edges_list,
}

os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)


def compact_json(data) -> str:
    """Массивы из двух чисел пишем в одну строку, остальное — стандартный indent=2."""
    import re

    raw = json.dumps(data, indent=2, ensure_ascii=False)
    # Схлопываем двухэлементные числовые массивы [ \n  X, \n  Y \n] → [X, Y]
    raw = re.sub(r"\[\s*(-?\d+),\s*(-?\d+)\s*\]", r"[\1, \2]", raw)
    return raw


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(compact_json(data))

print(f"\n  Узлов : {len(nodes_list)}")
print(f"  Рёбер : {len(edges_list)}")
print(f"  Файл  : {OUTPUT_FILE}")
