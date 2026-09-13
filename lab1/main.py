import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from module1 import ask_group
from module2 import ask_value


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 1")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        self.data_label = QLabel("data", alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.data_label)
        central_widget.setLayout(layout)

        self.__create_menubar()

    def __handle_action1(self) -> None:
        ask_group(self)

    def __handle_action2(self) -> None:
        ask_value(self)

    def __create_menubar(self):
        menubar = self.menuBar()

        main_menu = menubar.addMenu("Main Menu")

        action1 = QAction("Action 1", self)
        action1.triggered.connect(self.__handle_action1)
        main_menu.addAction(action1)

        action2 = QAction("Action 2", self)
        action2.triggered.connect(self.__handle_action2)
        main_menu.addAction(action2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
