# -*- coding: utf-8 -*-
# -*- coding: euc-kr -*-

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class LineDetector:

    def __init__(self, topic):
        self.image_width = 640 # 이미지의 너비
        self.scan_width, self.scan_height = 200, 50 #20 # 각 차선 인식할 범위 (가로, 세로 크기)
        self.lmid, self.rmid = self.scan_width, self.image_width - self.scan_width # 왼쪽 및 오른쪽 차선 탐색의 끝 x좌표
        self.area_width, self.area_height = 10, 10 #10 # 차선 인식 박스의 크기 (가로, 세로)
        self.roi_vertical_pos = 300 # ROI영역의 시작 y 좌표 위치
        self.row_begin = (self.scan_height - self.area_height) // 2 # ROI에서 차선 인식 첫 row 위치
        self.row_end = self.row_begin + self.area_height # ROI에서 차선 인식 마지막 row 위치
        self.pixel_cnt_threshold = 0.2 * self.area_width * self.area_height # 차선 인식 박스에서 차선으로 인식할 픽셀의 개수 threadhold

        # Initialize various class-defined attributes, and then...
        self.cam_img = np.zeros(shape=(480, 640, 3), dtype=np.uint8)
        self.mask = np.zeros(shape=(self.scan_height, self.image_width),
                             dtype=np.uint8)
        self.edge = np.zeros(shape=(self.scan_height, self.image_width),
                             dtype=np.uint8)
        self.bridge = CvBridge()
        rospy.Subscriber(topic, Image, self.conv_image)

    def conv_image(self, data):
        self.cam_img = self.bridge.imgmsg_to_cv2(data, 'bgr8')
        v = self.roi_vertical_pos
        roi = self.cam_img[v:v + self.scan_height, :]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        avg_value = np.average(hsv[:, :, 2])
        value_threshold = avg_value + (255 - avg_value) * (40 / 100)
        lbound = np.array([0, 0, value_threshold], dtype=np.uint8)
        ubound = np.array([131, 255, 255], dtype=np.uint8)
        self.mask = cv2.inRange(hsv, lbound, ubound)

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        #blur = cv2.GaussianBlur(gray, (5, 5), 0)
        self.edge = cv2.Canny(gray, 30, 100)

        # Hough 변환 사용하여 선 검출
        linesimage = np.zeros((self.scan_height, self.image_width, 3), np.uint8)
        self.lineview = cv2.cvtColor(self.edge, cv2.COLOR_GRAY2BGR)
        lines = cv2.HoughLines(self.edge, 1, np.pi / 180, 55)
        try:
            for line in lines:
                for rho, theta in line:
                    if np.pi / 180 * 170 <= theta or theta <= np.pi / 180 * 10: # 너무 수직인 선 제거
                        continue
                    if np.pi / 180 * 80 <= theta <= np.pi / 180 * 100: # 너무 수평인 선 제거
                        continue
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * (a))
                    x2 = int(x0 - 1000 * (-b))
                    y2 = int(y0 -1000 * (a))

                    # 기울기 기준으로 차선 아닌 선 걸러내기
                    m = -a / b
                    ly = rho / b
                    ry = m * self.image_width + rho / b
                    bx = (rho - b * self.scan_height) / a
                    midx = self.image_width / 2
                    if bx < midx and m > 0:
                        continue
                    if bx > midx and m < 0:
                        continue
                    #print(rho, theta)
                    # 검출된 선 그리기
                    cv2.line(self.lineview, (x1,y1), (x2,y2), (0, 0, 255), 2)
                    cv2.line(linesimage, (x1, y1), (x2, y2), (255, 255, 255), 2)
        except:
            pass
        
        # 선 그려진 이미지 이진화
        lower_binary = np.array([127, 127, 127])
        upper_binary = np.array([255, 255, 255])
        self.linesimage_bin = cv2.inRange(linesimage,lower_binary,upper_binary)

    def detect_lines(self):
        # Return positions of left and right lines detected.
        left, right = -1, -1
    
        # 왼쪽 차선 검출
        for l in range(self.area_width, self.lmid):
            area = self.mask[self.row_begin:self.row_end, l - self.area_width:l] 
            if cv2.countNonZero(area) > self.pixel_cnt_threshold:
                lineare = self.linesimage_bin[self.row_begin:self.row_end, l - self.area_width:l]
                if cv2.countNonZero(lineare) > 10:
                    left = l
                    #break

        # 오른쪽 차선 검출
        for r in range(self.image_width - self.area_width, self.rmid, -1):
            area = self.mask[self.row_begin:self.row_end, r:r + self.area_width]
            if cv2.countNonZero(area) > self.pixel_cnt_threshold:
                lineare = self.linesimage_bin[self.row_begin:self.row_end, r:r + self.area_width]
                if cv2.countNonZero(lineare) > 10:
                    right = r
                    #break

        return left, right

    def show_images(self, left, right):
        # Display images for debugging purposes;
        # do not forget to call cv2.waitKey().
	#return
        
	while True:
		if cv2.waitKey(1) & 0xFF == 27:
			break
		
		self.cam_img = cv2.rectangle(self.cam_img, (0, self.roi_vertical_pos),
 			(self.image_width - 1, self.roi_vertical_pos + self.scan_height),
			(255, 0, 0), 3)

		if left != -1:
			lsquare = cv2.rectangle(self.cam_img,
		                        (left - self.area_width, self.roi_vertical_pos + self.row_begin),
		                        (left, self.roi_vertical_pos + self.row_end),
		                        (0, 255, 0), 3)
		else:
			print("Lost left line")

		if right != -1:
			rsquare = cv2.rectangle(self.cam_img,
		                        (right, self.roi_vertical_pos + self.row_begin),
		                        (right + self.area_width, self.roi_vertical_pos + self.row_end),
		                        (0, 255, 0), 3)
		else:
			print("Lost right line")




		cv2.imshow("frame", self.cam_img)
		cv2.imshow("mask", self.mask)
		cv2.imshow("edge", self.edge)
		#cv2.imshow("lineview", self.lineview)
		cv2.imshow("linesimage_bin", self.linesimage_bin)
		
        
        
        
        
        
        
