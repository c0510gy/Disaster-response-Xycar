# -*- coding: utf-8 -*-
# -*- coding: euc-kr -*-

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit
from PyQt5.QtWidgets import QGridLayout

class Controller(QWidget):
	
	def __init__(self, parent=None):
		super(QWidget, self).__init__()
		
		self.edit = QLineEdit()
		
		grid = QGridLayout()
		grid.addWidget(self.edit, 0, 0)
		
		self.setLayout(grid)

		self.show()

	def setText(self, text):
		self.edit.setText(text)
	
app = QApplication(sys.argv)

sys.exit(app.exec_())
