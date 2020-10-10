import requests
import json
import qtawesome as qta
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize

from core.modules.firebase import Firebase


class Home(QWidget, Firebase):
	"""
		Esta vista se encarga mostrar las opciones disponibles de la app

		Metodos:
			__init__ (func): Constructor de la clase
			loadUI (func): Cargar los widgets en este metodo.
			loadCSS (func): Cargar los estilos CSS en este metodo.
			resize_event (func): Detecta el tamaño de la ventana principal y se ajusta la vista dependiendo el tamaño.
			percentage (func): Calcula el porcentaje entre X y Y
			retranslateUI (func): Convierte y adapta la interfaz actual a pantallas pequeñas y grandes
			switchWindow (func): Permite cambiar entre ventanas
	"""
	def __init__(self, parent=None, *args):
		"""
			El contructor se encarga de crear las configuraciones por default en las que se 
			ejecutará la clase como instanciar firebase para usar el metodo auth, cargar la interfaz
			y sus estilos CSS ,tambien se intenta conectar a la clase padre en busqueda
			de un evento (resizeEvent) cuando este es activado ejecuta el metodo resize_event.

			Args:
				parent (:obj:`obj`, opcional): parent object.
				args (:obj: 'list', opcional): parametros indefinidos.

		"""
		super(Home, self).__init__()
		parent.window_size.connect(self.resize_event)
		self.parent = parent
		self.auth = self.Auth()
		self.loadUI()
		self.loadCSS()


	def loadUI(self):
		
		self.root_container = QWidget(self)
		self.root_container.setObjectName('root')
		self.root_container.resize(self.parent.largo, self.parent.alto)

		self.label = QLabel("Elige una opción: ", self.root_container)
		self.label.setAlignment(Qt.AlignCenter)
		self.label.setObjectName('title')

		self.central_container = QWidget(self.root_container)
		self.central_container.setObjectName('button_container')

		chart_icon = qta.icon('fa5.chart-bar', color="white")
		stream_icon = qta.icon('fa5s.heartbeat', color="white")

		self.peak_viewer = QPushButton(chart_icon, 'Peak Viewer', self.central_container)
		self.peak_viewer.setIconSize(QSize(64, 64))
		self.peak_viewer.setObjectName('button')
		self.peak_viewer.setCursor(Qt.PointingHandCursor)
		
		self.peak_streamer = QPushButton(stream_icon, 'Peak Streamer', self.central_container)
		self.peak_streamer.setIconSize(QSize(64, 64))
		self.peak_streamer.setObjectName('button')
		self.peak_streamer.setCursor(Qt.PointingHandCursor)

		self.peak_viewer.clicked.connect(lambda x: self.switchWindow(3))
		self.peak_streamer.clicked.connect(lambda x: self.switchWindow(4))


	def loadCSS(self):
		css = ApplicationContext().get_resource('styles/home.css') # obtener los estilos css
		with open(css, "r") as styles:
			self.setStyleSheet(styles.read())


	@pyqtSlot()
	def resize_event(self):
		self.root_container.resize(self.parent.largo, self.parent.alto)
		self.retranslateUI()


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


	def retranslateUI(self):

		self.label.resize(self.root_container.frameSize().width() -8, 50)
		self.label.move(0, 100)

		self.central_container.resize(self.percentage(80, self.root_container.frameSize().width()- 8), 150)
		self.central_container.move(self.percentage(10, self.root_container.frameSize().width()), 200)

		if self.parent.largo <= 576:
			self.central_container.resize(self.percentage(80, self.root_container.frameSize().width()- 8), 290)
			
			self.peak_viewer.resize(self.percentage(80, self.central_container.frameSize().width()- 8), 130)
			self.peak_viewer.move(self.percentage(10, self.central_container.frameSize().width()), 10)

			self.peak_streamer.resize(self.percentage(80, self.central_container.frameSize().width()- 8), 130)
			self.peak_streamer.move(self.percentage(10, self.central_container.frameSize().width()), 150)
		else: 
			self.peak_viewer.resize(self.percentage(30, self.central_container.frameSize().width()- 8), 130)
			self.peak_viewer.move(self.percentage(20, self.central_container.frameSize().width()), 10)

			self.peak_streamer.resize(self.percentage(30, self.central_container.frameSize().width()- 8), 130)
			self.peak_streamer.move(self.percentage(55, self.central_container.frameSize().width()), 10)

	def switchWindow(self, view):
		self.parent.container.setCurrentIndex(view)