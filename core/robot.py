from abc import ABC, abstractmethod


class RobotController(ABC):
    @abstractmethod
    def move_forward(self) -> None: ...

    @abstractmethod
    def turn_left(self) -> None: ...

    @abstractmethod
    def turn_right(self) -> None: ...

    @abstractmethod
    def turn_back(self) -> None: ...


class SimulationController(RobotController):
    def move_forward(self) -> None:
        print("[Robot] move_forward")

    def turn_left(self) -> None:
        print("[Robot] turn_left")

    def turn_right(self) -> None:
        print("[Robot] turn_right")

    def turn_back(self) -> None:
        print("[Robot] turn_back")


# ------------------------------------------------------------------
# Состояние робота
# ------------------------------------------------------------------

CLOCKWISE = ["north", "east", "south", "west"]

# Смещение (row, col) для абсолютного направления
DIRECTION_DELTA = {
    "north": (-1, 0),
    "south": (1, 0),
    "east": (0, 1),
    "west": (0, -1),
}


class Robot:
    """
    Хранит позицию и направление робота.
    Вычисляет нужные команды контроллеру при каждом шаге.
    """

    def __init__(
        self, start_pos: tuple, start_direction: str, controller: RobotController
    ):
        self.pos: tuple = start_pos
        self.direction: str = start_direction  # "north"|"south"|"east"|"west"
        self.controller = controller
        self.path: list[tuple] = []  # текущий маршрут (включая pos)
        self.path_index: int = 0  # индекс следующей цели в path

    def set_path(self, path: list[tuple]) -> None:
        """Установить новый маршрут. path[0] должен совпадать с self.pos."""
        self.path = path
        self.path_index = 1  # 0-й элемент - текущая позиция

    def has_next_step(self) -> bool:
        return self.path_index < len(self.path)

    def is_at_goal(self, end: tuple) -> bool:
        return self.pos == end

    def step(self) -> tuple | None:
        """
        Выполнить один шаг по маршруту: повернуть (если нужно) и проехать вперёд.
        Возвращает новую позицию или None если маршрут закончился.
        """
        if not self.has_next_step():
            return None

        target = self.path[self.path_index]
        needed_direction = self._direction_to(self.pos, target)

        self._rotate_to(needed_direction)

        self.controller.move_forward()
        self.pos = target
        self.path_index += 1

        return self.pos

    # Вспомогательные
    def _direction_to(self, from_pos: tuple, to_pos: tuple) -> str:
        """Определить абсолютное направление от from_pos к to_pos."""
        dr = to_pos[0] - from_pos[0]
        dc = to_pos[1] - from_pos[1]
        for direction, (r, c) in DIRECTION_DELTA.items():
            if r == dr and c == dc:
                return direction
        raise ValueError(f"Узлы {from_pos} и {to_pos} не являются соседями")

    def _rotate_to(self, target_direction: str) -> None:
        """Повернуть робота к target_direction минимальным числом поворотов."""
        current_idx = CLOCKWISE.index(self.direction)
        target_idx = CLOCKWISE.index(target_direction)

        diff = (target_idx - current_idx) % 4

        if diff == 0:
            pass  # уже смотрим в нужную сторону
        elif diff == 1:
            self.controller.turn_right()
        elif diff == 3:
            self.controller.turn_left()
        elif diff == 2:
            self.controller.turn_back()

        self.direction = target_direction
