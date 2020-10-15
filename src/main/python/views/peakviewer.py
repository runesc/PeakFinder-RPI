import requests
import json
import random
import string
import qtawesome as qta
import pandas as pd
import core.modules.pyqtgraph as pg
from fpdf import FPDF
from datetime import datetime
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout, QVBoxLayout, QRadioButton, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QPropertyAnimation, QRect, QTimer
from PyQt5.QtGui import QPixmap, QColor
from core.modules.pyqtgraph import PlotWidget, plot

class PeakViewer(QWidget):
	"""
	docstring
	"""
	def __init__(self, parent=None, *args):
		super().__init__()
		self.setAttribute(Qt.WA_StyledBackground, True) # this allow bg color in root widget
		
		self.parent = parent
		self.state = parent.state

		# Event controllers
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

		# First chart
		self.peaks = '0'
		self.dp = '0s'
		self.desv = '0s'
		self.block = True

		# Second chart
		self.predict_peaks = '0'
		self.predict_precision = '0%'
		self.predict_error = '0s'

		self.render()

	def render(self):
		self.setObjectName('bg-dark-gradient')

		self.title = QLabel("Peak<span style='font-weight:300'>Viewer</span>", self)
		self.title.setObjectName('view_title')