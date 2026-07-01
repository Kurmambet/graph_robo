from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.graph import Graph
from core.pathfinder import bfs, bfs_step_by_step
from core.robot import Robot, SimulationController
from gui.map_widget import MapWidget
from qr.scanner import scan_qr_once

# DEBUG_BFS = True


class MainWindow(QMainWindow):
    def __init__(self, map_path: str, debug_bfs: bool = False):
        super().__init__()
        self.debug_bfs = debug_bfs
        self.setWindowTitle("Robot Graph Simulation")
        self.map_path = map_path

        self.graph = Graph()
        self.graph.load_from_file(map_path)

        self.robot: Robot | None = None
        self.current_path: list = []

        self._bfs_gen = None
        self._bfs_state = None

        self._build_ui()
        self._start_session()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(12, 12, 12, 12)

        # Карта в прокручиваемой области
        self.map_widget = MapWidget()

        root.addWidget(self.map_widget, stretch=1)

        # Статус
        self.status_label = QLabel("Инициализация...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; padding: 4px;")
        root.addWidget(self.status_label)

        # Кнопки
        btn_row = QHBoxLayout()
        self.btn_continue = QPushButton("Продолжить (без изменений)")
        self.btn_scan = QPushButton("Сканировать QR")
        self.btn_restart = QPushButton("Рестарт")
        self.btn_bfs_step = QPushButton("Шаг BFS")

        self.btn_bfs_step.setMinimumHeight(36)
        self.btn_bfs_step.setEnabled(False)
        self.btn_bfs_step.clicked.connect(self._on_bfs_step)
        btn_row.addWidget(self.btn_bfs_step)

        if not self.debug_bfs:
            self.btn_bfs_step.setVisible(False)

        self.btn_continue.setEnabled(False)
        self.btn_scan.setEnabled(False)

        self.btn_continue.clicked.connect(self._on_continue)
        self.btn_scan.clicked.connect(self._on_scan_qr)
        self.btn_restart.clicked.connect(self._start_session)

        for btn in (self.btn_continue, self.btn_scan, self.btn_restart):
            btn.setMinimumHeight(36)
            btn_row.addWidget(btn)

        root.addLayout(btn_row)
        self.resize(900, 700)

    # ------------------------------------------------------------------
    # Сессия
    # ------------------------------------------------------------------

    def _start_session(self):
        self.graph.reset_session()
        controller = SimulationController()
        self.robot = Robot(self.graph.start, self.graph.start_direction, controller)

        self.map_widget.set_data(self.graph, self.robot)

        ok = self._rebuild_path()
        if not ok:
            return

        self._refresh()
        if self.debug_bfs:
            self._start_bfs_debug()
            self._set_waiting(False)
        else:
            self._set_waiting(True)

    # ------------------------------------------------------------------
    # Логика шага
    # ------------------------------------------------------------------

    def _on_continue(self):
        """Продолжить без изменений - просто делаем шаг."""
        self._do_step()

    def _on_scan_qr(self):
        """Сканируем QR, применяем команду, перестраиваем маршрут, делаем шаг."""
        self._set_status("наведите QR-код")
        qr_data = scan_qr_once()

        if qr_data is None:
            self._set_status("QR не распознан. Попробуйте ещё раз.")
            return

        self.graph.apply_qr_command(self.robot.pos, self.robot.direction, qr_data)

        ok = self._rebuild_path()
        if not ok:
            return  # ошибка уже показана в _rebuild_path

        self._do_step()

    def _do_step(self):
        """Сделать один шаг робота и обновить GUI."""
        self._set_waiting(False)

        if not self.robot.has_next_step():
            self._set_status("Маршрут завершён.")
            return

        self.robot.step()
        self._refresh()

        if self.robot.is_at_goal(self.graph.end):
            self._set_status("Робот достиг финиша!")
            self._set_waiting(False)
            QMessageBox.information(self, "Финиш!", "Робот достиг конечной точки.")
            return

        # Перестраиваем от новой позиции (вдруг маршрут стал короче/длиннее)
        ok = self._rebuild_path()
        if not ok:
            return

        self._set_waiting(True)

    def _rebuild_path(self) -> bool:
        """Запустить BFS от текущей позиции. Вернуть False если пути нет."""
        path = bfs(self.graph.session_adjacency, self.robot.pos, self.graph.end)

        if path is None:
            self._set_status("Путь до финиша не существует!")
            self.current_path = []
            self.map_widget.set_path([])
            self._set_waiting(False)
            QMessageBox.warning(
                self, "Тупик", "Пути до финиша не существует.\nМожно сделать рестарт."
            )
            return False

        self.current_path = path
        self.robot.set_path(path)
        self.map_widget.set_path(path)
        return True

    # ------------------------------------------------------------------
    # BFS DEBUG
    # ------------------------------------------------------------------

    def _start_bfs_debug(self):
        """Запустить пошаговый BFS от текущей позиции."""
        self._bfs_gen = bfs_step_by_step(
            self.graph.session_adjacency, self.robot.pos, self.graph.end
        )
        self.btn_bfs_step.setEnabled(True)
        self._on_bfs_step()  # показать начальное состояние сразу

    def _on_bfs_step(self):
        """Один шаг генератора BFS."""
        if self._bfs_gen is None:
            return
        try:
            state = next(self._bfs_gen)
            self._bfs_state = state
            self.map_widget.set_bfs_state(state)
            self._print_bfs_console(state)

            if state.phase in ("done", "no_path"):
                self.btn_bfs_step.setEnabled(False)
                if state.phase == "done":
                    self._set_status(f"BFS завершён. Путь: {len(state.path) - 1} хопов")
                    # передаём найденный путь роботу
                    self.current_path = state.path
                    self.robot.set_path(state.path)
                    self.map_widget.set_path(state.path)
                else:
                    self._set_status("BFS: путь не найден")
        except StopIteration:
            self.btn_bfs_step.setEnabled(False)

    def _print_bfs_console(self, state):
        """Вывод текущего состояния BFS в консоль."""
        import os

        os.system("cls" if os.name == "nt" else "clear")

        q_list = list(state.queue)
        cf_items = [(k, v) for k, v in state.came_from.items() if v is not None]

        print("-" * 48)
        print(f"  BFS DEBUG  |  фаза: {state.phase.upper()}")
        print("-" * 48)
        print(f"  ТЕКУЩИЙ    : {state.current}")
        print(f"  ОЧЕРЕДЬ    : {q_list}")
        print(f"  ПОСЕЩЕНО   : {sorted(state.visited)}")
        print(f"  ПУТЬ       : {state.path if state.path else '-'}")
        print()
        print("  came_from:")
        for node, parent in sorted(cf_items):
            print(f"    {node} <- {parent}")
        print("-" * 48)

    # ------------------------------------------------------------------
    # Вспомогательное
    # ------------------------------------------------------------------

    def _refresh(self):
        self.map_widget.set_data(self.graph, self.robot)
        self.map_widget.update()

    def _set_waiting(self, waiting: bool):
        self.btn_continue.setEnabled(waiting)
        self.btn_scan.setEnabled(waiting)

    def _set_status(self, text: str):
        self.status_label.setText(text)
