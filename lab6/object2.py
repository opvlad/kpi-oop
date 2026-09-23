import sys
import random
import socket
from ast import literal_eval

import pyperclip
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Object2")
        self.setGeometry(100, 100, 400, 300)

        clipboard_data = literal_eval(pyperclip.paste())
        required_key = ["nPoint", "xMin", "yMin", "xMax", "yMax"]

        if not all(key in clipboard_data for key in required_key):
            QMessageBox.critical(self, "Не вдалося прочитати параметри з буферу обміну", "")
            return

        self.points = []
        for _ in range(clipboard_data["nPoint"]):
            x = random.randint(clipboard_data["xMin"], clipboard_data["xMax"])
            y = random.randint(clipboard_data["yMin"], clipboard_data["yMax"])
            self.points.append((x, y))
        self.points.sort(key=lambda point: point[0])

        central_widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Згенеровані точки:")
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        points_text = "\n".join([f"({x}, {y})" for x, y in self.points])
        points_label = QLabel(points_text)
        layout.addWidget(points_label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        pyperclip.copy(self.points)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.connect(("localhost", 8000))
            server.sendall(b"points_created") # type: ignore


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.move(100, 500)
    app.exec()
