from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtWidgets import QTableView, QWidget, QVBoxLayout


class ShapeTableModel(QAbstractTableModel):
    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
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

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shapes Table")
        self.resize(600, 600)

        self.table_model = ShapeTableModel()
        self.table_view = QTableView(self)
        self.table_view.setModel(self.table_model)

        # self.table_view.clicked.connect(self._handle_click_table)

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)

    # def _handle_click_table(self, index: QModelIndex):
    #     if not index.isValid():
    #         return
    #
    #     print(shpa)
