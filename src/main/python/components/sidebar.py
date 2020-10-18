import qtawesome as qta
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QColor
from core.functions import percentage

class Sidebar(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)

        kwargs['window'].screen_size_signal.connect(self.resize_event)
        self.state = kwargs['window'].state
        self.setAttribute(Qt.WA_StyledBackground, True) # this allow bg color in root widget
          
        self.render()
        if self.state['settings']['screen'] == 'fullScreen':  self.retranslateUI()

    def render(self):
        self.setObjectName('bg-dark')


    def resize_event(self):
        self.retranslateUI()

    def retranslateUI(self):
        sc = self.state['settings']
        self.resize(percentage(4, sc['width']), sc['height']) # this component always use 4% of parent width
        

