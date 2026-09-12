from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QScrollBar, QVBoxLayout, QHBoxLayout, QPushButton, QLabel


class ScrollingDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Choose value")
        self.resize(250, 150)

        layout = QVBoxLayout(self)
        self.value_label = QLabel("0", self)
        scrollbar = QScrollBar(Qt.Orientation.Horizontal)
        scrollbar.setRange(0, 100)
        scrollbar.valueChanged.connect(self.__update_value)
        layout.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(scrollbar)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_yes = QPushButton("Yes")
        btn_no = QPushButton("Cancel")
        btn_layout.addWidget(btn_yes)
        btn_layout.addWidget(btn_no)
        layout.addLayout(btn_layout)

        btn_yes.clicked.connect(self.accept)
        btn_no.clicked.connect(self.reject)

    def __update_value(self, value: int) -> None:
        self.value_label.setText(str(value))

    def get_value(self) -> str:
        return self.value_label.text()


def ask_value(parent_window) -> None:
    dialog = ScrollingDialog(parent_window)

    if dialog.exec():
        parent_window.data_label.setText(dialog.get_value())
