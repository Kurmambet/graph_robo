import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow

MAP_PATH = "maps/generated.json"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow(MAP_PATH)
    window.show()
    sys.exit(app.exec())
