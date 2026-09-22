from PySide6.QtCore import QModelIndex

from shape_tools import DrawnShape
from shape_table import ShapeTableModel


class ShapeRepository:
    def __init__(self):
        self._shapes = []
        self.table_model = ShapeTableModel()
        self.table_model.set_shapes_reference(self._shapes)

    def get_shapes(self) -> list[DrawnShape]:
        return self._shapes

    def get_shape(self, index: int) -> DrawnShape | None:
        if len(self._shapes) < index:
            return None

        return self._shapes[index]

    def add(self, shape: DrawnShape):
        new_row_index = len(self._shapes)
        self.table_model.beginInsertRows(QModelIndex(), new_row_index, new_row_index)
        self._shapes.append(shape)
        self.table_model.endInsertRows()

    def remove_shape(self, shape: DrawnShape):
        if shape not in self._shapes:
            return

        shape_index = self._shapes.index(shape)
        self.table_model.beginRemoveRows(QModelIndex(), shape_index, shape_index)
        self._shapes.remove(shape)
        self.table_model.endRemoveRows()

    def clear(self):
        self.table_model.beginResetModel()
        self._shapes.clear()
        self.table_model.endResetModel()


shape_repo = ShapeRepository()
