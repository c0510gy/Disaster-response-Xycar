# -*- coding: utf-8 -*-
# -*- coding: euc-kr -*-

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class CamImage:

    def __init__(self, topic):
	self.cam_dat = None
        rospy.Subscriber(topic, Image, self.image_rev)

    def image_rev(self, data):
        self.cam_dat = data

    def getData(self):
        return self.cam_dat
		
        
        
        
        
        
        
