import requests
import json
import random
import string
import qtawesome as qta
#import pandas as pd
import core.modules.pyqtgraph as pg
from fpdf import FPDF
from datetime import datetime
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout, QVBoxLayout, QRadioButton, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QPropertyAnimation, QRect, QTimer
from PyQt5.QtGui import QPixmap, QColor

from core.modules.firebase import Firebase
from core.modules.pyqtgraph import PlotWidget, plot

#from core.models.DetectPeaks import detectPeaks
#from core.models.MM import mediaMovil
#from core.models.AR import AutoRegresive
#from core.models.SARIMA import modeloSARIMA
#from core.miscelaneous import compute_average, compute_std, compute_accuracy,compute_errormedio


from components.preloader import Preloader

class PeakViewer(QWidget, Firebase):
	"""
		Esta vista se encarga mostrar las opciones disponibles de la app

		Metodos:
			__init__ (func): Constructor de la clase
			loadUI (func): Cargar los widgets en este metodo.
			loadCSS (func): Cargar los estilos CSS en este metodo.
			resize_event (func): Detecta el tamaño de la ventana principal y se ajusta la vista dependiendo el tamaño.
			percentage (func): Calcula el porcentaje entre X y Y
			sizeXS (func): Configura la interfaz para pantallas pequeñas
			sizeLG (func): Configura la interfaz para pantallas pequeñas
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
				args (:obj: 'list', opcional): parametros indefinidos...

		"""
		super(PeakViewer, self).__init__()
		parent.window_size.connect(self.resize_event)
		self.parent = parent
		self.auth = self.Auth()
		self.db = self.RealTimeDB()
		self.storage = self.Storage()

		# Controladores de eventos
		self.chart_layer_lock = False
		self.csv_file = ""
		self.csv_data_x, self.csv_data_y = [], []
		self.data_to_predict = []
		self.peaks_list = []
		self.modelo = "MM"
		self.prediction_ = []
		self.load_down_graph = False
		self.pred_peak_x, self.pred_peak_y = [], []
		self.analyzed_file = ''
		self.user_info = {}



		# Primer Grafico
		self.peaks = '0'
		self.dp = '0s'
		self.desv = '0s'
		self.block = True

		# Segundo Grafico
		self.predict_peaks = '0'
		self.predict_precision = '0%'
		self.predict_error = '0s'


		self.timer = QTimer(self)
		self.timer.start(300)
		self.timer.timeout.connect(self.hanldeUserInfo)


		self.loadUI()
		self.loadCSS()
		self.eventController()


	def loadUI(self):
		self.root_container = QWidget(self)
		self.root_container.setObjectName('root')
		self.root_container.resize(self.parent.largo, self.parent.alto)

		# El preloader se superpone sobre los demás widgets por eso es el unico que lleva self
		self.preloader = Preloader(self)
		self.preloader.hide()


		self.view_title = QLabel("Peak<span style='font-weight:300'>Viewer</span>", self.root_container)
		self.view_title.setObjectName('view_title')

		# Nota: para evitar superposicion colocar antes la float_bar y despues el float_round_btn

		self.float_bar = QWidget(self.root_container)
		self.float_bar.setObjectName("round_bar_primary")

		option_layout = QHBoxLayout()

		self.option_container = QWidget(self.float_bar)
		self.option_container.setLayout(option_layout)
		self.option_container.setObjectName('opt_cont')
		self.option_container.hide()

		self.simply_report = QPushButton(qta.icon('fa5s.file-medical-alt', color="white"),"Reporte\nSimple", self.option_container)
		self.simply_report.setIconSize(QSize(24, 24))
		self.simply_report.setObjectName("simply_report")
		self.simply_report.setCursor(Qt.PointingHandCursor)


		self.complete_report = QPushButton(qta.icon('fa5s.file-medical-alt', color="white"),"Reporte\nCompleto", self.option_container)
		self.complete_report.setIconSize(QSize(24, 24))
		self.complete_report.setObjectName("complete_report")
		self.complete_report.setCursor(Qt.PointingHandCursor)

		# Boton para guardar el reporte (al activarlo se muestra float_bar) 
		self.float_round_btn = QPushButton(qta.icon('fa5s.save', active='fa5s.times', color="white"), "", self.root_container)
		self.float_round_btn.setObjectName("round_btn_primary")
		self.float_round_btn.setIconSize(QSize(32, 32))
		self.float_round_btn.setCheckable(True)
		self.float_round_btn.setCursor(Qt.PointingHandCursor)



		# Barra izquierda
		self.left_bar = QWidget(self.root_container)
		self.left_bar.setObjectName('left_bar')

		top_layout = QVBoxLayout()
		
		self.top_menu = QWidget(self.left_bar)
		self.top_menu.setLayout(top_layout)
		self.top_menu.setObjectName('top_menu')

		self.btn_home = QPushButton(qta.icon('fa5s.home', color="white"), "", self.top_menu)
		self.btn_home.setIconSize(QSize(28, 28))
		self.btn_home.setObjectName('btn_home')
		
		self.btn_viewer = QPushButton(qta.icon('fa5s.chart-bar', color="white"), "", self.top_menu)
		self.btn_viewer.setIconSize(QSize(28, 28))
		self.btn_viewer.setObjectName('btn_viewer')
		
		self.btn_streamer = QPushButton(qta.icon('fa5s.heartbeat', color="white"), "", self.top_menu)
		self.btn_streamer.setIconSize(QSize(28, 28))
		self.btn_streamer.setObjectName('btn_streamer')
		
		self.btn_cloud = QPushButton(qta.icon('fa5s.arrow-down', color="white"), "", self.top_menu)
		self.btn_cloud.setIconSize(QSize(28, 28))
		self.btn_cloud.setObjectName('btn_cloud')
		

		bottom_layout = QVBoxLayout()
		
		self.bottom_menu = QWidget(self.left_bar)
		self.bottom_menu.setLayout(bottom_layout)
		self.bottom_menu.setObjectName('bottom_menu')
		
		self.btn_profile = QPushButton(qta.icon('fa5s.user', color="white"), "", self.top_menu)
		self.btn_profile.setIconSize(QSize(28, 28))
		self.btn_profile.setObjectName('btn_profile')

		self.btn_quit = QPushButton(qta.icon('fa5s.sign-out-alt', color="white"), "", self.top_menu)
		self.btn_quit.setIconSize(QSize(28, 28))
		self.btn_quit.setObjectName('btn_quit')

		option_layout.addWidget(self.simply_report)
		option_layout.addWidget(self.complete_report)

		top_layout.addWidget(self.btn_home)
		top_layout.addWidget(self.btn_viewer)
		top_layout.addWidget(self.btn_streamer)
		top_layout.addWidget(self.btn_cloud)
		bottom_layout.addWidget(self.btn_profile)
		bottom_layout.addWidget(self.btn_quit)

		for x in range(top_layout.count()):
			widget = top_layout.itemAt(x).widget().setCursor(Qt.PointingHandCursor)
			

		for x in range(bottom_layout.count()):
			widget = bottom_layout.itemAt(x).widget().setCursor(Qt.PointingHandCursor)


		# Efecto sombra
		shadow = QGraphicsDropShadowEffect(color=QColor(0, 0, 0, 255 * 0.1), blurRadius=5, xOffset=5, yOffset=5)
		shadow2 = QGraphicsDropShadowEffect(color=QColor(0, 0, 0, 255 * 0.1), blurRadius=5, xOffset=5, yOffset=5)

		
		# ----------------------------------------- Primer grafico --------------------------------------
		self.chart_container = QWidget(self.root_container)
		self.chart_container.setObjectName('chart_container')
		self.chart_container.setGraphicsEffect(shadow2)
		self.chart_container.setMouseTracking(True)


		""" 
			Campo de resultados

			El campo de resultados es el area donde se muestran los resultados obtenidos por la carga del csv.

			Para crearlo fue necesario usar un QGridLayout el cual se monta sobre el widget 
			self.statistics_data, despues se crean 2 listas (object_list, label_content) donde se guardan
			los nombres de objetos (identificadores para manipular el contenido y los estilos) y 
			el contenido de las etiquetas

		"""
		self.statistics = QWidget(self.chart_container)
		self.statistics.setMouseTracking(True)

		grid_layout = QGridLayout()
		
		self.statistics_data = QWidget(self.statistics)
		self.statistics_data.setLayout(grid_layout)
		self.statistics_data.setMouseTracking(True)

		object_list = ["title", "peaks_val", "peaks_label", "prom_duration_val", 
						"prom_duration_label", "desv_val", "desv_label"]

		label_content = ["Estadisticas", self.peaks, "Peaks", self.dp, "Duración Promedio", 
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

		self.detect_peaks = QPushButton("Detectar", self.statistics)
		self.detect_peaks.setObjectName('btn-primary')
		self.detect_peaks.setCursor(Qt.PointingHandCursor)

		self.reset_chart = QPushButton("Limpiar", self.statistics)
		self.reset_chart.setObjectName('btn-secondary')
		self.reset_chart.setCursor(Qt.PointingHandCursor)


		# Chart (Campo de grafico)

		self.chart_widget = pg.PlotWidget(self.chart_container)
		self.chart_widget.setBackground("#414345")
		self.chart_widget.showGrid(y=True)
		self.chart_widget.getAxis("bottom").setPen(pg.mkPen(color="#414345", width=0))
		self.chart_widget.setMouseTracking(True)
		self.chart_widget.mouseMoveEvent = self.showLayer

		self.chart_layer = QWidget(self.chart_widget)
		self.chart_layer.setObjectName("chart_layer")
		self.chart_layer.setCursor(Qt.PointingHandCursor)
		self.chart_layer.hide()


		# Boton de carga de archivos

		self.chart_layer_btn = QPushButton("Cargar CSV",self.chart_layer)
		self.chart_layer_btn.setObjectName("btn-primary")
		self.chart_layer_btn.setCursor(Qt.PointingHandCursor)

		# Manipular el layer que se muestra sobre chart_widget

		self.chart_container.mouseMoveEvent = self.hideLayer
		self.statistics.mouseMoveEvent = self.hideLayer
		self.statistics_data.mouseMoveEvent = self.hideLayer


		# ----------------------------------------- Segundo grafico --------------------------------------
		grid_layout2 = QGridLayout()

		self.predict_container = QWidget(self.root_container)
		self.predict_container.setObjectName('chart_container')
		self.predict_container.setGraphicsEffect(shadow)


		self.prediction = QWidget(self.predict_container)
		self.prediction.setMouseTracking(True)


		self.prediction_data = QWidget(self.prediction)
		self.prediction_data.setLayout(grid_layout2)
		self.prediction_data.setMouseTracking(True)

		object_id = ["title", "prediction_peaks_val", "peaks_label", "precision_val", 
					"precision_label", "error_val", "error_label"]

		object_text = ["Estadisticas", self.predict_peaks, "Peaks", self.predict_precision, "Precisión", 
					self.predict_error, "Error medio"]

		index = 0
		for x in range(4):
			for y in range(2):
				if [x,y] != [0,1]:
					# Crear label, establecer texto y nombre de objeto
					label = QLabel(object_text[index])
					label.setObjectName(object_id[index])
					grid_layout2.addWidget(label, x, y) # Insertarlo en el layout		
					index += 1
	
		self.predict_peaks_btn = QPushButton("Predecir", self.prediction)
		self.predict_peaks_btn.setObjectName('btn-primary')
		self.predict_peaks_btn.setCursor(Qt.PointingHandCursor)

		self.reset_predict = QPushButton("Limpiar", self.prediction)
		self.reset_predict.setObjectName('btn-secondary')
		self.reset_predict.setCursor(Qt.PointingHandCursor)

		model_container = QHBoxLayout()
		model_container.setContentsMargins(0, 10, 0, 0)
		self.model_bar = QWidget(self.predict_container)
		self.model_bar.setLayout(model_container)
		self.model_bar.setObjectName("model_bar")


		object_id = ['mm_model', "ar_model", "sarima_model", "dft_model", "meta_model"]
		object_text = ["Modelo MM", "Modelo AR", "Modelo SARIMA", "Modelo DFT", "Meta modelo"]
		index = 0

		for x in range(5):
			radio = QRadioButton(object_text[x])
			radio.setObjectName(object_id[x])
			radio.setCursor(Qt.PointingHandCursor)
			model_container.addWidget(radio)
			index += 1

		self.model_bar.findChild(QRadioButton, "mm_model").setChecked(True)


		self.predict_chart = pg.PlotWidget(self.predict_container)
		self.predict_chart.setBackground("#414345")
		self.predict_chart.showGrid(y=True)
		self.predict_chart.getAxis("bottom").setPen(pg.mkPen(color="#414345", width=0))


	def hideLayer(self, event=None):
		self.chart_layer.hide()
	
	def switchWindow(self, view):
		self.parent.container.setCurrentIndex(view)

	def showLayer(self, event=None):
		if self.chart_layer_lock == False:
			self.chart_layer.show()


	def loadCSS(self):
		css = ApplicationContext().get_resource('styles/peakviewer.css') # obtener los estilos css
		with open(css, "r") as styles:
			self.setStyleSheet(styles.read())


	@pyqtSlot()
	def resize_event(self):
	
		self.root_container.resize(self.parent.largo, self.parent.alto)
		
		if self.parent.largo < 576:
			self.sizeXS()
		else:
			self.sizeLG()


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


	def sizeXS(self):
		self.left_bar.hide()
		self.retranslateUI()


	def sizeLG(self):
		self.left_bar.show()
		self.retranslateUI()


	def retranslateUI(self):
		
		self.left_bar.resize(self.percentage(4, self.root_container.width()), self.parent.alto)

		self.view_title.resize(self.percentage(20, self.root_container.width()), self.percentage(10, self.root_container.height()))
		self.view_title.move(self.percentage(5.5, self.root_container.width()), 0)

		self.float_round_btn.resize(self.percentage(7, self.root_container.height()), self.percentage(7, self.root_container.height()))
		self.float_round_btn.move(int(self.root_container.width() - self.percentage(7, self.root_container.width())), self.percentage(1.5, self.root_container.height()))

		#self.float_bar.resize(self.percentage(25, self.root_container.width()), self.percentage(7, self.root_container.height()))
		self.top_menu.resize(self.left_bar.width(), self.percentage(40, self.left_bar.height()))
		self.top_menu.move(0, self.percentage(8, self.left_bar.height()))

		self.bottom_menu.resize(self.left_bar.width(), self.percentage(20, self.left_bar.height()))
		self.bottom_menu.move(0,  self.percentage(75, self.left_bar.height()))


		if self.float_round_btn.isChecked():		

			self.float_bar.resize(self.percentage(25, self.root_container.width()), self.percentage(7, self.root_container.height()))
			self.float_bar.move(self.float_round_btn.x() - self.float_bar.width() + self.float_round_btn.width() , self.percentage(1.5, self.root_container.height()))

		else:
			self.float_bar.resize(self.percentage(7, self.root_container.height()), self.percentage(7, self.root_container.height()))
			self.float_bar.move(self.float_round_btn.x() - self.float_bar.width() + self.float_round_btn.width() , self.percentage(1.5, self.root_container.height()))

		self.option_container.resize(self.percentage(70, self.float_bar.width()), self.float_bar.height())
		self.option_container.move(self.percentage(14.5, self.float_bar.width()), 0)

		self.simply_report.resize(self.simply_report.width(), self.option_container.height())
		self.simply_report.move(0,0)

		self.complete_report.resize(self.complete_report.width(), self.option_container.height())
		self.complete_report.move(self.simply_report.width(), 0)		

		if self.parent.largo > 576:

			# Primer contenedor

			self.chart_container.resize(self.percentage(92, self.root_container.width()), self.percentage(40, self.root_container.height()))
			self.chart_container.move(self.percentage(6, self.root_container.width()) - 8, self.percentage(10, self.root_container.height()))
		
			self.statistics.resize(self.percentage(30, self.chart_container.width()),self.percentage(80, self.chart_container.height()))
			self.statistics.move(self.percentage(1, self.chart_container.width()),self.percentage(10, self.chart_container.height()))

			self.statistics_data.resize(self.percentage(95, self.statistics.width()), self.percentage(80, self.statistics.height()))
			self.statistics_data.move(self.percentage(2.5, self.statistics.width()), self.percentage(0, self.statistics.height()))

			self.detect_peaks.resize(self.percentage(37, self.statistics.width()), 40)
			self.detect_peaks.move(self.percentage(7, self.statistics.width()), self.percentage(82, self.statistics.height()))

			self.reset_chart.resize(self.percentage(37, self.statistics.width()), 40)
			self.reset_chart.move(self.percentage(48, self.statistics.width()), self.percentage(82, self.statistics.height()))

			self.chart_widget.resize(self.percentage(68, self.chart_container.width()),self.percentage(80, self.chart_container.height()))
			self.chart_widget.move(self.percentage(29.5, self.chart_container.width()), self.percentage(10, self.chart_container.height()))

			self.chart_layer.resize(self.chart_widget.frameSize())
			self.chart_layer_btn.resize(self.percentage(55, self.statistics.width()), 30)
			self.chart_layer_btn.move(int(self.chart_layer.frameSize().width() / 2 - self.chart_layer_btn.frameSize().width() / 2), int(self.chart_layer.frameSize().height() / 2 - self.chart_layer_btn.frameSize().height() / 2))


			# Segundo contenedor

			self.predict_container.resize(self.percentage(92, self.root_container.width()), self.percentage(40, self.root_container.height()))
			self.predict_container.move(self.percentage(6, self.root_container.width()) - 8, self.percentage(53, self.root_container.height()))

			self.prediction.resize(self.percentage(30, self.predict_container.width()),self.percentage(80, self.predict_container.height()))
			self.prediction.move(self.percentage(1, self.predict_container.width()),self.percentage(10, self.predict_container.height()))

			self.prediction_data.resize(self.percentage(95, self.prediction.width()), self.percentage(80, self.prediction.height()))
			self.prediction_data.move(self.percentage(2.5, self.prediction.width()), self.percentage(0, self.prediction.height()))

			self.predict_peaks_btn.resize(self.percentage(37, self.prediction.width()), 40)
			self.predict_peaks_btn.move(self.percentage(7, self.prediction.width()), self.percentage(82, self.prediction.height()))

			self.reset_predict.resize(self.percentage(37, self.prediction.width()), 40)
			self.reset_predict.move(self.percentage(48, self.prediction.width()), self.percentage(82, self.prediction.height()))
		
			self.model_bar.resize(self.percentage(66, self.predict_container.width()), self.percentage(17, self.predict_container.height()))
			self.model_bar.move(self.percentage(32, self.predict_container.width()), 0)

			self.predict_chart.resize(self.percentage(68, self.predict_container.width()),self.percentage(80, self.predict_container.height()))
			self.predict_chart.move(self.percentage(29.5, self.predict_container.width()), self.percentage(20, self.chart_container.height()))


		else:
			self.chart_container.resize(self.percentage(90, self.root_container.width()), self.percentage(45, self.root_container.height()))
			self.chart_container.move(self.percentage(5, self.root_container.width()) - 8, self.percentage(1.5, self.root_container.height()))

			self.predict_container.resize(self.percentage(90, self.root_container.width()), self.percentage(45, self.root_container.height()))
			self.predict_container.move(self.percentage(5, self.root_container.width()) - 8, self.percentage(47.5, self.root_container.height()))

			self.statistics.resize(self.percentage(100, self.chart_container.width()),self.percentage(30, self.chart_container.height()))


	def eventController(self):
		self.btn_home.clicked.connect(lambda x : self.switchWindow(2))
		self.btn_viewer.clicked.connect(lambda x : self.switchWindow(3))
		self.btn_streamer.clicked.connect(lambda x : self.switchWindow(4))
		self.btn_cloud.clicked.connect(lambda x : self.switchWindow(5))
		self.btn_profile.clicked.connect(lambda x : self.switchWindow(6))
		self.btn_quit.clicked.connect(lambda x : self.logout())

		#self.simply_report.clicked.connect()

		# Top Section
		self.float_round_btn.clicked.connect(self.float_bar_anim)
		self.chart_layer_btn.clicked.connect(self.loadCSV)
		self.detect_peaks.clicked.connect(self.graphPeaks)
		self.reset_chart.clicked.connect(self.resetCharts)

		# Down Section 

		self.model_bar.findChild(QRadioButton, "mm_model").toggled.connect(lambda:self.setModel("MM"))
		self.model_bar.findChild(QRadioButton, "ar_model").toggled.connect(lambda:self.setModel("AR"))
		self.model_bar.findChild(QRadioButton, "sarima_model").toggled.connect(lambda:self.setModel("SARIMA"))
		self.model_bar.findChild(QRadioButton, "dft_model").toggled.connect(lambda:self.setModel("DFT"))
		self.model_bar.findChild(QRadioButton, "meta_model").toggled.connect(lambda:self.setModel("Meta"))


		self.predict_peaks_btn.clicked.connect(self.makePrediction)

		self.reset_predict.clicked.connect(self.clearPrediction)

		self.simply_report.clicked.connect(self.genSimpleReport)



	# ----------------------------------- Eventos -------------------------


	def float_bar_anim(self, status):
		if self.float_round_btn.isChecked():
			self.float_bar.resize(self.percentage(25, self.root_container.width()), self.percentage(7, self.root_container.height()))
			self.float_bar.move(self.float_round_btn.x() - self.float_bar.width() + self.float_round_btn.width() , self.percentage(1.5, self.root_container.height()))
			
			self.float_round_btn.setIcon(qta.icon('fa5s.times', color="white"))

			self.option_container.resize(self.percentage(70, self.float_bar.width()), self.float_bar.height())
			self.option_container.move(self.percentage(14.5, self.float_bar.width()), 0)			

			self.option_container.show()
			
			self.simply_report.resize(self.simply_report.width(), self.option_container.height())
			self.simply_report.move(0,0)

			self.complete_report.resize(self.complete_report.width(), self.option_container.height())
			self.complete_report.move(self.simply_report.width(), 0)		
		else:
			self.float_bar.resize(self.percentage(7, self.root_container.height()), self.percentage(7, self.root_container.height()))
			self.float_bar.move(self.float_round_btn.x() - self.float_bar.width() + self.float_round_btn.width() , self.percentage(1.5, self.root_container.height()))
			self.float_round_btn.setIcon(qta.icon('fa5s.save', color="white"))
			self.option_container.hide()


	def loadCSV(self):
		try:
			self.csv_file, _ = QFileDialog.getOpenFileName(self, "Open File", "main", "Comma Separate Value (*.csv);;" "All files (*.*)")
			if self.csv_file:
				with open(self.csv_file, 'r') as file:
					data = pd.read_csv(file)
					data.columns = ['ts','sensor']
					self.analyzed_file=(self.csv_file.split('/'))[-1]

					for entry in range(len(data)):
						self.csv_data_x.append(data.loc[entry,'ts'])
						self.csv_data_y.append(data.loc[entry,'sensor'])				

				self.replot()

				#self.chart_widget.mouseMoveEvent = None
				self.chart_layer.hide()
				self.chart_layer_lock = True

		except FileNotFoundError as e:
			print("Mostrar notification component")

	def logout(self):
		self.switchWindow(0)
	def graphPeaks(self):
		try:
			self.data_to_predict = self.csv_data_y[:]
			self.peaks_list = detectPeaks(self.csv_data_y)
			self.peaks = len(self.peaks_list)
			self.dp = compute_average(self.peaks_list)
			self.desv = compute_std(self.peaks_list)

			peaks_x = self.peaks_list
			peaks_y = [750] * self.peaks


			self.statistics_data.findChild(QLabel, 'peaks_val').setText(str(self.peaks))
			self.statistics_data.findChild(QLabel, 'prom_duration_val').setText(str("{:.1f}".format(self.dp)) + 's')
			self.statistics_data.findChild(QLabel, 'desv_val').setText(str("{:.1f}".format(self.desv)) + 's')

			self.add_peaks = self.chart_widget.plot(peaks_x, peaks_y, symbol='o', symbolSize=10, symbolBrush=('b'))
		
		except ValueError as e:
			print("Notificacion")


	def resetCharts(self):
		try:
			self.csv_data_x, self.csv_data_y = [], []
			self.prediccion = []
			self.peaks_list = []

			self.peaks = 0
			self.dp = 0
			self.desv = 0

			self.chart_graph.setData(self.csv_data_x, self.csv_data_y)
			self.add_peaks.setData(self.csv_data_x, self.csv_data_y)
			self.statistics_data.findChild(QLabel, 'peaks_val').setText(str(self.peaks))
			self.statistics_data.findChild(QLabel, 'prom_duration_val').setText(str("{:.1f}".format(self.dp)) + 's')
			self.statistics_data.findChild(QLabel, 'desv_val').setText(str("{:.1f}".format(self.desv)) + 's')

			# Reset prediction results (segundo grafico)
			self.prediction_ = []
			self.predict_peaks = 0
			self.predict_precision = 0
			self.predict_error = 0

			self.pred_peak_x = []
			self.pred_peak_y = []

			self.prediction_data.findChild(QLabel, 'prediction_peaks_val').setText(str(self.predict_peaks))
			self.prediction_data.findChild(QLabel, 'precision_val').setText(str("{:.1f}%".format(self.predict_precision)))
			self.prediction_data.findChild(QLabel, 'error_val').setText(str("{:.1f}s".format(self.predict_error)))

			self.graph_peaks.setData(self.pred_peak_x, self.pred_peak_y)
			# Reset prediction graph
			self.down_graph.setData(self.csv_data_x, self.csv_data_y)

			# Unlock chart layer
			self.chart_layer.hide()
			self.chart_layer_lock = False

		except AttributeError as e:
			print("File not found")


	def setModel(self, model):
		self.modelo = model


	def makePrediction(self):
		if self.prediction_ == []:
			if self.modelo == "MM":
				self.prediction_ = mediaMovil(self.peaks_list)
			elif self.modelo == "AR":
				self.prediction_ = AutoRegresive(self.peaks_list, self.data_to_predict)
			elif self.modelo == "SARIMA":
				self.prediction_ = modeloSARIMA(self.peaks_list, self.data_to_predict)
			elif self.modelo == "DFT":
				pass
			elif self.modelo == "Meta":
				pass
		
			self.predict_peaks = len(self.prediction_)
			self.predict_precision = compute_accuracy(self.peaks_list[3:], self.prediction_)
			self.predict_error = compute_errormedio(self.peaks_list[3:],self.prediction_)

			self.prediction_data.findChild(QLabel, 'prediction_peaks_val').setText(str(self.predict_peaks))
			self.prediction_data.findChild(QLabel, 'precision_val').setText(str("{:.1f}%".format(self.predict_precision)))
			self.prediction_data.findChild(QLabel, 'error_val').setText(str("{:.1f}s".format(self.predict_error)))


			self.pred_peak_x = self.prediction_
			self.pred_peak_y = [750] * len(self.pred_peak_x)


			if self.load_down_graph == False:
				self.down_graph = self.predict_chart.plot(self.csv_data_x, self.csv_data_y)
				self.load_down_graph = True
			
			self.graph_peaks = self.predict_chart.plot(self.pred_peak_x, self.pred_peak_y,symbol='o',symbolSize=10,symbolBrush=('b'))


	def clearPrediction(self):
		self.prediction_ = []
		self.predict_peaks = 0
		self.predict_precision = 0
		self.predict_error = 0

		self.pred_peak_x = []
		self.pred_peak_y = []

		self.prediction_data.findChild(QLabel, 'prediction_peaks_val').setText(str(self.predict_peaks))
		self.prediction_data.findChild(QLabel, 'precision_val').setText(str("{:.1f}%".format(self.predict_precision)))
		self.prediction_data.findChild(QLabel, 'error_val').setText(str("{:.1f}s".format(self.predict_error)))


		self.graph_peaks.setData(self.pred_peak_x, self.pred_peak_y)

	def genSimpleReport(self):
		fileName, _ = QFileDialog.getSaveFileName(self,"Save", "", "Portable Document Format (*.pdf);;" "All files (*.*)")
		
		if fileName:

			fecha = datetime.today().strftime('%d-%m-%Y a las %H:%M')
			creation_date = "Reporte generado el dia " + fecha
			report_name = "Analisis del archivo " + self.analyzed_file

			pdf = FPDF(orientation="P")
			pdf.add_page()
			pdf.set_font("Courier",size=8)
			pdf.cell(0,5,ln=1,txt=creation_date,align="R")
			pdf.set_font("Courier",size=18)
			pdf.cell(0,25,ln=1,txt=report_name,align="C")
			pdf.set_font("Courier",size=10)
			pdf.cell(0,5,ln=1,txt="                     Registro   Prediccion         Error",align="L")
			
			i=0
			
			for peak in self.peaks_list[:3]:
				pdf.cell(0,5,ln=1,txt="Contraccion numero {}   {} s       ***Entrenamiento***".format(i+1,int(self.peaks_list[i]/10)),align="L")
				i+=1
			
			for peak in range(len(self.prediction_)):
				error = self.peaks_list[i] - self.prediction_[i-3]
				pdf.cell(0,5,ln=1,txt="Contraccion numero {}   {} s    {} s     {:.2f} s  ".format(i+1,int(self.peaks_list[i]/10),int(self.prediction_[i-3]/10), error /10),align="L")
				i+=1

			pdf.cell(0,15,ln=1,txt="Estadisticas prediccion    ",align="L")
			pdf.set_font("Courier",size=8)
			pdf.cell(0,5,ln=1,txt="Numero de peaks detectados    "+str(self.peaks),align="L")
			pdf.cell(0,5,ln=1,txt="Promedio entre peaks (s)      "+str("{:.2f}".format(self.dp)),align="L")
			pdf.cell(0,5,ln=1,txt="Desviacion estandar (s)       "+str("{:.2f}".format(self.desv)),align="L")
			pdf.cell(0,5,ln=1,txt="Numero de peaks predichos     "+str(self.predict_peaks),align="L")
			pdf.cell(0,5,ln=1,txt="Precision (%)                 "+str("{:.2f}".format(self.predict_precision)),align="L")
			pdf.cell(0,5,ln=1,txt="Error promedio (s)            "+str("{:.2f}".format(self.predict_error)),align="L")

			pdf.output(fileName)

			uid = self.user_info['localId']
			file_ = fileName.split("/")[-1]
			self.storage.child("{}/pdf/{}".format(uid, file_)).put(fileName)
			id_file = self.file_id_gen()
			file__ = file_.split('.')[0]
			
			query = {
				"files/{}/{}/".format(uid, id_file):{
				"comments": "archivo subido wiii",
				"file_name": file__,
				"path":"{}/pdf/{}".format(uid, file_),
				"pdf_path": "{}/pdf/{}".format(uid, file_),
				"size": "24Kb",
				}
			}
			self.db.update(query)

	def file_id_gen(self, lenght=28):
		word_bag = string.ascii_letters + string.digits
		return ''.join(random.choice(word_bag) for i in range(lenght))

	# ----------------------------------- Refreshers -------------------------

	def replot(self):
		self.chart_graph = self.chart_widget.plot(self.csv_data_x, self.csv_data_y)

	
	def hanldeUserInfo(self):
		try:
			if self.parent.user_info:
				self.user_info = self.parent.user_info
				#print(self.user_info)
				self.timer.stop()
		except AttributeError:
			pass
