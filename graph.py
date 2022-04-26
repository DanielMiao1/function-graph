from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from PyQt5.QtWidgets import *

import time
import random


class Tab(QLabel):
	clicked = pyqtSignal()

	def __init__(self, parent, text=""):
		super().__init__(parent=parent)
		if text:
			self.setText(text)
		self.resize(QSize(8 * len(text), 20))
		self.setCursor(Qt.PointingHandCursor)
		self.setAlignment(Qt.AlignCenter)
		self.selected = False

	def enterEvent(self, event):
		if self.selected:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")
		else:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
		super().enterEvent(event)

	def leaveEvent(self, event):
		if self.selected:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.2);")
		else:
			self.setStyleSheet("background-color: transparent;")
		super().leaveEvent(event)

	def mousePressEvent(self, event):
		self.setStyleSheet("background-color: rgba(0, 0, 0, 0.2);")
		self.clicked.emit()
		self.selected = True
		for i in self.parent().tab_widgets:
			if i == self:
				continue
			i.selected = False
			i.setStyleSheet("background-color: transparent;")
		super().mousePressEvent(event)

	def mouseReleaseEvent(self, event):
		if not self.selected:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
		super().mouseReleaseEvent(event)


class Tabs(QWidget):
	def __init__(self, parent, tabs):
		super().__init__(parent=parent)
		self.tab_widgets = []
		self.tabs = tabs
		for x, y in enumerate(tabs.keys()):
			self.tab_widgets.append(Tab(self, y))
			self.tab_widgets[-1].clicked.connect(tabs[y])
			self.tab_widgets[-1].move(QPoint(sum(i.width() for i in self.tab_widgets[:-1]), 0))
			self.tab_widgets[-1].show()
		self.tab_widgets[0].selected = True
		self.tab_widgets[0].setStyleSheet("background-color: rgba(0, 0, 0, 0.2)")


class Point(QPushButton):
	def __init__(self, parent, window, sample_number, value, array, color="black"):
		super().__init__(parent=parent)
		self.parent_ = window
		self.setStyleSheet("background-color: " + color)
		self.color = color
		self.array = array
		self.resize(QSize(window.width() // (window.samples), window.width() // window.samples))
		self.sample_number, self.value = sample_number, value

	def enterEvent(self, event):
		self.setStyleSheet(f"background-color: rgba({', '.join(map(str, QColor(self.color).getRgb()[:-1]))}, 0.5)")
		self.parent_.label.setText("Point %i\n%0.*fs\nArray [%s]" % (self.sample_number, self.parent_.float_precision, self.value, (", ".join(map(str, self.array))) if len(self.array) <= 16 else (", ".join(map(str, self.array[:15])) + "..." + str(self.array[-1]))))
		self.parent_.label.show()
		super().enterEvent(event)

	def leaveEvent(self, event):
		self.setStyleSheet("background-color: " + self.color)
		super().enterEvent(event)


class Column(QPushButton):
	def __init__(self, parent, window, sample_number, value, array):
		super().__init__(parent=parent)
		self.setStyleSheet("background: transparent;")
		self.parent_ = window
		self.array = array
		self.sample_number = sample_number
		self.value = value
		self.resize(QSize(parent.width() // (window.samples), parent.height()))

	def enterEvent(self, event):
		if not self.parent_.static:
			self.parent_.points[self.sample_number - 1].setStyleSheet("background: #FF0000;")
			self.setStyleSheet("background: rgba(0, 0, 0, 0.2);")
			self.parent_.label.setText("Point %i\n%0.*fs\nArray [%s]" % (self.sample_number, self.parent_.float_precision, self.value, (", ".join(map(str, self.array))) if len(self.array) <= 16 else (", ".join(map(str, self.array[:15])) + "..." + str(self.array[-1]))))
			self.parent_.label.show()
		super().enterEvent(event)

	def leaveEvent(self, event):
		if not self.parent_.static:
			self.parent_.points[self.sample_number - 1].setStyleSheet("background: " + self.parent_.points[self.sample_number - 1].color)
			self.setStyleSheet("background: transparent;")
		super().enterEvent(event)


class StaticButton(QPushButton):
	def __init__(self, parent):
		super().__init__(parent=parent)
		self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1)")
		self.setText("Static")
		self.setCursor(Qt.PointingHandCursor)
		self.resize(100, 50)
		self.active = False

	def enterEvent(self, event):
		if self.active:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.4)")
		else:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.2)")
		super().enterEvent(event)

	def leaveEvent(self, event):
		if self.active:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.3)")
		else:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1)")
		super().leaveEvent(event)

	def mousePressEvent(self, event):
		if self.active:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.2)")
		else:
			self.setStyleSheet("background-color: rgba(0, 0, 0, 0.3)")
		self.active = not self.active
		super().mousePressEvent(event)


class StatisticsButton(QPushButton):
	def __init__(self, parent):
		super().__init__(parent=parent)
		self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1)")
		self.setText("Statistics")
		self.setCursor(Qt.PointingHandCursor)
		self.resize(120, 50)

	def enterEvent(self, event):
		self.setStyleSheet("background-color: rgba(0, 0, 0, 0.2)")
		super().enterEvent(event)

	def leaveEvent(self, event):
		self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1)")
		super().leaveEvent(event)

	def mousePressEvent(self, event):
		self.setStyleSheet("background-color: rgba(0, 0, 0, 0.3)")
		super().mousePressEvent(event)


class TimeFunction(QObject):
	finished = pyqtSignal()
	timed = pyqtSignal(list)

	def __init__(self, function, samples, start, sample_start):
		super().__init__()
		self.function = function
		self.samples = samples
		self.start_ = start
		self.sample_start = sample_start

	def runFunction(self):
		for x, y in zip(range(self.samples), range(self.samples)):
			array = range(self.start_, y + self.start_ + 1)
			start = time.time()
			self.function(array)
			end = time.time()
			self.timed.emit([x, array, end - start])
		self.finished.emit()


class TimeMonitorPage(QWidget):
	def __init__(self, parent, function, samples, start, sample_start, float_precision):
		super().__init__(parent=parent)
		self.points, self.columns = [], []
		self.static = False
		self.label = QLabel("Point info", self)
		self.label.move(QPoint(5, 5))
		self.label.resize(QSize(self.width(), 50))
		self.label.setAlignment(Qt.AlignTop)
		self.static_button = StaticButton(self)
		self.static_button.move(QPoint(self.width() - 100, 0))
		self.static_button.setToolTip("Shift")
		self.static_button.clicked.connect(self.toggleStatic)
		self.statistics_button = StatisticsButton(self)
		self.statistics_button.move(QPoint(self.width() - 220, 0))
		self.statistics_button.clicked.connect(self.statistics)
		self.scroll_area = QScrollArea(self)
		self.scroll_area.setStyleSheet("""
QScrollBar:horizontal {
	background: rgba(0, 0, 0, 0.1);
	height: 10px;
	margin: 0px 20px 0 20px;
}
QScrollBar::handle:horizontal {
	background: rgba(0, 0, 0, 0.2);
	min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
	background: rgba(0, 0, 0, 0.3);
	min-width: 20px;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
	background: rgba(0, 0, 0, 0.4);
	width: 20px;
	subcontrol-origin: margin;
}

QScrollBar::add-line:horizontal:hover,
QScrollBar::sub-line:horizontal:hover {
	background: rgba(0, 0, 0, 0.5);
}


QScrollBar::add-line:horizontal {
	subcontrol-position: right;
}

QScrollBar::sub-line:horizontal {
	subcontrol-position: left;
}
""")
		self.scroll_widget = QWidget(self)
		self.scroll_area.setStyleSheet("border: none;")
		self.scroll_area_layout = QHBoxLayout()
		self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.scroll_area.setWidgetResizable(False)
		self.scroll_area.setWidget(self.scroll_widget)
		self.function = function
		self.samples = samples
		self.start_ = start
		self.sample_start = sample_start
		self.float_precision = float_precision
		self.label.raise_()
		self.static_button.raise_()
		self.thread, self.time_function = QThread(), TimeFunction(function, samples, start, sample_start)
		self.time_function.moveToThread(self.thread)
		self.thread.started.connect(self.time_function.runFunction)
		self.time_function.timed.connect(self.addPoint)
		self.time_function.finished.connect(self.thread.quit)
		self.thread.finished.connect(self.thread.deleteLater)
		self.time_function.finished.connect(self.time_function.deleteLater)
		self.thread.finished.connect(self.movePoints)
		self.thread.start()

	def statistics(self):
		pass

	def toggleStatic(self):
		for i in self.columns:
			self.points[i.sample_number - 1].setStyleSheet("background: " + self.points[i.sample_number - 1].color)
			i.setStyleSheet("background: transparent;")
		self.static = not self.static

	def movePoints(self):
		max_value = max(map((lambda point: point.value), self.points))
		multiply_rate = 1
		while multiply_rate * max_value < self.height():
			multiply_rate *= 10
		multiply_rate = multiply_rate + (multiply_rate / 10) - multiply_rate
		for i in range(len(self.points)):
			self.points[i].move(QPoint(self.points[i].sample_number * (self.width() // (self.samples)), self.height() - (self.points[i].value * (100000 / (max_value * self.height()))) - 12))
			self.columns[i].move(QPoint(self.columns[i].sample_number * (self.width() // (self.samples)), 0))

	def addPoint(self, items):
		self.points.append(Point(self.scroll_widget, self, items[0] + 1, items[2], items[1]))
		self.scroll_area_layout.addWidget(self.points[-1])
		self.columns.append(Column(self.scroll_widget, self, items[0] + 1, items[2], items[1]))
		self.scroll_area_layout.addWidget(self.columns[-1])
		self.points[-1].show()
		self.columns[-1].show()

	def resizeEvent(self, event):
		self.scroll_area.resize(self.size())
		self.label.resize(QSize(self.width(), 50))
		self.static_button.move(QPoint(self.width() - 100, 0))
		self.scroll_widget.resize(QSize(self.width() + 100, self.height() - 10))
		if self.points:
			self.movePoints()
		super().resizeEvent(event)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Shift:
			self.static = True
			self.static_button.active = True
			self.static_button.setStyleSheet("background-color: rgba(0, 0, 0, 0.3)")
		super().keyPressEvent(event)

	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Shift:
			self.static = False
			for i in self.columns:
				self.points[i.sample_number - 1].setStyleSheet("background: " + self.points[i.sample_number - 1].color)
				i.setStyleSheet("background: transparent;")
			self.static_button.active = False
			self.static_button.setStyleSheet("background-color: rgba(0, 0, 0, 0.2)")
		super().keyReleaseEvent(event)

class MemoryMonitorPage(QWidget):
	def __init__(self, parent):
		super().__init__(parent=parent)


class StatisticsPage(QWidget):
	def __init__(self, parent):
		super().__init__(parent=parent)


class GraphWindow(QMainWindow):
	def __init__(self, function, samples, start, sample_start, float_precision, window_title):
		super().__init__()
		self.setWindowTitle(window_title)
		self.setMinimumSize(QSize(1000, 500))
		self.stacked_widget = QStackedWidget(self)
		self.stacked_widget.move(0, 20)
		self.stacked_widget.resize(QSize(self.width(), self.height() - 20))
		self.stacked_widget.addWidget(TimeMonitorPage(self, function, samples, start, sample_start, float_precision))
		self.stacked_widget.addWidget(MemoryMonitorPage(self))
		self.stacked_widget.addWidget(StatisticsPage(self))
		self.tabs = Tabs(self, {"Execution Time": lambda: self.stacked_widget.setCurrentIndex(0), "Maximum Memory Usage": lambda: self.stacked_widget.setCurrentIndex(1), "Statistics": lambda: self.stacked_widget.setCurrentIndex(2)})
		self.tabs.resize(QSize(self.width(), 20))
		self.show()



def graph(function, samples=200, array_start=0, sample_start=2, float_precision=20, window_title="Function Runtime Graph"):
	application, window = QApplication([]), GraphWindow(function, samples, array_start, sample_start, float_precision, window_title)
	application.exec_()
