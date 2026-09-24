import sys
import socket
from ast import literal_eval

import pyperclip
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCharts import QLineSeries, QChart, QChartView
from PySide6.QtGui import QPainter, QColor, QPalette


class GraphWidget(QWidget):
    def __init__(self, points):
        super().__init__()
        self.points = points
        self.setMinimumSize(600, 400)

        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("white"))
        self.setPalette(palette)

        series = QLineSeries()
        for x, y in self.points:
            series.append(x, y)

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("Графік функції")
        axis_x = chart.axes(Qt.Orientation.Horizontal)[0]
        axis_x.setTitleText("x")

        axis_y = chart.axes(Qt.Orientation.Vertical)[0]
        axis_y.setTitleText("y")

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout = QVBoxLayout()
        layout.addWidget(chart_view)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Object3")
        self.resize(800, 600)

        clipboard_data = pyperclip.paste()
        try:
            points = literal_eval(clipboard_data)
            if not isinstance(points, list):
                QMessageBox.critical(self, "Не вдалося прочитати дані з буферу обміну", "")
        except (ValueError, SyntaxError):
            QMessageBox.critical(self, "Не вдалося прочитати дані з буферу обміну", "")
            points = []

        central_widget = QWidget()
        layout = QVBoxLayout()
        graph_widget = GraphWidget(points)
        layout.addWidget(graph_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("localhost", 8000))
        server.listen()
        conn, addr = server.accept()
        data = conn.recv(1024)
        data_str = data.decode()
        if data_str == "points_created":
            app = QApplication(sys.argv)
            window = MainWindow()
            window.show()
            window.move(600, 200)
            app.exec()
