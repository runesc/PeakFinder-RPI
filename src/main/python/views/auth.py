import requests
import json
import pyAesCrypt
from pathlib import Path
import logging
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QPixmap

from core.modules.firebase import Firebase
from components.notification import Notification

class SignIn(QWidget, Firebase):
	"""
		Esta vista se encarga del proceso de inicio de sesion de los usuarios registrados.

		Metodos:
			__init__ (func): Constructor de la clase
			loadUI (func): Cargar los widgets en este metodo.
			loadCSS (func): Cargar los estilos CSS en este metodo.
			resize_event (func): Detecta el tamaño de la ventana principal y se ajusta dependiendo el tamaño.
			switchWindow (func): Realiza el cambio de pestañas de la app
			authenticate (func): Proceso de inicio de sesion, almacenamiento de tokens y refresco de sesion
			refreshSession (func): Refresca la sesion del usuario cada hora para evitar bloqueo de funciones
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
				args (:obj: 'list', opcional): parametros indefinidos.

		"""
		super(SignIn, self).__init__()
		parent.screen_size_signal.connect(self.resize_event)
		self.parent = parent
		self.auth = self.Auth()
		self.loadUI()
		self.loadCSS()


	def loadUI(self):
	
		self.root_container = QWidget(self)
		self.root_container.setObjectName('root')
		self.root_container.resize(self.parent.width(), self.parent.height())


		#: Flex display: se oculta left_side por default (solamente cuando la pantalla es menor a 768px)

		self.right_side = QWidget(self.root_container)
		self.right_side.setObjectName("right_side")
		self.left_side = QWidget(self.root_container)
		self.left_side.setObjectName("left_side")
		

		# Right Side (jumbotron)
		self.bg_img = QLabel(self.left_side)
		self.bg_img.setPixmap(QPixmap(ApplicationContext().get_resource('img/chart-min.jpg')))
		self.bg_img.setScaledContents(True)

		self.jumbotron = QWidget(self.left_side)
		self.jumbotron.setObjectName("jumbotron-bg")

		
		self.jumbotron_header = QLabel("PeakFinder", self.jumbotron)
		self.jumbotron_header.setAlignment(Qt.AlignCenter)
		self.jumbotron_header.setObjectName("jumbotron-head")
		
		self.jumbotron_body = QLabel("""Herramienta para la detección y análisis de contracciones en tiempo real.""", self.jumbotron)
		self.jumbotron_body.setObjectName("jumbotron-body")
		self.jumbotron_body.setWordWrap(True)
		self.jumbotron_body.setAlignment(Qt.AlignCenter)

		# Left Side (form)

		self.form_container = QWidget(self.right_side)
		self.form_container.setObjectName("form_container")

		self.footer = QLabel(self.form_container)
		self.footer.setPixmap(QPixmap(ApplicationContext().get_resource('img/waves.png')))
		self.footer.move(0, 310)
		self.footer.setScaledContents(True)
		
		self.email = QLineEdit(self.form_container)
		self.email.setPlaceholderText("Escribe tu email")
		self.email.setClearButtonEnabled(True)
		self.email.setObjectName("input")

		self.password = QLineEdit(self.form_container)
		self.password.setPlaceholderText("Escribe tu contraseña")
		self.password.setEchoMode(QLineEdit.Password)
		self.password.setClearButtonEnabled(True)
		self.password.setObjectName("input")

		self.sign_in = QPushButton("Iniciar sesión", self.form_container)
		self.sign_in.setObjectName("btn-primary")
		self.sign_in.setCursor(Qt.PointingHandCursor)

		self.register = QLabel("¿No tienes cuenta? <b>Registrate</b>", self.form_container)
		self.register.setObjectName("register")
		self.register.setAlignment(Qt.AlignCenter)
		self.register.setCursor(Qt.PointingHandCursor)


		self.sign_in.clicked.connect(self.authenticate)
		self.email.returnPressed.connect(self.authenticate)
		self.password.returnPressed.connect(self.authenticate)
		self.register.mousePressEvent = self.switchWindow


	def loadCSS(self):
	
		css = ApplicationContext().get_resource('styles/auth.css') # obtener los estilos css
		with open(css, "r") as styles:
			self.setStyleSheet(styles.read())


	@pyqtSlot()
	def resize_event(self):

		self.root_container.resize(self.parent.largo, self.parent.alto)

		if self.parent.largo < 768:
			self.sizeXS()
		else:
			self.sizeLG()

	
	def switchWindow(self, event):

		self.parent.container.setCurrentIndex(1)


	def authenticate(self):
		try:
			self.user = self.auth.sign_in_with_email_and_password(self.email.text(), self.password.text())
			self.user = str(self.user).replace("'", '"')
			
			
			with open(str(Path.home()) + '/PeakFinder/private.json', "w") as file:
				file.write(str(self.user))
				file.close()
			
			self.user = eval(self.user)
			self.parent.user_info = self.user

			refresh_session = QTimer(self)
			refresh_session.timeout.connect(self.refreshSession)
			refresh_session.start(3.528e+6) # Call this function each 58.8 minutes (3.528e+6ms)

			self.parent.container.setCurrentIndex(2)

		except requests.exceptions.HTTPError as error:
			print(error)
				#error_json = error.args[1]
				#error_json = json.loads(error_json)['error']			


	def refreshSession(self):
		new_token = self.auth.refresh(self.user['refreshToken'])
		with open(str(Path.home()) + '/PeakFinder/private.json', 'r+') as json_file:
			data = json_file.read()
			json_file.seek(0)
			
			data = eval(data)
			data['idToken'] = new_token['idToken']
			self.parent.user_info = data
			json_file.write(str(data))
			
			json_file.truncate()
			json_file.close()



	@staticmethod
	def percentage(percent, of):
		"""
			return:
				porcentaje (:obj:`int`): parent object.
		"""				
		return int((percent * of) / 100.0)


	def sizeXS(self):

		self.left_side.hide()
		self.right_side.resize(self.parent.largo, self.parent.alto)
		self.right_side.move(0, 0)
		self.retranslateUI()


	def sizeLG(self):

		self.left_side.show()
		self.left_side.resize(self.percentage(65, self.parent.largo), self.parent.alto)
		self.right_side.resize(self.percentage(35, self.parent.largo), self.parent.alto)
		self.right_side.move(self.percentage(65, self.parent.largo), 0)
		self.retranslateUI()


	def retranslateUI(self):
		# Left side
		self.bg_img.resize(self.left_side.frameSize())
		self.jumbotron.resize(self.left_side.frameSize())

		self.jumbotron_header.resize(self.left_side.frameSize().width(), 65)
		self.jumbotron_header.move(0, int(self.parent.alto / 2) - 100)
		self.jumbotron_body.resize(self.left_side.frameSize().width() / 2, 120)
		self.jumbotron_body.move(self.left_side.frameSize().width() / 4, int(self.parent.alto / 2.2))


		# Right side
		self.form_container.resize(self.right_side.frameSize().width(),self.parent.alto)

		self.email.resize(self.percentage(76, self.form_container.frameSize().width()), 50) # ocupa 80% del form_container
		self.email.move(self.percentage(12, self.form_container.frameSize().width()) - 10, 230)

		self.password.resize(self.percentage(76, self.form_container.frameSize().width()), 50) # ocupa 80% del form_container
		self.password.move(self.percentage(12, self.form_container.frameSize().width()) - 10, 300)

		self.sign_in.resize(self.percentage(76, self.form_container.frameSize().width()), 40)
		self.sign_in.move(self.percentage(12, self.form_container.frameSize().width()) - 10, 380)

		self.register.resize(self.form_container.frameSize().width(), 40)
		self.register.move(0, 480)


		self.footer.resize(self.right_side.frameSize().width(), 400)


class SignUp(QWidget, Firebase):
	"""
		Esta vista se encarga del proceso de inicio de sesion de los usuarios registrados.

		Metodos:
			__init__ (func): Constructor de la clase
			loadUI (func): Cargar los widgets en este metodo.
			loadCSS (func): Cargar los estilos CSS en este metodo.
			resize_event (func): Detecta el tamaño de la ventana principal y se ajusta dependiendo el tamaño.
			switchWindow (func): Realiza el cambio de pestañas de la app
			authenticate (func): Proceso de inicio de sesion, almacenamiento de tokens y refresco de sesion
			refreshSession (func): Refresca la sesion del usuario cada hora para evitar bloqueo de funciones
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
				args (:obj: 'list', opcional): parametros indefinidos.

		"""
		super(SignUp, self).__init__()
		parent.window_size.connect(self.resize_event)
		self.parent = parent
		self.auth = self.Auth()
		self.db = self.RealTimeDB()
		self.loadUI()
		self.loadCSS()


	def loadUI(self):

		self.root_container = QWidget(self)
		self.root_container.setObjectName('root')
		self.root_container.resize(self.parent.largo, self.parent.alto)


		#: Flex display: se oculta left_side por default (solamente cuando la pantalla es menor a 768px)

		self.right_side = QWidget(self.root_container)
		self.right_side.setObjectName("right_side")
		self.left_side = QWidget(self.root_container)
		self.left_side.setObjectName("left_side")
		

		# Right Side (jumbotron)
		self.bg_img = QLabel(self.left_side)
		self.bg_img.setPixmap(QPixmap(ApplicationContext().get_resource('img/chart-min.jpg')))
		self.bg_img.setScaledContents(True)

		self.jumbotron = QWidget(self.left_side)
		self.jumbotron.setObjectName("jumbotron-bg")

		
		self.jumbotron_header = QLabel("PeakFinder", self.jumbotron)
		self.jumbotron_header.setAlignment(Qt.AlignCenter)
		self.jumbotron_header.setObjectName("jumbotron-head")
		
		self.jumbotron_body = QLabel("""Herramienta para la detección y análisis de contracciones en tiempo real.""", self.jumbotron)
		self.jumbotron_body.setObjectName("jumbotron-body")
		self.jumbotron_body.setWordWrap(True)
		self.jumbotron_body.setAlignment(Qt.AlignCenter)

		# Left Side (form)

		self.form_container = QWidget(self.right_side)
		self.form_container.setObjectName("form_container")

		self.footer = QLabel(self.form_container)
		self.footer.setPixmap(QPixmap(ApplicationContext().get_resource('img/waves.png')))
		self.footer.move(0, 310)
		self.footer.setScaledContents(True)
		
		self.email = QLineEdit(self.form_container)
		self.email.setPlaceholderText("Escribe tu email")
		self.email.setClearButtonEnabled(True)
		self.email.setObjectName("input")

		self.password = QLineEdit(self.form_container)
		self.password.setPlaceholderText("Escribe tu contraseña")
		self.password.setEchoMode(QLineEdit.Password)
		self.password.setClearButtonEnabled(True)
		self.password.setObjectName("input")

		self.confirm_password = QLineEdit(self.form_container)
		self.confirm_password.setPlaceholderText("Confirma tu contraseña")
		self.confirm_password.setEchoMode(QLineEdit.Password)
		self.confirm_password.setClearButtonEnabled(True)
		self.confirm_password.setObjectName("input")


		self.sign_in = QPushButton("Registrarme", self.form_container)
		self.sign_in.setObjectName("btn-primary")
		self.sign_in.setCursor(Qt.PointingHandCursor)

		self.register = QLabel("Ya tengo cuenta. <b>Iniciar sesión</b>", self.form_container)
		self.register.setObjectName("register")
		self.register.setAlignment(Qt.AlignCenter)
		self.register.setCursor(Qt.PointingHandCursor)


		self.sign_in.clicked.connect(self.authenticate)
		self.email.returnPressed.connect(self.authenticate)
		self.password.returnPressed.connect(self.authenticate)		
		self.register.mousePressEvent = self.switchWindow


	def loadCSS(self):
		"""
			The __init__ method may be documented in either the class level
			docstring, or as a docstring on the __init__ method itself.

			Either form is acceptable, but the two should not be mixed. Choose one
			convention to document the __init__ method and be consistent with it.		
		"""		
		css = ApplicationContext().get_resource('styles/auth.css') # obtener los estilos css
		with open(css, "r") as styles:
			self.setStyleSheet(styles.read())


	@pyqtSlot()
	def resize_event(self):
		self.root_container.resize(self.parent.largo, self.parent.alto)

		if self.parent.largo < 768:
			self.sizeXS()
		else:
			self.sizeLG()

	
	def switchWindow(self, event):
		self.parent.container.setCurrentIndex(0)


	def authenticate(self):
		try:
			self.user = self.auth.create_user_with_email_and_password(self.email.text(), self.password.text())
			self.user = str(self.user).replace("'", '"')


			"""
				create profile bucket (realtimedb)

			"""
			
			
			
			with open(str(Path.home()) + '/PeakFinder/private.json', "w") as file:
				file.write(str(self.user))
				file.close()
			
			self.user = eval(self.user)
			self.parent.user_info = self.user

			refresh_session = QTimer(self)
			refresh_session.timeout.connect(self.refreshSession)
			refresh_session.start(3.528e+6) # Call this function each 58.8 minutes (3.528e+6ms)

			self.parent.container.setCurrentIndex(0)

		except requests.exceptions.HTTPError as error:
			print(error)
				#error_json = error.args[1]
				#error_json = json.loads(error_json)['error']			


	def refreshSession(self):
		new_token = self.auth.refresh(self.user['refreshToken'])
		with open(str(Path.home()) + '/PeakFinder/private.json', 'r+') as json_file:
			data = json_file.read()
			json_file.seek(0)
			
			data = eval(data)
			data['idToken'] = new_token['idToken']
			self.parent.user_info = data
			json_file.write(str(data))
			
			json_file.truncate()
			json_file.close()


	@staticmethod
	def percentage(percent, of):
		"""
			return:
				porcentaje (:obj:`int`): parent object.
		"""				
		return int((percent * of) / 100.0)


	def sizeXS(self):
		self.left_side.hide()
		self.right_side.resize(self.parent.largo, self.parent.alto)
		self.right_side.move(0, 0)
		self.retranslateUI()


	def sizeLG(self):
		self.left_side.show()
		self.left_side.resize(self.percentage(65, self.parent.largo), self.parent.alto)
		self.right_side.resize(self.percentage(35, self.parent.largo), self.parent.alto)
		self.right_side.move(self.percentage(65, self.parent.largo), 0)
		self.retranslateUI()


	def retranslateUI(self):
		# Left side
		self.bg_img.resize(self.left_side.frameSize())
		self.jumbotron.resize(self.left_side.frameSize())

		self.jumbotron_header.resize(self.left_side.frameSize().width(), 65)
		self.jumbotron_header.move(0, int(self.parent.alto / 2) - 100)
		self.jumbotron_body.resize(self.left_side.frameSize().width() / 2, 120)
		self.jumbotron_body.move(self.left_side.frameSize().width() / 4, int(self.parent.alto / 2))


		# Right side
		self.form_container.resize(self.right_side.frameSize().width(),self.parent.alto)

		self.email.resize(self.percentage(76, self.form_container.frameSize().width()), 50) # ocupa 76% del form_container
		self.email.move(self.percentage(12, self.form_container.frameSize().width()) - 10, 160)

		self.password.resize(self.percentage(76, self.form_container.frameSize().width()), 50) # ocupa 76% del form_container
		self.password.move(self.percentage(12, self.form_container.frameSize().width()) - 10, 230)

		self.confirm_password.resize(self.percentage(76, self.form_container.frameSize().width()), 50) # ocupa 76% del form_container
		self.confirm_password.move(self.percentage(12, self.form_container.frameSize().width()) - 10, 300)

		self.sign_in.resize(self.percentage(76, self.form_container.frameSize().width()), 40) # ocupa 76% del form_container
		self.sign_in.move(self.percentage(12, self.form_container.frameSize().width()) - 10, 380)

		self.register.resize(self.form_container.frameSize().width(), 40)
		self.register.move(0, 480)


		self.footer.resize(self.right_side.frameSize().width(), 400)