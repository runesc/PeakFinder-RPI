import requests
import json
import pyAesCrypt
import qtawesome as qta
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QGraphicsDropShadowEffect, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QTimer
from PyQt5.QtGui import QColor

from core.modules.firebase import Firebase

class Cloud(QWidget, Firebase):
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
		super(Cloud, self).__init__()
		parent.window_size.connect(self.resize_event)

		self.parent = parent
		self.auth = self.Auth()
		self.db = self.RealTimeDB()
		self.storage = self.Storage()
		
		self.user_info = {}
		
		self.timer = QTimer(self)
		self.timer.start(300)
		self.timer.timeout.connect(self.hanldeUserInfo)


		self.selected_file = None


		self.loadUI()
		self.loadCSS()
		self.eventController()


	def loadUI(self):
		
		self.root_container = QWidget(self)
		self.root_container.setObjectName('root')
		self.root_container.resize(self.parent.largo, self.parent.alto)

		self.view_title = QLabel("Cloud<span style='font-weight:300'>Storage</span>", self.root_container)
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

		# Efecto sombra
		shadow = QGraphicsDropShadowEffect(color=QColor(0, 0, 0, 255 * 0.1), blurRadius=5, xOffset=5, yOffset=5)
		
		self.chart_container = QWidget(self.root_container)
		self.chart_container.setObjectName('chart_container')
		self.chart_container.setGraphicsEffect(shadow)

		self.file_list = QTreeWidget(self.chart_container)
		self.file_list.setObjectName("file_list")
		self.file_list.setHeaderLabels(["Archivo", "Tamaño", "", "", "", ""])
		self.file_list.setIndentation(0)

		self.file_list.setCursor(Qt.PointingHandCursor)

		self.button_container = QWidget(self.chart_container)
		self.button_container.setObjectName('boton_container')

		self.download_csv = QPushButton("Descargar csv", self.button_container)
		self.download_csv.setObjectName("download_csv")
		self.download_csv.setCursor(Qt.PointingHandCursor)

		self.download_pdf = QPushButton("Descargar pdf", self.button_container)
		self.download_pdf.setObjectName("download_pdf")
		self.download_pdf.setCursor(Qt.PointingHandCursor)

		self.load_csv = QPushButton("Cargar csv", self.button_container)
		self.load_csv.setObjectName("load_csv")
		self.load_csv.setCursor(Qt.PointingHandCursor)

	def switchWindow(self, view):
		self.parent.container.setCurrentIndex(view)


	def loadCSS(self):
		css = ApplicationContext().get_resource('styles/cloud.css') # obtener los estilos css
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

		self.chart_container.resize(self.percentage(92, self.root_container.width()), self.percentage(80, self.root_container.height()))
		self.chart_container.move(self.percentage(6, self.root_container.width()) - 8, self.percentage(10, self.root_container.height()))
		
		self.file_list.resize(self.percentage(95, self.chart_container.width()), self.percentage(89, self.chart_container.height()))
		self.file_list.move(self.percentage(2.5, self.chart_container.width()), self.percentage(5, self.chart_container.height()))

		self.button_container.resize(self.percentage(95, self.chart_container.width()), self.percentage(10, self.chart_container.height()))
		self.button_container.move(self.percentage(2.5, self.chart_container.width()), self.percentage(90, self.chart_container.height()))

		eje_x = 65

		for x in [self.download_csv, self.download_pdf, self.load_csv]:
			x.resize(self.percentage(10, self.chart_container.width()), 40)
			x.move(self.percentage(eje_x, self.chart_container.width()), int(self.button_container.height()/2 - x.height()/2))
			eje_x += 10

	#	for item in [self.]
	#	self.download_csv.move(self.percentage(5, self.chart_container.width()), self.percentage(85, self.chart_container.height()))



	
	def eventController(self):
		self.top_menu.findChild(QPushButton, "btn_home").clicked.connect(lambda x : self.switchWindow(2))
		self.top_menu.findChild(QPushButton, "btn_viewer").clicked.connect(lambda x : self.switchWindow(3))
		self.top_menu.findChild(QPushButton, "btn_streamer").clicked.connect(lambda x : self.switchWindow(4))
		self.top_menu.findChild(QPushButton, "btn_cloud").clicked.connect(lambda x : self.switchWindow(5))		

		self.bottom_menu.findChild(QPushButton, "btn_profile").clicked.connect(lambda x : self.switchWindow(6))		
		self.bottom_menu.findChild(QPushButton, "btn_quit").clicked.connect(lambda x : self.switchWindow(0))


		self.file_list.itemSelectionChanged.connect(self.test)
		self.download_csv.clicked.connect(lambda:self.download_file("csv"))
		self.download_pdf.clicked.connect(lambda:self.download_file("pdf"))
		

	def test(self):
		self.selected_file = self.file_list.selectedItems()


	def hanldeUserInfo(self):
		try:
			if self.parent.user_info:
				self.user_info = self.parent.user_info
				uid = self.user_info['localId']
				self.all_files = self.db.child("files/{}".format(uid)).get()

				if self.all_files.val():
					self.constructList()
				
				self.timer.stop()
		except AttributeError:
			pass

	def constructList(self):
		for file in self.all_files.each():
			self.topLevelItem = QTreeWidgetItem(self.file_list, [file.val()['file_name'], file.val()['size'], file.key()])

		
	def download_file(self, file_type):

		if self.selected_file:
			if file_type=='csv':
				fileName, _ = QFileDialog.getSaveFileName(self,"Save", "", "Portable Document Format (*.csv);;" "All files (*.*)")
				file_path=dict(self.db.child("files/{}".format(self.user_info['localId'])).get().val())[self.selected_file[0].text(2)]['path']
				self.storage.child(file_path).download(fileName)

			elif file_type=='pdf':
				fileName, _ = QFileDialog.getSaveFileName(self,"Save", "", "Portable Document Format (*.pdf);;" "All files (*.*)")
				file_path=dict(self.db.child("files/{}".format(self.user_info['localId'])).get().val())[self.selected_file[0].text(2)]['pdf_path']
				self.storage.child(file_path).download(fileName)			