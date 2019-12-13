#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: euc-kr -*-

import sys
import rospy
import time
from std_msgs.msg import Int32MultiArray

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QLineEdit
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5 import QtGui

class MapPainter(QWidget):
	
	def __init__(self, width, height, size, controller, parent=None):
		super(QWidget, self).__init__()
		self.controller = controller
		
		self.setGeometry(0, 0, 100, 100)
		
		self.w = width
		self.h = height
		self.size = size
		self.mapinfo = [[0 for _ in range(width)] for _ in range(height)]

	def setMapInfo(self, mapinfo):
		self.mapinfo = mapinfo
		self.update()
	
	def mousePressEvent(self, e):
		cursor = e.pos()
		x = cursor.x()
		y = cursor.y()
		gx = x // self.size
		gy = y // self.size
		print('clicked!', gx, gy)
		self.controller.sendLoc([gx, gy])
		
	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
		
		#painter.drawRect(100, 15, 400, 200)
		for y in range(self.h):
			for x in range(self.w):
				if self.mapinfo[y][x] == 0:
					painter.setBrush(QBrush(Qt.white))
				elif self.mapinfo[y][x] == 1:
					painter.setBrush(QBrush(Qt.green))
				elif self.mapinfo[y][x] == 2:
					painter.setBrush(QBrush(Qt.blue))
				elif self.mapinfo[y][x] == 3:
					painter.setBrush(QColor(255, 255, 0))
				elif self.mapinfo[y][x] == -1:
					painter.setBrush(QBrush(Qt.red))
				painter.drawRect(x * self.size, y * self.size, self.size, self.size)


class Controller(QWidget, QObject):
	
	update_signal = pyqtSignal()
	
	
	def __init__(self, parent=None):
		super(QWidget, self).__init__()
		
		#ROS
		
		rospy.init_node('xycar_ad_controller')
		rospy.Subscriber('/xycar_ad/controller_msg', Int32MultiArray, self.callback)
		self.pub = rospy.Publisher('/xycar_ad_controller/controller_msg', Int32MultiArray, queue_size=1)
		
		# PyQt
		self.setWindowTitle('Xycar AD Controller')
		self.currentMap = None
		
		self.edit = QTextEdit()
		self.showWidth = 20
		self.showHeight = 20
		self.showSize = 20
		self.mapPainter = MapPainter(self.showWidth, self.showHeight, self.showSize, self)
		
		grid = QGridLayout()
		#grid.addWidget(self.edit, 0, 0)
		grid.addWidget(self.mapPainter, 0, 0)
		
		self.setLayout(grid)

		self.show()
		self.edit.setText('started')
		print('PyQt started')
		self.resize((self.showWidth + 1) * self.showSize, (self.showHeight + 1) * self.showSize)
		self.update_signal.connect(self.updateText)

	def callback(self, dat):
		self.currentMap = dat.data
		self.update_signal.emit()
		#self.edit.setText('hello')
		#print(self.currentMap)
		#self.updateText(currentMap)

	def sendLoc(self, loc):
		loc = [loc[0] + self.w // 2 - self.showWidth // 2, loc[1] + self.h // 2 - self.showHeight // 2]
		print('loc:', loc)
		self.pub.publish(Int32MultiArray(data=loc))

	def updateText(self):
		if self.currentMap is None:
			return
		
		self.w, self.h = self.currentMap[:2]
		showMap = []
		
		m = ''
		for y in range(self.showHeight):
			r = []
			for x in range(self.showWidth):
				#if currentMap[y][x] == 
				px = self.w // 2 - self.showWidth // 2 + x
				py = self.h // 2 - self.showHeight // 2 + y
				m += str(self.currentMap[2 + py * self.w + px])
				r.append(self.currentMap[2 + py * self.w + px])
			showMap.append(r)
			m += '\n'
		self.edit.setText(m)
		self.mapPainter.setMapInfo(showMap)
	


app = QApplication(sys.argv)
cont = Controller()
sys.exit(app.exec_())
