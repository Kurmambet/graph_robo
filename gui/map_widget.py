from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget

CELL = 80  # пикселей на клетку
MARGIN = 40  # отступ от края
NODE_R = 14  # радиус узла
ARROW_SIZE = 10  # размер стрелки робота


class MapWidget(QWidget):
    """
    Отрисовка графа и робота.
    Перерисовывается вызовом update() снаружи.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = None  # core.graph.Graph
        self.robot = None  # core.robot.Robot
        self.path: list = []  # текущий маршрут

    def set_data(self, graph, robot):
        self.graph = graph
        self.robot = robot
        self.update()

    def set_path(self, path: list):
        self.path = path
        self.update()

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

    # ------------------------------------------------------------------
    # Вспомогательное: перевод координат сетки → пиксели

    def _px(self, row, col) -> QPointF:
        x = MARGIN + col * CELL
        y = MARGIN + row * CELL
        return QPointF(x, y)

    # ------------------------------------------------------------------

    def _draw_edges(self, p: QPainter):
        """Рисуем все рёбра рабочей сессии."""
        pen = QPen(QColor("#aaaaaa"), 2)
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
        """Выделяем маршрут толстой цветной линией."""
        if len(self.path) < 2:
            return

        pen = QPen(QColor("#2196F3"), 5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)

        for i in range(len(self.path) - 1):
            p.drawLine(self._px(*self.path[i]), self._px(*self.path[i + 1]))

    def _draw_nodes(self, p: QPainter):
        """Рисуем узлы. Старт=зелёный, финиш=красный, остальные=белые."""
        for node in self.graph.nodes:
            cx, cy = self._px(*node).x(), self._px(*node).y()

            if node == self.graph.start:
                color = QColor("#4CAF50")
            elif node == self.graph.end:
                color = QColor("#F44336")
            elif self.robot and node == self.robot.pos:
                color = QColor("#FF9800")
            else:
                color = QColor("#ffffff")

            p.setBrush(QBrush(color))
            p.setPen(QPen(QColor("#555555"), 1.5))
            p.drawEllipse(QPointF(cx, cy), NODE_R, NODE_R)

            # Координата подписью
            font = QFont("Arial", 7)
            p.setFont(font)
            p.setPen(QPen(QColor("#333333")))
            p.drawText(int(cx) - 12, int(cy) + 4, f"{node[0]},{node[1]}")

    def _draw_robot(self, p: QPainter):
        """Рисуем стрелку робота поверх его узла."""
        direction_angle = {
            "north": 270,
            "east": 0,
            "south": 90,
            "west": 180,
        }
        angle = direction_angle.get(self.robot.direction, 0)

        cx, cy = self._px(*self.robot.pos).x(), self._px(*self.robot.pos).y()

        p.save()
        p.translate(cx, cy)
        p.rotate(angle)

        # Стрелка → треугольник
        arrow = QPolygonF(
            [
                QPointF(NODE_R + ARROW_SIZE, 0),
                QPointF(NODE_R - 2, -6),
                QPointF(NODE_R - 2, 6),
            ]
        )
        p.setBrush(QBrush(QColor("#1565C0")))
        p.setPen(QPen(QColor("#0D47A1"), 1))
        p.drawPolygon(arrow)

        p.restore()

    # ------------------------------------------------------------------

    def sizeHint(self):
        from PyQt6.QtCore import QSize

        if self.graph is None:
            return QSize(400, 400)
        w = MARGIN * 2 + (self.graph.cols - 1) * CELL
        h = MARGIN * 2 + (self.graph.rows - 1) * CELL
        return QSize(w, h)
