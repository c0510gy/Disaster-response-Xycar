# -*- coding: utf-8 -*-
# -*- coding: euc-kr -*-

import rospy
from sensor_msgs.msg import Imu
from diagnostic_msgs.msg import DiagnosticArray

class ImuRead:

    def __init__(self, linear_topic, gyro_topic):
        self.ax = -1
        self.ay = -1
        self.az = -1
        rospy.Subscriber(linear_topic, Imu, self.read_linear_data)
        self.roll = -1
        self.pitch = -1
        self.yaw = -1
        rospy.Subscriber(gyro_topic, DiagnosticArray, self.read_gyro_data)

    def read_linear_data(self, data):
        status = data.linear_acceleration
        self.ax = status.x
        self.ay = status.y
        self.az = status.z

    def read_gyro_data(self, data):
        status = data.status[0].values
        self.roll = status[0].value
        self.pitch = status[1].value
        self.yaw = status[2].value

    def get_linear_data(self):
        return float(self.ax), float(self.ay), float(self.az)

    def get_gyro_data(self):
        return float(self.roll), float(self.pitch), float(self.yaw)

