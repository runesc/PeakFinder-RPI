import qtawesome as qta
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QColor


class Preloader(QWidget):
	def __init__(self, parent=None, **kwargs):
	  super(Preloader, self).__init__(parent=parent)

	  parent.parent.window_size.connect(self.resize_event)

	  self.parent = parent
		
	  self.loadUI()
	  self.loadCSS()

	def loadUI(self):
		self.root_container = QWidget(self)
		self.root_container.setObjectName('root')


		self.title = QLabel("Epera unos momentos", self.root_container)
		self.title.setAlignment(Qt.AlignCenter)
		self.title.setObjectName("title")

		self.pulse_button = QPushButton("Cargando...", self.root_container)
		self.pulse_button.setObjectName("loader_btn")
		self.pulse_icon = qta.icon('fa5s.spinner', color='white', animation=qta.Pulse(self.pulse_button))
		self.pulse_button.setIcon(self.pulse_icon)

	
	@staticmethod
	def percentage(percent, of):
		"""
			The __init__ method may be documented in either the class level
			docstring, or as a docstring on the __init__ method itself.

			Either form is acceptable, but the two should not be mixed. Choose one
			convention to document the __init__ method and be consistent with it.	

			return:
				porcentaje (:obj:`int`): parent object.
		"""				
		return int((percent * of) / 100.0)



	def loadCSS(self):
		css = ApplicationContext().get_resource('styles/preloader.css') # obtener los estilos css
		with open(css, "r") as styles:
			self.setStyleSheet(styles.read())

	def resize_event(self):
		self.root_container.resize(self.parent.root_container.width(), self.parent.root_container.height())
		self.retranslateUI()


	def retranslateUI(self):
		self.title.resize(self.root_container.width(), self.percentage(10, self.root_container.height()))
		self.title.move(0, self.percentage(35, self.root_container.height()))

		self.pulse_button.resize(self.root_container.width(), self.percentage(10, self.root_container.height()))
		self.pulse_button.move(0, self.percentage(45, self.root_container.height()))