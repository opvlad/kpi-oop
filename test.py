import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QInputDialog,
    QLineEdit,
    QStatusBar,
)

from PySide6.QtGui import QFont


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 1")
        self.resize(800, 600)
        self.setMouseTracking(True)

        self.__open_action = None
        self.__save_action = None
        self.__exit_action = None
        self.__zoom_in_action = None
        self.__zoom_out_action = None

        central_widget = QWidget()
        central_widget.setMouseTracking(True)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.addWidget(
            QLabel("Main content area"), alignment=Qt.AlignmentFlag.AlignCenter
        )
        central_widget.setLayout(layout)

        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()

    def mouseMoveEvent(self, event) -> None:
        x = int(event.position().x())
        y = int(event.position().y())
        self.label_position.setText(f"x: {x}, y: {y}")

    def _create_actions(self):
        def __handle_open_file():
            status_bar = self.statusBar()
            status_bar.showMessage("File opened", 1000)

        def __handle_save_file():
            status_bar = self.statusBar()
            status_bar.showMessage("File saved", 1000)

        def __handle_zoom_in_action():
            pass

        def __handle_zoom_out_action():
            pass

        self.__open_action = QAction("&Open", self)
        self.__open_action.setShortcut("Ctrl+O")
        self.__open_action.setStatusTip("Open existing file")
        self.__open_action.triggered.connect(__handle_open_file)

        self.__save_action = QAction("&Save", self)
        self.__save_action.setShortcut("Ctrl+S")
        self.__save_action.setStatusTip("Save file")
        self.__save_action.triggered.connect(__handle_save_file)

        self.__exit_action = QAction("E&xit", self)
        self.__exit_action.setShortcut("Ctrl+Q")
        self.__exit_action.setStatusTip("Exit application")
        self.__exit_action.triggered.connect(self.close)

        view_group = QActionGroup(self)

        self.__zoom_in_action = QAction("Zoom &In", self)
        self.__zoom_in_action.setShortcut("Ctrl+=")
        self.__zoom_in_action.setCheckable(True)
        self.__zoom_in_action.setActionGroup(view_group)
        self.__zoom_in_action.triggered.connect(__handle_zoom_in_action)

        self.__zoom_out_action = QAction("Zoom &Out", self)
        self.__zoom_out_action.setShortcut("Ctrl+-")
        self.__zoom_out_action.setCheckable(True)
        self.__zoom_out_action.setActionGroup(view_group)
        self.__zoom_out_action.triggered.connect(__handle_zoom_out_action)

    def _create_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.__open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.__save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.__exit_action)

        edit_menu = menubar.addMenu("&Edit")
        help_menu = menubar.addMenu("&Help")

        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.__zoom_in_action)
        view_menu.addAction(self.__zoom_out_action)

    def _create_toolbars(self):
        toolbar = self.addToolBar("File")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        toolbar.addAction(self.__open_action)
        toolbar.addSeparator()
        toolbar.addAction(self.__save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.__exit_action)

        toolbar.setMovable(True)
        toolbar.setFloatable(True)

    def _create_status_bar(self):
        status_bar = self.statusBar()

        status_bar.showMessage("Application started", 3000)

        self.label_position = QLabel("x: 0, y: 0")
        status_bar.addPermanentWidget(self.label_position)


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
