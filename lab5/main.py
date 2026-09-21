import sys  # noqa
from typing import Type

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenuBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QPen, QColor, QPainter, QIcon, QPalette

from shape_tools import Tool, TOOLS, ToolBase
from shape_table import ShapeWindow
from repository import shape_repo


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.pen = QPen(QColor("red"), 3, Qt.PenStyle.DashLine)

        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("white"))
        self.setPalette(palette)

        self.current_tool_class = TOOLS[Tool.FREEHAND]
        self.active_tool = None

    def mousePressEvent(self, event):
        if self.current_tool_class and event.button() == Qt.MouseButton.LeftButton:
            self.active_tool = self.current_tool_class()
            self.active_tool.press(self, event.position().toPoint())

    def mouseMoveEvent(self, event):
        if self.active_tool and event.buttons() == Qt.MouseButton.LeftButton:
            self.active_tool.move(self, event.position().toPoint())

    def mouseReleaseEvent(self, event):
        if self.active_tool and event.button() == Qt.MouseButton.LeftButton:
            self.active_tool.release(self, shape_repo, event.position().toPoint())
            self.active_tool = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen)

        ToolBase.draw_finished(shape_repo, painter)

        if self.active_tool:
            self.active_tool.draw_preview(self, painter)


class ObjectsAction(QAction):
    action_group = None

    def __init__(self, text: str, parent, tool_class: Type[ToolBase], tip: str):
        super().__init__(text, parent)
        self._create_action_group(parent)
        self.setCheckable(True)
        self.setActionGroup(self.action_group)
        self.setToolTip(tip)

        self.tool_class = tool_class
        self.triggered.connect(parent.set_current_tool)

    @classmethod
    def _create_action_group(cls, parent):
        if cls.action_group is None:
            cls.action_group = QActionGroup(parent)


class ObjectsMenu:
    def __init__(self, menubar: QMenuBar):
        self.menu = menubar.addMenu("Об’єкти")

    def add_actions(self, actions: list[QAction]):
        for action in actions:
            self.menu.addAction(action)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 5")
        self.resize(800, 600)

        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

        self.table_window = None
        # self.show_table_window()

        self._create_actions()
        self._create_menubar()
        self._create_toolbars()

    def set_current_tool(self):
        for action in self.objects_menu.menu.actions():
            if action.isChecked() and isinstance(action, ObjectsAction):
                self.canvas.current_tool_class = action.tool_class

    def show_table_window(self):
        if self.table_window is None:
            self.table_window = ShapeWindow()

        self.table_window.show()

        self.table_window.raise_()
        self.table_window.activateWindow()

    def hide_table_window(self):
        if self.table_window:
            self.table_window.hide()

    def closeEvent(self, event) -> None:
        if self.table_window:
            self.table_window.close()
        event.accept()

    def _create_actions(self):
        self.point_action = ObjectsAction(
            "Крапка", self, TOOLS[Tool.FREEHAND], "Олівець"
        )
        self.point_action.setChecked(True)
        self.line_action = ObjectsAction(
            "Лінія", self, TOOLS[Tool.LINE], "Намалювати лінію"
        )
        self.rectangle_action = ObjectsAction(
            "Прямокутник", self, TOOLS[Tool.RECTANGLE], "Намалювати прямокутник"
        )
        self.ellipse_action = ObjectsAction(
            "Еліпс", self, TOOLS[Tool.ELLIPSE], "Намалювати еліпс"
        )
        self.line_with_circles_action = ObjectsAction(
            "Лінія з кружечками",
            self,
            TOOLS[Tool.LINE_WITH_CIRCLES],
            "Намалювати лінію з кружечками",
        )
        self.cube_action = ObjectsAction(
            "Куб", self, TOOLS[Tool.CUBE], "Намалювати каркас куба"
        )
        self.point_action.setIcon(QIcon("../icons/pencil.svg"))
        self.line_action.setIcon(QIcon("../icons/minus.svg"))
        self.rectangle_action.setIcon(QIcon("../icons/rectangle.svg"))
        self.ellipse_action.setIcon(QIcon("../icons/ellipse.svg"))
        self.line_with_circles_action.setIcon(QIcon("../icons/linewithcircles.png"))
        self.cube_action.setIcon(QIcon("../icons/box.svg"))

        self.open_table_action = QAction(
            "Відкрити таблицю", self, toolTip="Відкрити таблицю фігур"
        )
        self.open_table_action.setShortcut("Ctrl+T")
        self.open_table_action.triggered.connect(self.show_table_window)

        self.hide_table_action = QAction(
            "Закрити таблицю", self, toolTip="Закрити таблицю фігур"
        )
        self.hide_table_action.triggered.connect(self.hide_table_window)

    def _create_menubar(self):
        menubar = self.menuBar()

        self.file_menu = menubar.addMenu("Файл")
        self.objects_menu = ObjectsMenu(menubar)
        help_menu = menubar.addMenu("Довідка")  # noqa

        self.objects_menu.add_actions(
            [
                self.point_action,
                self.line_action,
                self.rectangle_action,
                self.ellipse_action,
                self.line_with_circles_action,
                self.cube_action,
            ]
        )
        self.file_menu.addAction(self.open_table_action)
        self.file_menu.addAction(self.hide_table_action)

    def _create_toolbars(self):
        toolbar = self.addToolBar("Shapes")

        toolbar.addAction(self.point_action)
        toolbar.addAction(self.line_action)
        toolbar.addAction(self.rectangle_action)
        toolbar.addAction(self.ellipse_action)
        toolbar.addAction(self.line_with_circles_action)
        toolbar.addAction(self.cube_action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
