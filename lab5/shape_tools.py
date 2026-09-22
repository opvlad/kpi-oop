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
    LINE_WITH_CIRCLES = auto()
    CUBE = auto()


class DrawnShape(ABC):
    @abstractmethod
    def draw(self, painter: QPainter, is_selected: bool = False) -> None: ...

    @abstractmethod
    def get_coords(
        self,
    ) -> tuple[int, int, int, int]: ...

    @abstractmethod
    def to_dict(self) -> dict: ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "DrawnShape": ...

    def get_name_and_coords(self) -> tuple[str, int, int, int, int]:
        coords = self.get_coords()
        return SHAPE_NAMES[self.__class__], *coords


@dataclass
class DrawnPath(DrawnShape):
    path: QPainterPath

    def draw(self, painter: QPainter, is_selected: bool = False) -> None:
        with ToolBase.shape_pen(painter, is_selected):
            painter.drawPath(self.path)

    def get_coords(self) -> tuple[int, int, int, int]:
        start = self.path.pointAtPercent(0.0)
        end = self.path.pointAtPercent(1.0)
        return int(start.x()), int(start.y()), int(end.x()), int(end.y())

    def to_dict(self) -> dict:
        points = []
        for i in range(self.path.elementCount()):
            element = self.path.elementAt(i)
            points.append((element.x, element.y))

        return {
            "__type__" : "DrawnPath",
            "points": points,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DrawnPath":
        path = QPainterPath()
        points = [QPoint(x, y) for x, y in data["points"]]

        start = points[0]
        path.moveTo(start)
        for point in points[1:]:
            path.lineTo(point)

        return cls(path)


@dataclass
class DrawnLine(DrawnShape):
    path: QPainterPath

    def draw(self, painter: QPainter, is_selected: bool = False) -> None:
        with ToolBase.shape_pen(painter, is_selected):
            painter.drawPath(self.path)

    def get_coords(self) -> tuple[int, int, int, int]:
        start = self.path.pointAtPercent(0.0)
        end = self.path.pointAtPercent(1.0)
        return int(start.x()), int(start.y()), int(end.x()), int(end.y())


@dataclass
class DrawnRect(DrawnShape):
    rect: QRect

    def draw(self, painter: QPainter, is_selected: bool = False) -> None:
        with ToolBase.shape_pen(painter, is_selected):
            painter.drawRect(self.rect)

    def get_coords(self) -> tuple[int, int, int, int]:
        start = self.rect.topLeft()
        end = self.rect.bottomRight()
        return start.x(), start.y(), end.x(), end.y()


@dataclass
class DrawnEllipse(DrawnShape):
    center: QPoint
    rx: float
    ry: float
    start: QPoint
    end: QPoint

    def draw(self, painter: QPainter, is_selected: bool = False) -> None:
        with ToolBase.shape_pen(painter, is_selected):
            brush = QBrush(QColor("yellow"))
            painter.setBrush(brush)
            painter.drawEllipse(self.center, self.rx, self.ry)
            painter.setBrush(Qt.BrushStyle.NoBrush)

    def get_coords(self) -> tuple[int, int, int, int]:
        return self.start.x(), self.start.y(), self.end.x(), self.end.y()


@dataclass
class DrawnLineWithCircles(DrawnShape):
    start: QPoint
    end: QPoint
    radius: float

    def draw(self, painter: QPainter, is_selected: bool = False) -> None:
        with ToolBase.shape_pen(painter, is_selected):
            painter.drawLine(self.start, self.end)
            painter.drawEllipse(self.start, self.radius, self.radius)
            painter.drawEllipse(self.end, self.radius, self.radius)

    def get_coords(self) -> tuple[int, int, int, int]:
        return self.start.x(), self.start.y(), self.end.x(), self.end.y()


@dataclass
class DrawnCube(DrawnShape):
    front_start: QPoint
    front_end: QPoint

    def draw(self, painter: QPainter, is_selected: bool = False) -> None:
        offset_x = (self.front_end.x() - self.front_start.x()) // 3
        offset_y = (self.front_end.y() - self.front_start.y()) // 3
        offset = QPoint(offset_x, -offset_y)

        back_start = self.front_start + offset
        back_end = self.front_end + offset

        with ToolBase.shape_pen(painter, is_selected):
            painter.drawRect(QRect(self.front_start, self.front_end))
            painter.drawRect(QRect(back_start, back_end))

            painter.drawLine(self.front_start, back_start)
            painter.drawLine(
                QPoint(self.front_end.x(), self.front_start.y()),
                QPoint(back_end.x(), back_start.y()),
            )
            painter.drawLine(
                QPoint(self.front_start.x(), self.front_end.y()),
                QPoint(back_start.x(), back_end.y()),
            )
            painter.drawLine(self.front_end, back_end)

    def get_coords(self) -> tuple[int, int, int, int]:
        return (
            self.front_start.x(),
            self.front_start.y(),
            self.front_end.x(),
            self.front_end.y(),
        )


class ToolBase(ABC):
    @abstractmethod
    def press(self, widget, pos: QPoint) -> None: ...

    @abstractmethod
    def move(self, widget, pos: QPoint) -> None: ...

    @abstractmethod
    def release(self, widget, shape_repo, pos: QPoint) -> None: ...

    @abstractmethod
    def draw_preview(self, widget, painter: QPainter) -> None: ...

    @staticmethod
    def draw_finished(
        shape_repo, painter: QPainter, selected: DrawnShape | None = None
    ) -> None:
        for shape in shape_repo.get_shapes():
            is_selected = shape is selected
            shape.draw(painter, is_selected)

    @staticmethod
    @contextmanager
    def shape_pen(painter: QPainter, is_selected: bool) -> Generator[None, None, None]:
        last_pen = painter.pen()
        color = QColor("red") if is_selected else QColor("black")
        pen = QPen(color, 3)
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

    def release(self, widget, shape_repo, pos: QPoint) -> None:
        shape_repo.add(DrawnPath(self.path))
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

    def release(self, widget, shape_repo, pos: QPoint) -> None:
        path = QPainterPath()
        path.moveTo(self.start)
        path.lineTo(pos)
        shape_repo.add(DrawnLine(path))
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

    def release(self, widget, shape_repo, pos: QPoint) -> None:
        if self.start and self.end:
            rect = QRect(self.start, self.end)
            shape_repo.add(DrawnRect(rect))
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
        self.rx = (self.end.x() - self.start.x()) // 2
        self.ry = (self.end.y() - self.start.y()) // 2
        self.center = QPoint(self.start.x() + self.rx, self.start.y() + self.ry)
        widget.update()

    def release(self, widget, shape_repo, pos: QPoint) -> None:
        if self.center and self.rx and self.ry:
            shape_repo.add(
                DrawnEllipse(self.center, self.rx, self.ry, self.start, self.end)
            )
            widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.center and self.rx and self.ry:
            painter.drawEllipse(self.center, self.rx, self.ry)


class LineWithCirclesTool(LineTool, EllipseTool):
    def __init__(self):
        LineTool.__init__(self)
        EllipseTool.__init__(self)
        self.radius = 10

    def release(self, widget, shape_repo, pos: QPoint) -> None:
        if self.start and self.end:
            shape_repo.add(DrawnLineWithCircles(self.start, self.end, self.radius))
            widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        LineTool.draw_preview(self, widget, painter)

        self.rx, self.ry = self.radius, self.radius
        self.center = self.start
        EllipseTool.draw_preview(self, widget, painter)

        self.center = self.end
        EllipseTool.draw_preview(self, widget, painter)


class CubeTool(RectTool, LineTool):
    def __init__(self):
        RectTool.__init__(self)
        LineTool.__init__(self)

    def release(self, widget, shape_repo, pos: QPoint) -> None:
        if self.start and self.end:
            shape_repo.add(DrawnCube(self.start, self.end))
            widget.update()

    def draw_preview(self, widget, painter: QPainter) -> None:
        if self.start and self.end:
            front_start = self.start
            front_end = self.end

            offset_x = (front_end.x() - front_start.x()) // 3
            offset_y = (front_end.y() - front_start.y()) // 3
            offset = QPoint(offset_x, -offset_y)

            RectTool.draw_preview(self, widget, painter)

            self.start = front_start + offset
            self.end = front_end + offset
            RectTool.draw_preview(self, widget, painter)

            corners_front = (
                front_start,
                QPoint(front_end.x(), front_start.y()),
                QPoint(front_start.x(), front_end.y()),
                front_end,
            )

            corners_back = (
                self.start,
                QPoint(self.end.x(), self.start.y()),
                QPoint(self.start.x(), self.end.y()),
                self.end,
            )

            for front, back in zip(corners_front, corners_back):
                self.start = front
                self.end = back
                LineTool.draw_preview(self, widget, painter)

            self.start = front_start
            self.end = front_end


TOOLS: dict[Tool, Type[ToolBase]] = {
    Tool.FREEHAND: FreehandTool,
    Tool.LINE: LineTool,
    Tool.RECTANGLE: RectTool,
    Tool.ELLIPSE: EllipseTool,
    Tool.LINE_WITH_CIRCLES: LineWithCirclesTool,
    Tool.CUBE: CubeTool,
}


SHAPE_CLASSES: dict[str, Type[DrawnShape]] = {
    "DrawnPath": DrawnPath,
    "DrawnLine": DrawnLine,
    "DrawnRect": DrawnRect,
    "DrawnEllipse": DrawnEllipse,
    "DrawnLineWithCircles": DrawnLineWithCircles,
    "DrawnCube": DrawnCube,
}


SHAPE_NAMES: dict[Type[DrawnShape], str] = {
    DrawnPath: "Крива",
    DrawnLine: "Лінія",
    DrawnRect: "Прямокутник",
    DrawnEllipse: "Еліпс",
    DrawnLineWithCircles: "Лінія з кружечками",
    DrawnCube: "Куб",
}
