#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: euc-kr -*-

import rospy
import time
import cv2
from std_msgs.msg import Int32MultiArray
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import subprocess

#import yolo

class RemoteXycar(object):
	
	def __init__(self):
		self.yolo_path = '/home/ysg/xycar/src/xycar_ad_remote/src/'
		rospy.init_node('xycar_remote')
		self.pub = rospy.Publisher('/remote_pub', Int32MultiArray, queue_size=1)
		rospy.Subscriber('/remote_rec', Image, self.reciever)
		self.bridge = CvBridge()
		

	def send(self, data=None):
		pub_info = [1, 2, 3]
		pub_info = Int32MultiArray(data=pub_info)
		self.pub.publish(pub_info)
		
	def reciever(self, data):
		cam_img = self.bridge.imgmsg_to_cv2(data, 'bgr8')
		cv2.imwrite(self.yolo_path + 'tmp.jpg', cam_img)
		time.sleep(1)
		self.getDat()
		#print('recieved')

	def getDat(self):
		st = time.time()
		cmd = ['python3', self.yolo_path + 'yolo.py', '-i', './tmp.jpg']
		output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
		et = time.time()
		print('yolo finished:', et - st)
		output = eval(output)
		labels = dict()
		for i in output:
			labels[i[1]] = i[0]
		ret = False
		if 'stop sign' in labels:
			ret = True
			print('stop sign detected')
		
		pub_info = [int(ret)]
		if ret:
			pub_info += labels['stop sign']
		pub_info = Int32MultiArray(data=pub_info)
		self.pub.publish(pub_info)
		print(pub_info, 'sent')

if __name__ == '__main__':
	remoteXycar = RemoteXycar()
	time.sleep(3)
	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
		rate.sleep()
		#remoteXycar.send()
		#remoteXycar.getDat()
	
	rospy.on_shutdown()

