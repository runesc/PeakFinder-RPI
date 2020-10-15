import sys
import json
import pyAesCrypt
import requests
import logging
import os
from pathlib import Path
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

from core.modules.firebase import Firebase
from core.functions import exists, percentage


# Importar componentes
from components.sidebar import Sidebar

# Importar vistas
from views.auth import SignIn, SignUp
from views.peakviewer import PeakViewer
from views.peakstreamer import PeakStreamer
from views.cloud import Cloud
from views.profile import Profile


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
			'appVersion': self.build_settings['version'],
			'currentView': 0,
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
		if exists(self.state['PATH']) and exists(self.state['PATH'] + 'config.json') and exists(self.state['PATH'] + 'session.json'): 

			with open(self.state['PATH'] + 'session.json', 'r') as user:
				user = eval(user.read()) # convert str to json

			try:
				token = self.state['firebaseAuth'].get_account_info(user['idToken'])
			except (requests.exceptions.HTTPError):
				logging.info('Sesion existe pero está expirada. Generando nueva sesion...')
				token = self.state['firebaseAuth'].refresh(user['refreshToken'])
			
			# Set config.json in state['settings']
			with open(self.state['PATH'] + 'config.json', 'r') as config_file:
				self.state.update({
					'userInfo': user,
					'screens': {
						'PeakViewer': PeakViewer,
						'PeakStreamer': PeakStreamer,
						'Cloud': Cloud,
						'Profile': Profile
					},
					'settings': eval(config_file.read()) # convert str from file to json
				})
		else:
			# Run this script if file sys check fails
			try:
				os.mkdir(self.state['PATH'])
			except FileExistsError as FileError:
				logging.warning(FileError)
			finally:
				with open(self.state['PATH'] + 'config.json', 'w+') as config_file:
					config_file.write(str({
						'screen': 'default',
						'width': 1336,
						'height': 768,
					}))
					config_file.close()
				
				self.state.update({ # Add SignIn and SignUp to list
					'screens': {
						'SignIn': SignIn,
						'SignUp': SignUp,
						'PeakViewer': PeakViewer,
						'PeakStreamer': PeakStreamer,
						'Cloud': Cloud,
						'Profile': Profile
					}
				})
			
		self.ComponentWillMount()
		self.render()
		self.ComponentDidMount()
		self.loadCSS()
			
	def ComponentWillMount(self):
		"""
			Este metodo se ejecuta antes del render y sirve para aplicar las configuraciones previas al render
		"""
		settings, app_title = self.state['settings'], self.build_settings['app_name']
		
		if settings['screen'] == 'fullScreen':
			self.showFullScreen()
		else:
			self.resize(settings['width'], settings['height'])
			self.setWindowTitle(app_title) # This solve OS X Title

	def render(self):
		"""
			Aqui se hace el render de las vistas que se van a mostrar en la app
		"""

		# Sidebar and app content
		self.sidebar = Sidebar(self)
		self.app_content = QStackedWidget(self)

		# Add a loop here	
		self.app_content.addWidget(PeakViewer(self))
	

	def ComponentDidMount(self):
		"""
			Añadir root (QStackedLayout object) al estado para interactuar con el y navegar entre pestañas
		"""
		self.state['root'] = self.app_content

	
	def resizeEvent(self, event):
		"""
			Al cambiar el tamaño de la ventana se actualiza el estado, se redimensiona la pantalla y se emite una señal 
			para las clases hijo.
		"""
		self.state['settings'].update({'width': self.width(), 'height': self.height()})
		self.retranslateUI()
		self.screen_size_signal.emit()

	
	def retranslateUI(self):
		"""
			Se instancia las configuracion de pantalla en "sc" y aqui se hacen los calculos para el diseño responsive
			y la alineación de los objetos
		"""
		sc = self.state['settings']
		
		self.app_content.resize(percentage(96, sc['width']), sc['height'])
		self.app_content.move(percentage(4, sc['width']), 0)

	
	def loadCSS(self):
		"""
			Cargar estilos CSS globales 
		"""
		css = self.get_resource('styles/app.css') 
		with open(css, "r") as styles:
			self.setStyleSheet(styles.read())
	

if __name__ == '__main__':
    appctxt = ApplicationContext()
    app = BootstrapApp()
    app.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
