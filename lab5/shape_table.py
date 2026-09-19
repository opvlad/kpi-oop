import typing

from PySide6.QtCore import Qt
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtWidgets import QTableView, QWidget, QVBoxLayout


class ShapeTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._headers = ["x1", "y1", "x2", "y2"]
        self._data = [[1, 2, 3, 4], [5, 6, 7, 8]]

    def rowCount(self, parent=None):
        return len(self._data)

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
            return str(self._data[index.row()][index.column()])

        return None


class ShapeTable(QWidget):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shapes Table")
        self.resize(500, 400)

        self.table_model = ShapeTableModel(self)
        self.table_view = QTableView(self)
        self.table_view.setModel(self.table_model)

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)
