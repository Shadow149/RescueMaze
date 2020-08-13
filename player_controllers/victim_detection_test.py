from controller import Robot
import cv2
import numpy as np
import os

def process(image_data, camera):
	img = np.array(np.frombuffer(image_data, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4)))
	img[:,:,2] = np.zeros([img.shape[0], img.shape[1]])


	#convert from BGR to HSV color space
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	#apply threshold
	thresh = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)[1]

	# draw all contours in green and accepted ones in red
	contours, h = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	for c in contours:
		coords = list(c[0][0])
		print("Victim at x="+str(coords[0])+" y="+str(coords[1]))


robot = Robot()
timeStep = 32

ps0 = robot.getDistanceSensor('ps0')
ps0.enable(timeStep)

left_camera = robot.getCamera("camera_left")
left_camera.enable(timeStep)

while robot.step(timeStep) != -1:
	img = left_camera.getImage()
	process(img, left_camera)
	
	