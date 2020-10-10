import requests
import json
import pyAesCrypt
import qtawesome as qta
import core.modules.pyqtgraph as pg
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QGraphicsDropShadowEffect, QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QColor


from core.modules.firebase import Firebase
from core.modules.pyqtgraph import PlotWidget, plot

class PeakStreamer(QWidget, Firebase):
	"""
		Esta vista se encarga mostrar las opciones disponibles de la app

		Metodos:
			__init__ (func): Constructor de la clase
			loadUI (func): Cargar los widgets en este metodo.
			loadCSS (func): Cargar los estilos CSS en este metodo.
			resize_event (func): Detecta el tamaño de la ventana principal y se ajusta la vista dependiendo el tamaño.
			percentage (func): Calcula el porcentaje entre X y Y
			retranslateUI (func): Convierte y adapta la interfaz actual a pantallas pequeñas y grandes
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
		super(PeakStreamer, self).__init__()
		parent.window_size.connect(self.resize_event)
		self.parent = parent
		self.auth = self.Auth()

		self.number = "0"
		self.time = "0s"
		self.desv = "0s"
		
		self.loadUI()
		self.loadCSS()
		self.eventController()


	def loadUI(self):
		
		self.root_container = QWidget(self)
		self.root_container.setObjectName('root')
		self.root_container.resize(self.parent.largo, self.parent.alto)

		self.view_title = QLabel("Peak<span style='font-weight:300'>Streamer</span>", self.root_container)
		self.view_title.setObjectName('view_title')
		
		"""
			| 
			|		Barra lateral			
			|
		"""

		self.left_bar = QWidget(self.root_container)
		self.left_bar.setObjectName('left_bar')


		self.top_layout = QVBoxLayout()
		self.top_menu = QWidget(self.left_bar)
		self.top_menu.setLayout(self.top_layout)
		self.top_menu.setObjectName('top_menu')


		buttons_icons = [qta.icon('fa5s.home', color="white"), qta.icon('fa5s.chart-bar', color="white"),
			qta.icon('fa5s.heartbeat', color="white"), qta.icon('fa5s.arrow-down', color="white")]

		buttons_ids = ["btn_home", "btn_viewer", "btn_streamer", "btn_cloud"]

		for x in range(len(buttons_ids)):
			btn = QPushButton(buttons_icons[x], "", self.top_menu)
			btn.setObjectName(buttons_ids[x])
			btn.setIconSize(QSize(28, 28))
			btn.setCursor(Qt.PointingHandCursor)
			self.top_layout.addWidget(btn)
		

		self.bottom_layout = QVBoxLayout()
		self.bottom_menu = QWidget(self.left_bar)
		self.bottom_menu.setLayout(self.bottom_layout)
		self.bottom_menu.setObjectName('bottom_menu')

		buttons_icons = [qta.icon('fa5s.user', color="white"), qta.icon('fa5s.sign-out-alt', color="white")]
		buttons_ids = ["btn_profile", "btn_quit"]

		for x in range(len(buttons_ids)):
			btn = QPushButton(buttons_icons[x], "", self.top_menu)
			btn.setObjectName(buttons_ids[x])
			btn.setIconSize(QSize(28, 28))
			btn.setCursor(Qt.PointingHandCursor)
			self.bottom_layout.addWidget(btn)

		"""
			| 
			|		Fin Barra lateral			
			|
		"""	

		"""
			| 
			|		PeakStreamer container
			|
		"""			

		# Efecto sombra
		shadow = QGraphicsDropShadowEffect(color=QColor(0, 0, 0, 255 * 0.1), blurRadius=5, xOffset=5, yOffset=5)
		#shadow2 = QGraphicsDropShadowEffect(color=QColor(0, 0, 0, 255 * 0.1), blurRadius=5, xOffset=5, yOffset=5)

		self.chart_container = QWidget(self.root_container)
		self.chart_container.setObjectName('chart_container')
		self.chart_container.setGraphicsEffect(shadow)

		self.chart_widget = pg.PlotWidget(self.chart_container)
		self.chart_widget.setBackground("#414345")
		self.chart_widget.showGrid(y=True)
		self.chart_widget.getAxis("bottom").setPen(pg.mkPen(color="#414345", width=0))

		self.button_container = QHBoxLayout()
		self.button_container.setSpacing(0)
		self.button_container.setContentsMargins(0,0,0,0)
		self.control_center = QWidget(self.chart_container)
		self.control_center.setLayout(self.button_container)
		self.control_center.setObjectName('control_center')

		self.obj_id = ['play_pause_stream', "stop_stream", "rec_stream", "reset_stream", "clean_stream"]
		obj_icon = [qta.icon('fa5s.play', color="white"), qta.icon('fa5s.stop', color="white"),
					qta.icon('fa5s.circle', color="tomato"), qta.icon('fa5s.redo-alt', color="white"),
					qta.icon('fa5s.save', color="white")]

		for x in range(5):
			btn = QPushButton(obj_icon[x],"",self.control_center)
			btn.setObjectName(self.obj_id[x])
			btn.setIconSize(QSize(16, 16))
			btn.setCursor(Qt.PointingHandCursor)
			self.button_container.addWidget(btn, stretch=1)	
			self.button_container.setSpacing(0)

		self.button_container.setContentsMargins(160, 0, 160, 0)


		"""
			| 
			|		Fin de PeakStreamer container
			|
		"""
		
		"""
			| 
			|		Data Area
			|
		"""	

		self.data_area = QWidget(self.root_container)


		self.statistics = QWidget(self.data_area)

		grid_layout = QGridLayout()
		self.statistics_data = QWidget(self.statistics)
		self.statistics_data.setLayout(grid_layout)


		object_list = ["title", "peaks_val", "peaks_label", "prom_duration_val", 
						"prom_duration_label", "desv_val", "desv_label"]

		label_content = ["Contracciones en Tiempo Real", self.number, "Numero", self.time, "Tiempo medio", 
						self.desv, "Desviación Estandar"]

		index = 0

		# Calcular la posicion que tendrán en el layout
		for x in range(4):
			for y in range(2):
				if [x,y] != [0,1]:
					# Crear label, establecer texto y nombre de objeto
					label = QLabel(label_content[index])
					label.setObjectName(object_list[index])
					index += 1
					grid_layout.addWidget(label, x, y) # Insertarlo en el layout


		self.statistics_data.findChild(QLabel, 'title').setAlignment(Qt.AlignBottom) # Corregir alineacion del titulo		
		self.statistics_data.findChild(QLabel, 'title').setWordWrap(True)

		self.comments = QTextEdit(self.data_area)
		self.comments.setPlaceholderText("Comentarios de la medicion")
		self.comments.setObjectName('comment_box')




	def switchWindow(self, view):
		self.parent.container.setCurrentIndex(view)


	def loadCSS(self):
		css = ApplicationContext().get_resource('styles/peakstreamer.css') # obtener los estilos css
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
		self.view_title.resize(self.percentage(20, self.root_container.width()), self.percentage(10, self.root_container.height()))
		self.view_title.move(self.percentage(5.5, self.root_container.width()), 0)

		self.left_bar.resize(self.percentage(4, self.root_container.width()), self.parent.alto)

		self.top_menu.resize(self.left_bar.width(), self.percentage(40, self.left_bar.height()))
		self.top_menu.move(0, self.percentage(8, self.left_bar.height()))

		self.bottom_menu.resize(self.left_bar.width(), self.percentage(20, self.left_bar.height()))
		self.bottom_menu.move(0,  self.percentage(75, self.left_bar.height()))


		self.chart_container.resize(self.percentage(92, self.root_container.width()), self.percentage(45, self.root_container.height()))
		self.chart_container.move(self.percentage(6, self.root_container.width()) - 8, self.percentage(10, self.root_container.height()))

		self.chart_widget.resize(self.percentage(95, self.chart_container.width()),self.percentage(70, self.chart_container.height()))
		self.chart_widget.move(self.percentage(2.5, self.chart_container.width()), self.percentage(10, self.chart_container.height()))

		self.control_center.resize(self.percentage(50, self.chart_container.width()),self.percentage(15, self.chart_container.height()))
		self.control_center.move(self.percentage(25, self.chart_container.width()), self.percentage(85, self.chart_container.height()))

		# Control Center buttons
		for x in range(5):
			self.control_center.findChild(QPushButton, self.obj_id[x]).setFixedSize(self.percentage(15, self.chart_container.height()), self.percentage(15, self.chart_container.height()))
		
		if self.root_container.width() < 1000:
			self.button_container.setContentsMargins(0, 0, 0, 0)
		else:
			self.button_container.setContentsMargins(160, 0, 160, 0)


		self.data_area.resize(self.percentage(92, self.root_container.width()), self.percentage(45, self.root_container.height()))
		self.data_area.move(self.percentage(6, self.root_container.width()) - 8, self.percentage(55, self.root_container.height()))

		self.statistics.resize(self.percentage(30, self.data_area.width()),self.percentage(100, self.data_area.height()))
		self.statistics.move(self.percentage(1, self.data_area.width()),self.percentage(3.5, self.data_area.height()))

		self.statistics_data.resize(self.percentage(95, self.statistics.width()), self.percentage(80, self.statistics.height()))
		self.statistics_data.move(self.percentage(2.5, self.statistics.width()), self.percentage(0, self.statistics.height()))
	
		self.comments.resize(self.percentage(68, self.data_area.width()),self.percentage(70, self.data_area.height()))
		self.comments.move(self.percentage(33, self.data_area.width()), self.percentage(10, self.data_area.height()))


	def eventController(self):
		self.top_menu.findChild(QPushButton, "btn_home").clicked.connect(lambda x : self.switchWindow(2))
		self.top_menu.findChild(QPushButton, "btn_viewer").clicked.connect(lambda x : self.switchWindow(3))
		self.top_menu.findChild(QPushButton, "btn_streamer").clicked.connect(lambda x : self.switchWindow(4))
		self.top_menu.findChild(QPushButton, "btn_cloud").clicked.connect(lambda x : self.switchWindow(5))		

		self.bottom_menu.findChild(QPushButton, "btn_profile").clicked.connect(lambda x : self.switchWindow(6))		
		self.bottom_menu.findChild(QPushButton, "btn_quit").clicked.connect(lambda x : self.switchWindow(0))			
