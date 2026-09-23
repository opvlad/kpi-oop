import sys
import subprocess

import pyperclip
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QLabel, QLineEdit


class ParameterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Введення параметрів")
        self.layout = QVBoxLayout()

        self.nPointLabel = QLabel("nPoint:")
        self.nPointInput = QLineEdit()
        self.layout.addWidget(self.nPointLabel)
        self.layout.addWidget(self.nPointInput)

        self.xMinLabel = QLabel("xMin:")
        self.xMinInput = QLineEdit()
        self.layout.addWidget(self.xMinLabel)
        self.layout.addWidget(self.xMinInput)

        self.xMaxLabel = QLabel("xMax:")
        self.xMaxInput = QLineEdit()
        self.layout.addWidget(self.xMaxLabel)
        self.layout.addWidget(self.xMaxInput)

        self.yMinLabel = QLabel("yMin:")
        self.yMinInput = QLineEdit()
        self.layout.addWidget(self.yMinLabel)
        self.layout.addWidget(self.yMinInput)

        self.yMaxLabel = QLabel("yMax:")
        self.yMaxInput = QLineEdit()
        self.layout.addWidget(self.yMaxLabel)
        self.layout.addWidget(self.yMaxInput)

        btn_yes = QPushButton("Yes")
        btn_no = QPushButton("Cancel")
        btn_yes.clicked.connect(self.accept)
        btn_no.clicked.connect(self.reject)
        self.layout.addWidget(btn_yes)
        self.layout.addWidget(btn_no)

        self.setLayout(self.layout)

    def get_parameters(self) -> dict:
        return {
            'nPoint': int(self.nPointInput.text()),
            'xMin': int(self.xMinInput.text()),
            'xMax': int(self.xMaxInput.text()),
            'yMin': int(self.yMinInput.text()),
            'yMax': int(self.yMaxInput.text())
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.process2 = None
        self.process3 = None
        self.setWindowTitle("Lab6")
        self.resize(300, 200)

        self.button = QPushButton("Почати роботу", self)
        self.button.setGeometry(100, 80, 100, 40)
        self.button.clicked.connect(self.start_process)

    def clear_processes(self):
        if self.process2:
            self.process2.terminate()
        if self.process3:
            self.process3.terminate()

    def start_process(self) -> None:
        if self.process2 or self.process3:
            self.clear_processes()

        dialog = ParameterDialog()
        if dialog.exec():
            params = dialog.get_parameters()
            pyperclip.copy(params)

            self.process3 = subprocess.Popen([sys.executable, 'object3.py'])
            self.process2 = subprocess.Popen([sys.executable, "object2.py"])

    def closeEvent(self, event) -> None:
        self.clear_processes()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.move(100, 200)
    app.exec()