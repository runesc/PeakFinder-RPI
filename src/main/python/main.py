import sys
import os
import json
import pyAesCrypt
import requests
import logging
from pathlib import Path
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget
from PyQt5.QtCore import Qt, pyqtSignal

from core.modules.firebase import Firebase

# Importar vistas
from views.auth import SignIn, SignUp
from views.Home import Home
from views.peakviewer import PeakViewer
from views.peakstreamer import PeakStreamer
from views.cloud import Cloud
from views.profile import Profile

class Main(QMainWindow, Firebase):
	window_size = pyqtSignal()

	def __init__(self):
		super(Main,self).__init__()
		self.largo, self.alto = 1300, 700

		file = str(Path.home()) + '/PeakFinder/private.json'
		path = str(Path.home()) + '/PeakFinder/'

		self.auth = self.Auth()

		self.current_view = 3

		# Si existe la carpeta intentar acceder al archivo si no existe entonces crear carpeta y ir a signIn
		if os.path.isdir(path):
			
			if os.path.exists(file):
				
				with open(file, 'r') as user:
					user = user.read()

				# Convertir string a dict
				user = eval(user)

				try:
					token = self.auth.get_account_info(user['idToken'])
					self.user_info = user
					self.current_view = 2
				except requests.exceptions.HTTPError as status:
					logging.basicConfig(filename='logging.txt',level=logging.DEBUG)
					logging.debug(status)
					token = self.auth.refresh(user['refreshToken'])
					self.user_info = user
					self.current_view = 2
				
		else:
			try:
				os.mkdir(str(Path.home()) + '/PeakFinder/')
			except FileExistsError: pass
			

		self.loadUI()


	def loadUI(self):
		"""
			Aumentar tamaño de la ventana, crear la capa 1 y 2. Nota: La CAPA 2 es un QStackedWidget
		"""
		self.setWindowFlags(Qt.CustomizeWindowHint)
		self.resize(self.largo, self.alto)
		self.widget = QWidget()
		self.widget.resize(self.largo, self.alto)
		self.setCentralWidget(self.widget)
		self.container = QStackedWidget(self.widget)
		self.container.resize(self.largo, self.alto)

		"""
			Por cada vista encontrada en la lista se debe 
			cargar en el container y en las vistas se deben enviar las propiedades y metodos del parent
		"""
		for vista in [SignIn, SignUp, Home, PeakViewer, PeakStreamer, Cloud, Profile]:
			self.container.addWidget(vista(self)) 

		self.container.setCurrentIndex(self.current_view)
		

	""" 
		Cuando la ventana cambia su tamaño guarda las nuevas resoluciones 
		en sus variables y refresca el tamaño de las capas y emite esos cambios
		a las vistas.
	"""
	def resizeEvent(self, event):
		self.largo = self.frameSize().width()
		self.alto = self.frameSize().height()
		self.widget.resize(self.largo, self.alto)
		self.container.resize(self.largo, self.alto)
		self.window_size.emit()




if __name__ == "__main__":
    appctxt = ApplicationContext()
    window = Main()
    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
