from collections.abc import Callable

from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QModelIndex, QAbstractTableModel
from PySide6.QtWidgets import QTableView, QWidget, QVBoxLayout, QToolBar


class EventEmitter:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, func):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(func)
        return func

    def emit(self, event: str, *args, **kwargs):
        if event in self._listeners:
            for listener in self._listeners[event]:
                listener(*args, **kwargs)


shape_events = EventEmitter()


class ShapeTableModel(QAbstractTableModel):
    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._is_initialized:
            return

        super().__init__()
        self._shapes = None
        self._headers = ["Shape", "x1", "y1", "x2", "y2"]
        self._is_initialized = True

    def set_shapes_reference(self, shapes):
        self._shapes = shapes

    def rowCount(self, parent=None):
        return len(self._shapes)

    def columnCount(self, parent=None):
        return len(self._headers)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> int | str | None:

        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self._headers):
                    return self._headers[section]
                return section

            if orientation == Qt.Orientation.Vertical:
                return section + 1

        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            shape = self._shapes[index.row()]
            data = shape.get_name_and_coords()
            return data[index.column()]

        return None


class ShapeWindow(QWidget):
    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._is_initialized:
            return

        super().__init__()
        self.setWindowTitle("Shapes Table")
        self.resize(600, 600)

        self.table_model = ShapeTableModel()
        self.table_view = QTableView(self)
        self.table_view.setModel(self.table_model)

        self.table_view.clicked.connect(self._handle_click_cell)
        self.table_view.verticalHeader().sectionClicked.connect(
            self._handle_click_vertical_header
        )

        remove_action = QAction("Видалити фігуру", self)
        remove_action.setShortcut("Delete")
        remove_action.triggered.connect(self._handle_remove_action)
        self.table_view.addAction(remove_action)

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)
        self._is_initialized = True

    @staticmethod
    def _handle_click_cell(cell_index: QModelIndex):
        if not cell_index.isValid():
            return

        shape_events.emit("shape_selected", shape_index=cell_index.row())

    @staticmethod
    def _handle_click_vertical_header(row: int):
        shape_events.emit("shape_selected", shape_index=row)

    @staticmethod
    def _handle_remove_action():
        shape_events.emit("shape_removed")
