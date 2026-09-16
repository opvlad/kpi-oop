from enum import Enum, auto
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Generator, Type
from dataclasses import dataclass

from PySide6.QtGui import QColor
from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QPainter, QPainterPath, QBrush, Qt, QPen


class Tool(Enum):
    FREEHAND = auto()
    LINE = auto()
    RECTANGLE = auto()
    ELLIPSE = auto()


class DrawnShape(ABC):
    @abstractmethod
    def draw(self, painter: QPainter) -> None: ...


@dataclass
class DrawnPath(DrawnShape):
    path: QPainterPath

    def draw(self, painter: QPainter) -> None:
        with ToolBase.black_pen(painter):
            painter.drawPath(self.path)


@dataclass
class DrawnRect(DrawnShape):
    rect: QRect

    def draw(self, painter: QPainter) -> None:
        with ToolBase.black_pen(painter):
            painter.drawRect(self.rect)


@dataclass
class DrawnEllipse(DrawnShape):
    center: QPoint
    rx: float
    ry: float

    def draw(self, painter: QPainter) -> None:
        with ToolBase.black_pen(painter):
            brush = QBrush(QColor("yellow"))
            painter.setBrush(brush)
            painter.drawEllipse(self.center, self.rx, self.ry)
            painter.setBrush(Qt.BrushStyle.NoBrush)


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
        for shape in widget.strokes:
            shape.draw(painter)

    @staticmethod
    @contextmanager
    def black_pen(painter: QPainter) -> Generator[None, None, None]:
        last_pen = painter.pen()
        pen = QPen(QColor("black"), 3)
        painter.setPen(pen)
        yield
        painter.setPen(last_pen)


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
        widget.strokes.append(DrawnPath(self.path))
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
        widget.strokes.append(DrawnPath(path))
        widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.start and self.end:
            painter.drawLine(self.start, self.end)


class RectTool(ToolBase):
    def __init__(self):
        self.center = None
        self.start = None
        self.end = None

    def press(self, widget, pos: QPoint) -> None:
        self.center = pos

    def move(self, widget, pos: QPoint) -> None:
        half_width = abs(self.center.x() - pos.x())
        half_height = abs(self.center.y() - pos.y())
        self.start = QPoint(self.center.x() - half_width, self.center.y() - half_height)
        self.end = QPoint(self.center.x() + half_width, self.center.y() + half_height)
        widget.update()

    def release(self, widget, pos: QPoint) -> None:
        if self.start and self.end:
            rect = QRect(self.start, self.end)
            widget.strokes.append(DrawnRect(rect))
            widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.start and self.end:
            rect = QRect(self.start, self.end)
            painter.drawRect(rect)


class EllipseTool(ToolBase):
    def __init__(self):
        self.start = None
        self.end = None
        self.center = None
        self.rx = None
        self.ry = None

    def press(self, widget, pos: QPoint) -> None:
        self.start = pos

    def move(self, widget, pos: QPoint) -> None:
        self.end = pos
        self.rx = (self.end.x() - self.start.x()) / 2
        self.ry = (self.end.y() - self.start.y()) / 2
        self.center = QPoint(self.start.x() + self.rx, self.start.y() + self.ry)
        widget.update()

    def release(self, widget, pos: QPoint) -> None:
        if self.center and self.rx and self.ry:
            widget.strokes.append(DrawnEllipse(self.center, self.rx, self.ry))
            widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.center and self.rx and self.ry:
            painter.drawEllipse(self.center, self.rx, self.ry)


TOOLS: dict[Tool, Type[ToolBase]] = {
    Tool.FREEHAND: FreehandTool,
    Tool.LINE: LineTool,
    Tool.RECTANGLE: RectTool,
    Tool.ELLIPSE: EllipseTool,
}
