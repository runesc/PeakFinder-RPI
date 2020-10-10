
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QColor, QPixmap, QPainter, QPainterPath

class RoundedImg(QLabel):
	def __init__(self, path, size, parent=None, **kwargs):
		super(RoundedImg, self).__init__(parent=parent)
		self.setMaximumSize(size, size)
		self.setMinimumSize(size, size)
		self.radius = int(size/2)

		self.target = QPixmap(self.size())
		self.target.fill(Qt.transparent)

		pic = QPixmap(path).scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

		painter = QPainter(self.target)
		painter.setRenderHint(QPainter.Antialiasing, True)
		painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
		painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

		path_ = QPainterPath()
		path_.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)

		painter.setClipPath(path_)
		painter.drawPixmap(0, 0, pic)
		self.setPixmap(self.target)