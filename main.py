import os
import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def resource_path(relative_path: str) -> str:
    """
    Путь к ресурсам, работает и в режиме разработки, и внутри exe.
    Для maps/ используем папку РЯДОМ с exe, а не внутри архива PyInstaller.
    """
    if getattr(sys, "frozen", False):
        # Запущено как exe — берём папку где лежит сам exe
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    # Флаг дебага передаём через переменную окружения —
    # её удобно зашить прямо в exe при сборке
    debug_mode = os.environ.get("ROBOT_SIM_DEBUG", "0") == "1"

    map_path = resource_path(os.path.join("maps", "default.json"))

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow(map_path, debug_bfs=debug_mode)
    window.show()
    sys.exit(app.exec())
