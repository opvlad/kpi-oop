from PySide6.QtCore import QModelIndex

from shape_tools import DrawnShape
from shape_table import ShapeTableModel


class ShapeRepository:
    def __init__(self, table_model: ShapeTableModel):
        self._shapes = []
        self.table_model = table_model

    def get_shapes(self):
        print("get")
        return self._shapes

    def add(self, shape: DrawnShape):
        print("add")
        new_row_index = len(self._shapes)
        self.table_model.beginInsertRows(QModelIndex(), new_row_index, new_row_index)
        self._shapes.append(shape)
        self.table_model.endInsertRows()
