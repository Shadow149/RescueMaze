from controller import Robot
import cv2
import numpy as np

def detectVisualSimple(image_data, camera):

	coords_list = []
	img = np.array(np.frombuffer(image_data, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4)))
	img[:,:,2] = np.zeros([img.shape[0], img.shape[1]])


	#convert from BGR to HSV color space
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	#apply threshold
	thresh = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)[1]

	# draw all contours in green and accepted ones in red
	contours, h = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	
	for c in contours:
		if cv2.contourArea(c) > 1000:
			coords = list(c[0][0])
			coords_list.append(coords)
			print("Victim at x="+str(coords[0])+" y="+str(coords[1]))

	return coords_list


robot = Robot()
timeStep = 32

camera = robot.getCamera("camera_centre")
camera.enable(timeStep)

while robot.step(timeStep) != -1:
	img = camera.getImage()
	detectVisualSimple(img, camera)
	
	