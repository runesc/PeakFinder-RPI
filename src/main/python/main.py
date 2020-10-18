import sys
import json
import pyAesCrypt
import requests
import logging
import os
from pathlib import Path
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget
from PyQt5.QtCore import Qt, pyqtSignal

from core.modules.firebase import Firebase
from core.functions import exists, percentage


# Importar componentes
from components.sidebar import Sidebar

# Importar vistas
from views.auth import SignIn, SignUp
from views.peakviewer import PeakViewer
#from views.peakstreamer import PeakStreamer
#from views.cloud import Cloud
#from views.profile import Profile


class BootstrapApp(QMainWindow, Firebase, ApplicationContext):
	screen_size_signal = pyqtSignal()
	state_updated = pyqtSignal(object)

	def __init__(self):
		"""
			Comprobar si existe la carpeta PeakFinder y los archivos config.json y private.json, si existen 
			entonces leer session.json y intentar obtener información del usuario para saber si el token ha 
			expirado o no, si expiro entonces se utiliza la funcion refresh para refrescar el token del usuario, 
			por ultimo se actualiza el estado (userInfo, screens) "userInfo" contiene la informacion del usuario 
			y "screens" las pantallas que se deberán renderizar dinamicamente.

			De lo contrario sino existe la carpeta entonces generar una nueva y escribir sobre ella 
			el archivo config.json para guardar las configuraciones de la app, session.json lo escribe
			la vista "auth.py".
		
		"""
		super().__init__()
		self.state = {
			'PATH': str(Path.home()) + '/PeakFinder/',
			'SESSION': str(Path.home()) + '/PeakFinder/session.json',
			'CONFIG': str(Path.home()) + '/PeakFinder/config.json',
			'APPCTX': ApplicationContext(),
			'appVersion': self.build_settings['version'],
			'debug': False,
			'userInfo': {},
			'settings': {},
			'screens': {},
			'firebaseAuth': self.Auth(),
			'firebaseDB': self.Database(),
			'firebaseStorage': self.Storage()
		}

		# Enable debug mode
		if self.state['debug']: 
			logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')

		# Check File system
		if exists(self.state['PATH']) and exists(self.state['CONFIG']) and exists(self.state['SESSION']): 

			with open(self.state['SESSION'], 'r') as user:
				user = eval(user.read()) # convert str to json
				
			try:
				# Si la sesion está dentro de la primera hora entonces
				token = self.state['firebaseAuth'].get_account_info(user['idToken'])
				self.setSession()
			except (requests.exceptions.HTTPError, KeyError) as e:
				# If file is corrupt ignore, else refresh session and save in state
				if type(e) != KeyError:
					logging.info('Sesion existe pero está expirada. Generando nueva sesion...')
					token = self.state['firebaseAuth'].refresh(user['refreshToken'])
					self.setSession()
				else:
					logging.error('Sesión currupta, se requiere generar una nueva.')
		else:
			# Run this if config data folder not exists
			try:
				os.mkdir(self.state['PATH'])
			except FileExistsError as FileError:
				logging.warning(FileError)
			finally:
				logging.error('config.json no existe. Reparando...')
				# Try to fix config.json
				if not exists(self.state['CONFIG']):
					with open(self.state['CONFIG'], 'w+') as config_file:
						config_file.write(str({
							'screen': 'default',
							'width': 1336,
							'height': 768,
						}))
						config_file.close()
		# add settings to state
		with open(self.state['CONFIG'], 'r') as app_conf:
			self.state.update({'settings': eval(app_conf.read())})
			app_conf.close()
		
		
		# Continue Life Cycle
		self.ComponentWillMount()
		self.render()
		if self.state['settings']['screen'] == 'fullScreen': self.retranslateUI()
		self.ComponentDidMount()
		self.loadCSS()

	
	def ComponentWillMount(self):
		"""
			Este metodo se ejecuta antes del render y sirve para aplicar las configuraciones previas al render
		"""
		settings, app_title, user_info = self.state['settings'], self.build_settings['app_name'], self.state['userInfo']
		self.setMinimumSize(800, 600) # Adjust window size
		if settings['screen'] == 'fullScreen':
			self.showFullScreen()
		else:
			self.resize(settings['width'], settings['height'])
			self.setWindowTitle(app_title) # This solve OS X Title

		# Add screens
		if bool(user_info):
			self.state.update({
				'screens': {
					#'PeakViewer': PeakViewer,
					#'PeakStreamer': PeakStreamer,
					#'Cloud': Cloud,
					#'Profile': Profile
			}})
		else:
			self.state.update({
				'screens': {
					#'SignIn': SignIn,
					#'SignUp': SignUp,
					#'PeakViewer': PeakViewer,
					#'PeakStreamer': PeakStreamer,
					#'Cloud': Cloud,
					#'Profile': Profile
			}})


	def render(self):
		self.display = QWidget(self)
		self.sidebar = Sidebar(self.display, window=self)

		self.screen_manager = QStackedWidget(self.display)
		
		# Add loop here
		self.screen_manager.addWidget(SignIn(self))

		self.setCentralWidget(self.display)
	
	
	def ComponentDidMount(self):
		"""
			Añadir root (QStackedLayout object) al estado para interactuar con el y navegar entre pestañas
		"""
		self.state['root'] = self.screen_manager

	
	def resizeEvent(self, event):
		"""
			Al cambiar el tamaño de la ventana se actualiza el estado, se redimensiona la pantalla y se emite una señal 
			para las clases hijo.
		"""
		self.state['settings'].update({'width': self.width(), 'height': self.height()})
		self.retranslateUI()
		self.screen_size_signal.emit()


	def loadCSS(self):
		"""
			Cargar estilos CSS globales 
		"""
		css = self.get_resource('styles/app.css') 
		with open(css, "r") as styles:
			self.setStyleSheet(styles.read())

	
	def retranslateUI(self):
		"""
			Se instancia las configuracion de pantalla en "sc" y aqui se hacen los calculos para el diseño responsive
			y la alineación de los objetos
		"""
		sc, user_info = self.state['settings'], self.state['userInfo']
		try:
			self.display.resize(sc['width'], sc['height'])
			
			# Show and hide sidebar depends on user login status
			if bool(user_info):
				self.screen_manager.resize(percentage(96, sc['width']) + 1 , sc['height'])
				self.screen_manager.move(percentage(4, sc['width']), 0)
			else:
				self.sidebar.hide()
				self.screen_manager.resize(sc['width'], sc['height'])

		except AttributeError as e: pass
		
	
	def setSession(self):
		"""
			Esta funcion agrega el contenido de session.json al estado de la app
		"""
		with open(self.state['SESSION'], 'r') as session:
			self.state.update({'userInfo': eval(session.read())})
			session.close()


if __name__ == '__main__':
    appctxt = ApplicationContext()
    app = BootstrapApp()
    app.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
