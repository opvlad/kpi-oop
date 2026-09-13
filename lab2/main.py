import sys
from enum import Enum, auto
from abc import ABC, abstractmethod

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenuBar
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction, QActionGroup, QPen, QColor, QPainter, QPainterPath


class Tool(Enum):
    FREEHAND = auto()
    LINE = auto()
    RECTANGLE = auto()
    ELLIPSE = auto()


class ToolBase(ABC):
    @abstractmethod
    def press(self, widget, pos: QPoint) -> None: ...

    @abstractmethod
    def move(self, widget, pos: QPoint) -> None: ...

    @abstractmethod
    def release(self, widget, pos: QPoint) -> None: ...

    @abstractmethod
    def draw_preview(self, widget, painter: QPainter) -> None: ...

    @abstractmethod
    def draw_finished(self, widget, painter: QPainter) -> None: ...


class ObjectsAction(QAction):
    action_group = None

    def __init__(self, text: str, parent, tool: ToolBase):
        super().__init__(text, parent)
        self.__create_action_group(parent)
        self.setCheckable(True)
        self.setActionGroup(self.action_group)
        self.tool = tool
        self.triggered.connect(parent.set_current_tool)

    @classmethod
    def __create_action_group(cls, parent):
        if cls.action_group is None:
            cls.action_group = QActionGroup(parent)


class ObjectsMenu:
    def __init__(self, menubar: QMenuBar):
        self.menu = menubar.addMenu("Об’єкти")

    def add_actions(self, actions: list[QAction]):
        for action in actions:
            self.menu.addAction(action)


class FreehandTool(ToolBase):
    def __init__(self):
        self.path = None

    def press(self, widget, pos: QPoint) -> None:
        self.path = QPainterPath()
        self.path.moveTo(pos)

    def move(self, widget, pos: QPoint) -> None:
        self.path.lineTo(pos)
        widget.update()

    def release(self, widget, pos: QPoint) -> None:
        widget.strokes.append(self.path)
        self.path = None
        widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.path:
            painter.drawPath(self.path)

    def draw_finished(self, widget, painter: QPainter) -> None:
        for path in window.strokes:
            painter.drawPath(path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 1")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.strokes = []
        self.current_path = None
        self.pen = QPen(QColor("black"), 3)

        self.__tools = {
            Tool.FREEHAND: FreehandTool(),
            Tool.LINE: ...,
            Tool.RECTANGLE: ...,
            Tool.ELLIPSE: ...,
        }
        self.current_tool = self.__tools[Tool.FREEHAND]

        self.__create_menubar()

    def set_current_tool(self):
        for action in self.objects_menu.menu.actions():
            if action.isChecked() and isinstance(action, ObjectsAction):
                self.current_tool = action.tool

    def __create_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")
        self.objects_menu = ObjectsMenu(menubar)
        help_menu = menubar.addMenu("Довідка")

        self.point_action = ObjectsAction("Крапка", self, self.__tools[Tool.FREEHAND])
        self.point_action.setChecked(True)
        self.line_action = ObjectsAction("Лінія", self, self.__tools[Tool.LINE])
        self.rectangle_action = ObjectsAction(
            "Прямокутник", self, self.__tools[Tool.RECTANGLE]
        )
        self.ellipse_action = ObjectsAction("Еліпс", self, self.__tools[Tool.ELLIPSE])

        self.objects_menu.add_actions(
            [
                self.point_action,
                self.line_action,
                self.rectangle_action,
                self.ellipse_action,
            ]
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.current_tool.press(self, event.position().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.current_tool.move(self, event.position().toPoint())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.current_tool.release(self, event.position().toPoint())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen)

        self.current_tool.draw_preview(self, painter)
        self.current_tool.draw_finished(self, painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
