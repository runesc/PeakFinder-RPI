import qtawesome as qta
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QColor


class Notification(QWidget):
	def __init__(self, type_, title, description, parent=None, **kwargs):
	  super(Notification, self).__init__(parent=parent)


	  parent.parent.window_size.connect(self.retranslateUI)

	  self.parent = parent
	  self.type = type_
	  self.title = title
	  self.desc = description

	  self.loadUI()
	  self.loadCSS()
	  self.controllerEvent()

	def loadUI(self):
		self.root_container = QWidget(self)
		self.root_container.setObjectName(self.type)

		self.title = QLabel(self.title, self.root_container)
		self.title.setObjectName('title')

		self.close = QPushButton(qta.icon('fa5s.times', color="white"), "", self.root_container)
		self.close.setObjectName("close_btn")
		self.close.setCursor(Qt.PointingHandCursor)

		self.description = QLabel(self.desc, self.root_container)
		self.description.setObjectName('description')
		self.description.setWordWrap(True)


	def loadCSS(self):
		"""
			The __init__ method may be documented in either the class level
			docstring, or as a docstring on the __init__ method itself.

			Either form is acceptable, but the two should not be mixed. Choose one
			convention to document the __init__ method and be consistent with it.		
		"""		
		css = ApplicationContext().get_resource('styles/notification.css') # obtener los estilos css
		with open(css, "r") as styles:
			self.setStyleSheet(styles.read())


	def retranslateUI(self):
		self.root_container.resize(300, 90)
		self.title.resize(300, 25)
		self.close.move(self.title.width() - 30, 0)

		self.description.resize(300, 60)
		self.description.move(0, 25)


	def controllerEvent(self):
		self.close.clicked.connect(self.hideNotification)

	def hideNotification(self):
		self.hide()
