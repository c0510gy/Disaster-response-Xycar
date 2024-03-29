#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: euc-kr -*-

import rospy
import time

from motordriver import MotorDriver
#from imuread import ImuRead
from camimage import CamImage
from shortest_path import SPF

from std_msgs.msg import Int32MultiArray
from sensor_msgs.msg import Image

import numpy as np
import cv2

class AutoDrive:

    def __init__(self):
        self.image_width = 640 # 이미지의 너비
        rospy.init_node('xycar_driver')
        self.driver = MotorDriver('/xycar_motor_msg')

	self.cam_image = CamImage('/usb_cam/image_raw')
	self.pub = rospy.Publisher('/remote_rec', Image, queue_size=1)
	rospy.Subscriber('/remote_pub', Int32MultiArray, self.get_yolo_result)
	
	rospy.Subscriber('/xycar_ad_controller/controller_msg', Int32MultiArray, self.get_controller_msg)
	self.cont_pub = rospy.Publisher('/xycar_ad/controller_msg', Int32MultiArray, queue_size=1)

	self.yolo_dat = None
	
	self.x = 50
	self.y = 50
	self.dir = 0

	self.dx = self.x
	self.dy = self.y
	
	self.shortest_path = SPF(100, 100)


    def get_controller_msg(self, loc):
	self.dx = loc.data[0]
	self.dy = loc.data[1]
	
    def go_forward(self):
	self.driver.drive(90, 90 + 30)
	time.sleep(2)
	self.driver.drive(90, 90)

    def get_shortest_path(self):
	return self.shortest_path.get_path(self.x, self.y, self.dx, self.dy)

    def add_obstacle(self, x, y):
	self.shortest_path.set_obs(x, y)

    def get_yolo_result(self, data):
	print('recieved')
	self.yolo_dat = data.data
	if self.yolo_dat[0] == 1:
		print('detected!', self.yolo_dat[1:])
	else:
		print('not detected')
	#print(data.data)

    def publish_to_remote(self):
	#pub_info = [1, 1]
	#pub_info = Int32MultiArray(data=pub_info)
	dat = self.cam_image.getData()
	self.pub.publish(dat)

    def for_bck(self):
	for stop_cnt in range(2):
		self.driver.drive(90, 90)
		time.sleep(0.1)
		self.driver.drive(90, 70)
		time.sleep(0.1)

    def turn(self, ccw=False):
	angle = 50
	if ccw:
		angle *= -1
	self.driver.drive(90, 90 + 30)
	time.sleep(0.3)
	for i in range(5):
		self.turn_(angle)
		time.sleep(0.5)
	#self.bwd_stop()
	self.driver.drive(90, 90 - 20)
	print('back')
	time.sleep(0.5)
	self.bwd_stop()
	self.driver.drive(90, 90)

    def turn_(self, angle):
	self.driver.drive(90 + angle, 90 + 30)
	time.sleep(0.5)
	self.fwd_stop()
	time.sleep(0.5)
	self.for_bck()
	self.driver.drive(90 - angle, 90 - 25)
	time.sleep(0.5)
	self.bwd_stop()
	time.sleep(0.5)

    def fwd_stop(self):
	self.driver.drive(90, 40)
	time.sleep(0.1)
	self.driver.drive(90, 90)

    def bwd_stop(self):
	self.driver.drive(90, 140)
	time.sleep(0.1)
	self.driver.drive(90, 90)


if __name__ == '__main__':
    car = AutoDrive()
    time.sleep(10)
    rate = rospy.Rate(60)
    print('started')
    
    path, currentMap = car.get_shortest_path()
    car.cont_pub.publish(Int32MultiArray(data=currentMap))
    
    while not rospy.is_shutdown():
	while car.x == car.dx and car.y == car.dy:
		time.sleep(1)
	
	path, currentMap = car.get_shortest_path()
	car.cont_pub.publish(Int32MultiArray(data=currentMap))
	print(path)
	go_dir = 0
	next_p = [path[0][0], path[0][1]]
	
	# determine next direction
	if next_p[1] > car.y:
		go_dir = 0
	elif next_p[0] > car.x:
		go_dir = 1
	elif next_p[1] < car.y:
		go_dir = 2
	elif next_p[0] < car.x:
		go_dir = 3
	
	print(go_dir, car.dir)
	
	# turn operations to make the direction of xycar heads to next direction.
	if abs(go_dir - car.dir) == 1:
		if go_dir > car.dir:
			car.turn()
			car.dir += 1
			car.dir %= 4
		else:
			car.turn(True)
			car.dir -= 1
			car.dir = (car.dir + 4) % 4
	if car.dir == 0 and go_dir == 3:
		car.turn(True)
		car.dir = 3
	while go_dir != car.dir:
		car.dir += 1
		car.dir %= 4
		car.turn()

	# run stop sign recognition
        car.publish_to_remote()
	while car.yolo_dat is None:
		time.sleep(1)
	
	# go forward operation	
	if car.yolo_dat[0] == 1:
		car.add_obstacle(next_p[0], next_p[1])
	else:
		car.go_forward()
		car.x, car.y = next_p
		if car.x == car.dx and car.y == car.dy:
			print('arived')
			#break
	car.yolo_dat = None
	time.sleep(3)
    
    rospy.on_shutdown()
