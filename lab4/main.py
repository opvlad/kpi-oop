import sys  # noqa

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenuBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QPen, QColor, QPainter

from shape_tools import Tool, TOOLS, ToolBase


class ObjectsAction(QAction):
    action_group = None

    def __init__(self, text: str, parent, tool: ToolBase, tip: str):
        super().__init__(text, parent)
        self._create_action_group(parent)
        self.setCheckable(True)
        self.setActionGroup(self.action_group)
        self.setToolTip(tip)

        self.tool = tool
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

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.strokes = []
        self.pen = QPen(QColor("red"), 3, Qt.PenStyle.DashLine)

        self.current_tool = TOOLS[Tool.FREEHAND]

        self._create_actions()
        self._create_menubar()
        self._create_toolbars()

    def set_current_tool(self):
        for action in self.objects_menu.menu.actions():
            if action.isChecked() and isinstance(action, ObjectsAction):
                self.current_tool = action.tool

    def _create_actions(self):
        self.point_action = ObjectsAction("Крапка", self, TOOLS[Tool.FREEHAND], "Олівець")
        self.point_action.setChecked(True)
        self.line_action = ObjectsAction("Лінія", self, TOOLS[Tool.LINE], "Намалювати лінію")
        self.rectangle_action = ObjectsAction(
            "Прямокутник", self, TOOLS[Tool.RECTANGLE], "Намалювати прямокутник"
        )
        self.ellipse_action = ObjectsAction("Еліпс", self, TOOLS[Tool.ELLIPSE], "Намалювати еліпс")
        self.line_with_circles_action = ObjectsAction(
            "Лінія з кружечками", self, TOOLS[Tool.LINE_WITH_CIRCLES], "Намалювати лінію з кружечками"
        )
        self.cube_action = ObjectsAction(
            "Куб", self, TOOLS[Tool.CUBE], "Намалювати каркас куба"
        )

    def _create_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")  # noqa
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

    def _create_toolbars(self):
        toolbar = self.addToolBar("Shapes")

        toolbar.addAction(self.point_action)
        toolbar.addAction(self.line_action)
        toolbar.addAction(self.rectangle_action)
        toolbar.addAction(self.ellipse_action)
        toolbar.addAction(self.line_with_circles_action)
        toolbar.addAction(self.cube_action)

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
