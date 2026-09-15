from enum import Enum, auto
from abc import ABC, abstractmethod

from PySide6.QtGui import QColor
from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QPainter, QPainterPath, QBrush, Qt


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

    @staticmethod
    def draw_finished(widget, painter: QPainter) -> None:
        for tool, args in widget.strokes:
            if tool == Tool.RECTANGLE:
                brush = QBrush(QColor("yellow"))
                painter.setBrush(brush)
                painter.drawRect(args)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                continue

            elif tool == Tool.ELLIPSE:
                painter.drawEllipse(*args)
                continue

            painter.drawPath(args)


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
        widget.strokes.append((Tool.FREEHAND, self.path))
        self.path = None
        widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.path:
            painter.drawPath(self.path)


class LineTool(ToolBase):
    def __init__(self):
        self.start = None
        self.end = None

    def press(self, widget, pos: QPoint) -> None:
        self.start = pos

    def move(self, widget, pos: QPoint) -> None:
        self.end = pos
        widget.update()

    def release(self, widget, pos: QPoint) -> None:
        path = QPainterPath()
        path.moveTo(self.start)
        path.lineTo(pos)
        widget.strokes.append((Tool.LINE, path))
        self.start, self.end = None, None
        widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.start and self.end:
            painter.drawLine(self.start, self.end)


class RectTool(ToolBase):
    def __init__(self):
        self.rect = None
        self.start = None
        self.end = None

    def press(self, widget, pos: QPoint) -> None:
        self.start = pos

    def move(self, widget, pos: QPoint) -> None:
        self.end = pos
        widget.update()

    def release(self, widget, pos: QPoint) -> None:
        self.rect = QRect(self.start, self.end)
        widget.strokes.append((Tool.RECTANGLE, self.rect))
        self.rect, self.start, self.end = None, None, None
        widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.start and self.end:
            rect = QRect(self.start, self.end)
            painter.drawRect(rect)


class EllipseTool(ToolBase):
    def __init__(self):
        self.center = None
        self.rx = None
        self.ry = None

    def press(self, widget, pos: QPoint) -> None:
        self.center = pos

    def move(self, widget, pos: QPoint) -> None:
        self.rx = self.center.x() - pos.x()
        self.ry = self.center.y() - pos.y()
        widget.update()

    def release(self, widget, pos: QPoint) -> None:
        widget.strokes.append((Tool.ELLIPSE, (self.center, self.rx, self.ry)))
        self.center, self.rx, self.ry = None, None, None
        widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.center and self.rx and self.ry:
            painter.drawEllipse(self.center, self.rx, self.ry)


TOOLS = {
    Tool.FREEHAND: FreehandTool(),
    Tool.LINE: LineTool(),
    Tool.RECTANGLE: RectTool(),
    Tool.ELLIPSE: EllipseTool(),
}
