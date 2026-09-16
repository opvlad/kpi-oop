import sys
from typing import Type

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenuBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QPen, QColor, QPainter

from shape_tools import Tool, TOOLS, ToolBase


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.strokes = []
        self.pen = QPen(QColor("black"), 3)

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
            self.active_tool.release(self, event.position().toPoint())
            self.active_tool = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen)

        ToolBase.draw_finished(self, painter)

        if self.active_tool:
            self.active_tool.draw_preview(self, painter)


class ObjectsAction(QAction):
    action_group = None

    def __init__(self, text: str, parent, tool_class: Type[ToolBase]):
        super().__init__(text, parent)
        self._create_action_group(parent)
        self.setCheckable(True)
        self.setActionGroup(self.action_group)

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
        self.setWindowTitle("Lab 3")
        self.resize(800, 600)

        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

        self._create_menubar()

    def set_current_tool(self):
        for action in self.objects_menu.menu.actions():
            if action.isChecked() and isinstance(action, ObjectsAction):
                self.canvas.current_tool_class = action.tool_class

    def _create_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")
        self.objects_menu = ObjectsMenu(menubar)
        help_menu = menubar.addMenu("Довідка")

        self.point_action = ObjectsAction("Крапка", self, TOOLS[Tool.FREEHAND])
        self.point_action.setChecked(True)
        self.line_action = ObjectsAction("Лінія", self, TOOLS[Tool.LINE])
        self.rectangle_action = ObjectsAction(
            "Прямокутник", self, TOOLS[Tool.RECTANGLE]
        )
        self.ellipse_action = ObjectsAction("Еліпс", self, TOOLS[Tool.ELLIPSE])

        self.objects_menu.add_actions(
            [
                self.point_action,
                self.line_action,
                self.rectangle_action,
                self.ellipse_action,
            ]
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
