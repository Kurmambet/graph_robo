import copy
import json


class Graph:
    """
    Хранит два слоя карты:
    - _base_adjacency  : исходная карта, read-only, не меняется никогда
    - session_adjacency: рабочая копия текущей сессии, мутируется при получении QR
    """

    def __init__(self):
        self._base_adjacency: dict[tuple, list[tuple]] = {}
        self.session_adjacency: dict[tuple, list[tuple]] = {}
        self.nodes: set[tuple] = set()
        self.start: tuple = (0, 0)
        self.end: tuple = (0, 0)
        self.start_direction: str = "east"
        self.rows: int = 0
        self.cols: int = 0

    def load_from_file(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._parse(data)

    def load_from_dict(self, data: dict) -> None:
        self._parse(data)

    def _parse(self, data: dict) -> None:
        self.rows = data["rows"]
        self.cols = data["cols"]
        self.start = tuple(data["start"])
        self.end = tuple(data["end"])
        self.start_direction = data.get("start_direction", "east")

        self.nodes = {tuple(n) for n in data["nodes"]}

        self._base_adjacency = {node: [] for node in self.nodes}
        for edge in data["edges"]:
            a, b = tuple(edge[0]), tuple(edge[1])
            # граф ненаправленный
            self._base_adjacency[a].append(b)  # {(0,0): [(0,1), (1,0)],}
            self._base_adjacency[b].append(a)  # в обратном направлении

        self.reset_session()

    def reset_session(self) -> None:
        """Сбросить рабочую копию до исходной карты."""
        self.session_adjacency = copy.deepcopy(self._base_adjacency)

    # ------------------------------------------------------------------
    # Мутации сессии (вызываются после считывания QR)
    # ------------------------------------------------------------------

    def remove_edge(self, a: tuple, b: tuple) -> None:
        """Удалить ребро между a и b из рабочей копии."""
        if b in self.session_adjacency.get(a, []):
            self.session_adjacency[a].remove(b)
        if a in self.session_adjacency.get(b, []):
            self.session_adjacency[b].remove(a)

    def apply_qr_command(
        self, current_pos: tuple, robot_direction: str, qr_data: dict
    ) -> None:
        """
        qr_data: {"forward": bool, "back": bool, "left": bool, "right": bool}

        Удаляем из session_adjacency все рёбра из current_pos,
        которые соответствуют направлениям с False.

        robot_direction: "north" | "south" | "east" | "west"
        """
        # абсолютное направление -> смещение (row, col)
        direction_to_delta = {
            "north": (-1, 0),
            "south": (1, 0),
            "east": (0, 1),
            "west": (0, -1),
        }

        relative_to_absolute = _build_relative_map(robot_direction)

        for relative_dir, is_open in qr_data.items():
            if is_open:
                continue  # путь открыт - ничего не удаляем

            abs_dir = relative_to_absolute.get(relative_dir)
            if abs_dir is None:
                continue

            delta = direction_to_delta[abs_dir]
            neighbor = (current_pos[0] + delta[0], current_pos[1] + delta[1])

            if neighbor in self.nodes:
                self.remove_edge(current_pos, neighbor)

    def get_neighbors(self, node: tuple) -> list[tuple]:
        return self.session_adjacency.get(node, [])

    def has_node(self, node: tuple) -> bool:
        return node in self.nodes


def _build_relative_map(facing: str) -> dict[str, str]:
    """
    Cтроит карту относительных направлений.

    Возвращает словарь {relative: absolute} для текущей ориентации робота.

    Логика поворота:
        facing east  -> forward=east,  back=west,  left=north, right=south
        facing west  -> forward=west,  back=east,  left=south, right=north
        facing north -> forward=north, back=south, left=west,  right=east
        facing south -> forward=south, back=north, left=east,  right=west
    """
    # Порядок по часовой: n > e > s > w
    clockwise = ["north", "east", "south", "west"]
    idx = clockwise.index(facing)

    return {
        "forward": clockwise[idx],
        "right": clockwise[(idx + 1) % 4],
        "back": clockwise[(idx + 2) % 4],
        "left": clockwise[(idx + 3) % 4],
    }
