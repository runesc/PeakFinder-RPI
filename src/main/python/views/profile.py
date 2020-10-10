import requests
import json
import pyAesCrypt
import qtawesome as qta
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QGraphicsDropShadowEffect, QVBoxLayout, QGridLayout, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QColor
from core.modules.firebase import Firebase

from components.roundedimg import RoundedImg

class Profile(QWidget, Firebase):
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
		super(Profile, self).__init__()
		parent.window_size.connect(self.resize_event)
		self.parent = parent
		self.auth = self.Auth()
		
		self.loadUI()
		self.loadCSS()
		self.eventController()


	def loadUI(self):
		
		self.root_container = QWidget(self)
		self.root_container.setObjectName('root')
		self.root_container.resize(self.parent.largo, self.parent.alto)

		self.view_title = QLabel("User<span style='font-weight:300'>Profile</span>", self.root_container)
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
			|		Container izquierdo	
			|
		"""			


		self.bg = QWidget(self.root_container)
		self.bg.setObjectName("bg")

		self.user_container = QWidget(self.root_container)
		self.user_container.setObjectName('user_container')
		self.user_container.setGraphicsEffect(QGraphicsDropShadowEffect(color=QColor(0, 0, 0, 255 * 0.1), blurRadius=5, xOffset=5, yOffset=5))


		# Poner foto y nombre aqui
		self.pp = RoundedImg("C:/Users/luisp/Pictures/Saved Pictures/PP.jpg", 150, self.user_container)


		self.user_name = QLabel("Usuario Registrado", self.user_container)
		self.user_name.setAlignment(Qt.AlignCenter)
		self.user_name.setObjectName("user_name")

		layout = QGridLayout()
		self.user_data_layout = QWidget(self.user_container)
		self.user_data_layout.setObjectName("user_data_layout")
		self.user_data_layout.setLayout(layout)

		object_id = ["status","status_val","projects_label", "projects_val", "gb_label", 
					"gb_val", "sessions", "sessions_val"]

		object_text = ["Proyectos", '0', "GB Disponibles", '0', "Sesiones activas", '0', "Estado", "activo"]		

		index = 0
		for x in range(4):
			for y in range(2):
					# Crear label, establecer texto y nombre de objeto
					label = QLabel(object_text[index])
					label.setObjectName(object_id[index])
					layout.addWidget(label, x, y) # Insertarlo en el layout		
					index += 1





		"""
			| 
			|		Container derecho
			|
		"""	
		self.edit_user_container = QWidget(self.root_container)
		self.edit_user_container.setObjectName('user_container')
		self.edit_user_container.setGraphicsEffect(QGraphicsDropShadowEffect(color=QColor(0, 0, 0, 255 * 0.1), blurRadius=5, xOffset=5, yOffset=5))

		self.form = QWidget(self.edit_user_container)
		self.form.setObjectName('formulary')

		self.name_label = QLabel("Nombre", self.form)
		self.name_label.setObjectName('input_label')
		
		self.name_input = QLineEdit(self.form)
		self.name_input.setObjectName('input')
		self.name_input.setPlaceholderText("Escribe tu nombre")

		self.last_name_label = QLabel("Apellido", self.form)
		self.last_name_label.setObjectName('input_label')
		
		self.last_name_input = QLineEdit(self.form)
		self.last_name_input.setObjectName('input')
		self.last_name_input.setPlaceholderText("Escribe tu apellido")

		self.email_label = QLabel("Email", self.form)
		self.email_label.setObjectName('input_label')

		self.email_label_input = QLineEdit(self.form)
		self.email_label_input.setObjectName('input')
		self.email_label_input.setPlaceholderText("Escribe tu email")


		self.update_btn = QPushButton("Guardar",self.form)
		self.update_btn.setObjectName("btn-primary")
		self.update_btn.setCursor(Qt.PointingHandCursor)




		# Efecto sombra
		#shadow = QGraphicsDropShadowEffect(color=QColor(0, 0, 0, 255 * 0.1), blurRadius=5, xOffset=5, yOffset=5)
		#shadow2 = QGraphicsDropShadowEffect(color=QColor(0, 0, 0, 255 * 0.1), blurRadius=5, xOffset=5, yOffset=5)

	def switchWindow(self, view):
		self.parent.container.setCurrentIndex(view)


	def loadCSS(self):
		css = ApplicationContext().get_resource('styles/profile.css') # obtener los estilos css
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

		self.bg.resize(self.percentage(96, self.root_container.width()), self.percentage(30, self.root_container.height()))
		self.bg.move(self.percentage(4, self.root_container.width()), 0)

		self.user_container.resize(self.percentage(25, self.root_container.width()), self.percentage(60, self.root_container.height()))
		self.user_container.move(self.percentage(6, self.root_container.width()), self.percentage(20, self.root_container.height()))

		self.edit_user_container.resize(self.percentage(64, self.root_container.width()), self.percentage(60, self.root_container.height()))
		self.edit_user_container.move(self.percentage(33, self.root_container.width()), self.percentage(20, self.root_container.height()))

		self.form.resize(self.percentage(95, self.edit_user_container.width()), self.percentage(95, self.edit_user_container.height()))
		self.form.move(self.percentage(2.5, self.edit_user_container.width()), self.percentage(2.5, self.edit_user_container.height()))

		self.name_label.move(0, self.percentage(8, self.form.height()))
		self.name_input.resize(self.percentage(45, self.form.width()), 40)
		self.name_input.move(0, self.percentage(14.5, self.form.height()))

		self.last_name_label.move(self.percentage(50, self.form.width()), self.percentage(8, self.form.height()))
		self.last_name_input.resize(self.percentage(45, self.form.width()), 40)
		self.last_name_input.move(self.percentage(50, self.form.width()), self.percentage(14.5, self.form.height()))

		self.email_label.move(0, self.percentage(27, self.form.height()))
		self.email_label_input.resize(self.percentage(45, self.form.width()), 40)
		self.email_label_input.move(0, self.percentage(33.5, self.form.height()))

		self.update_btn.resize(self.percentage(25, self.form.height()), 40)
		self.update_btn.move(self.form.width() - self.percentage(25, self.form.height()), self.form.height()-50)

		# contenedor derecho
		self.pp.move(int(self.user_container.width() / 2 - self.pp.width() / 2), self.percentage(5, self.user_container.height()))

		self.user_name.resize(self.user_container.width(), 30)
		self.user_name.move(0, self.percentage(41, self.user_container.height()))

		self.user_data_layout.resize(self.user_container.width(), self.percentage(50, self.user_container.height()))
		self.user_data_layout.move(0, self.percentage(50, self.user_container.height()))


	def eventController(self):
		self.top_menu.findChild(QPushButton, "btn_home").clicked.connect(lambda x : self.switchWindow(2))
		self.top_menu.findChild(QPushButton, "btn_viewer").clicked.connect(lambda x : self.switchWindow(3))
		self.top_menu.findChild(QPushButton, "btn_streamer").clicked.connect(lambda x : self.switchWindow(4))
		self.top_menu.findChild(QPushButton, "btn_cloud").clicked.connect(lambda x : self.switchWindow(5))		

		self.bottom_menu.findChild(QPushButton, "btn_profile").clicked.connect(lambda x : self.switchWindow(6))		
		self.bottom_menu.findChild(QPushButton, "btn_quit").clicked.connect(lambda x : self.switchWindow(0))			
