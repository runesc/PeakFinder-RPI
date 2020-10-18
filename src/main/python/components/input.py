import qtawesome as qta
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QColor
from core.functions import percentage


class Input(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)