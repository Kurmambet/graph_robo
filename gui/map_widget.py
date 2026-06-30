from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget

NODE_R_FRAC = 0.18  # радиус узла = CELL * NODE_R_FRAC
ARROW_FRAC = 0.13  # размер стрелки = CELL * ARROW_FRAC
MARGIN_FRAC = 0.6  # отступ от края = CELL * MARGIN_FRAC


class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = None
        self.robot = None
        self.bfs_state = None
        self.path: list = []
        # Разрешаем виджету растягиваться вместе с окном
        self.setMinimumSize(200, 200)

    def set_data(self, graph, robot):
        self.graph = graph
        self.robot = robot
        self.update()

    def set_path(self, path: list):
        self.path = path
        self.update()

    def set_bfs_state(self, state):
        self.bfs_state = state
        self.update()

    # Вычисляем размер клетки динамически под текущий размер виджета
    def _cell_size(self) -> float:
        if self.graph is None:
            return 60.0
        w = self.width()
        h = self.height()
        cell_w = w / (self.graph.cols - 1 + 2 * MARGIN_FRAC)
        cell_h = h / (self.graph.rows - 1 + 2 * MARGIN_FRAC)
        return min(cell_w, cell_h)  # берём меньшее - вся карта влезает

    def _px(self, row, col) -> QPointF:
        cell = self._cell_size()
        margin = cell * MARGIN_FRAC
        x = margin + col * cell
        y = margin + row * cell
        return QPointF(x, y)

    # ------------------------------------------------------------------

    def paintEvent(self, event):
        if self.graph is None:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_edges(p)
        self._draw_path(p)
        self._draw_nodes(p)
        if self.robot:
            self._draw_robot(p)
        p.end()

    def resizeEvent(self, event):
        """При изменении размера окна - перерисовываем карту."""
        super().resizeEvent(event)
        self.update()

    # ------------------------------------------------------------------

    def _draw_edges(self, p: QPainter):
        cell = self._cell_size()
        pen = QPen(QColor("#aaaaaa"), max(1.0, cell * 0.025))
        p.setPen(pen)
        drawn = set()
        for node, neighbors in self.graph.session_adjacency.items():
            for nb in neighbors:
                key = tuple(sorted([node, nb]))
                if key in drawn:
                    continue
                drawn.add(key)
                p.drawLine(self._px(*node), self._px(*nb))

    def _draw_path(self, p: QPainter):
        if len(self.path) < 2:
            return
        cell = self._cell_size()
        pen = QPen(QColor("#2196F3"), max(2.0, cell * 0.07))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        for i in range(len(self.path) - 1):
            p.drawLine(self._px(*self.path[i]), self._px(*self.path[i + 1]))

    def _draw_nodes(self, p: QPainter):
        cell = self._cell_size()
        node_r = cell * NODE_R_FRAC
        font = QFont("Arial", max(6, int(cell * 0.12)))
        p.setFont(font)

        for node in self.graph.nodes:
            pt = self._px(*node)
            cx, cy = pt.x(), pt.y()

            s = self.bfs_state

            if node == self.graph.start:
                color = QColor("#4CAF50")
            elif node == self.graph.end:
                color = QColor("#F44336")
            elif s is not None and s.phase in ("done",) and node in s.path:
                color = QColor("#2196F3")  # финальный маршрут - синий
            elif s is not None and s.phase == "reconstruct" and node in s.path:
                color = QColor("#FF9800")  # восстановление пути - оранжевый
            elif s is not None and node == s.current:
                color = QColor("#9C27B0")  # текущий обрабатываемый - фиолетовый
            elif s is not None and node in s.queue:
                color = QColor("#FFEB3B")  # в очереди (фронт волны) - жёлтый
            elif s is not None and node in s.visited:
                color = QColor("#B3E5FC")  # уже посещён - голубой
            elif self.robot and node == self.robot.pos:
                color = QColor("#FF9800")
            else:
                color = QColor("#ffffff")

            p.setBrush(QBrush(color))
            p.setPen(QPen(QColor("#555555"), max(1.0, cell * 0.02)))
            p.drawEllipse(QPointF(cx, cy), node_r, node_r)

            p.setPen(QPen(QColor("#333333")))
            p.drawText(
                int(cx - node_r * 0.9), int(cy + node_r * 0.45), f"{node[0]},{node[1]}"
            )

    def _draw_robot(self, p: QPainter):
        cell = self._cell_size()
        node_r = cell * NODE_R_FRAC
        arr_sz = cell * ARROW_FRAC

        direction_angle = {"north": 270, "east": 0, "south": 90, "west": 180}
        angle = direction_angle.get(self.robot.direction, 0)

        pt = self._px(*self.robot.pos)
        cx, cy = pt.x(), pt.y()

        p.save()
        p.translate(cx, cy)
        p.rotate(angle)

        arrow = QPolygonF(
            [
                QPointF(node_r + arr_sz, 0),
                QPointF(node_r - 2, -arr_sz * 0.6),
                QPointF(node_r - 2, arr_sz * 0.6),
            ]
        )
        p.setBrush(QBrush(QColor("#1565C0")))
        p.setPen(QPen(QColor("#0D47A1"), 1))
        p.drawPolygon(arrow)
        p.restore()
