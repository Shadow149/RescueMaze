'''
This code allows for the colour sensor to be calibrated to match the swamp, hole, and checkpoint colour
'''
# Import all relevant libraries
from controller import Robot

# If you would like to view the HSV decomposition. Requires opencv installation
viewHSV = False
try:
    import numpy as np
    import cv2
    viewHSV = True
    print("Calibration of HSV decomposition of the colour camera is enabled")
except:
    print("[WARNING] Since OpenCV and numpy is not installed, the visual victim detection is turned off. \
        Run 'pip install opencv-python' to install OpenCV and 'pip install numpy' on your terminal/command line.\
        If you have python2, try 'pip3 install' rather than 'pip install'. ")

timeStep = 32
startTime = 0
duration = 0

# Create a robot instance from the imported robot class
robot = Robot()

# Declare colour sensor underneith the robot
colour_camera = robot.getCamera("colour_sensor")
colour_camera.enable(timeStep)


# Avoid holes and swamps by looking at the RBG colour of the camera
def viewColour():
    colour = colour_camera.getImage()

    print("Binary colour : ", colour)

    if viewHSV: 
        img = np.array(np.frombuffer(colour, np.uint8).reshape((colour_camera.getHeight(), colour_camera.getWidth(), 4)))
        img[:,:,2] = np.zeros([img.shape[0], img.shape[1]])
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)[0][0]
        print("HSV : ", hsv)

################################################################
###   Main loop starts here   ##################################
################################################################

while robot.step(timeStep) != -1:
    if (robot.getTime() - startTime) < duration:
        pass
    else:
        startTime = 0
        duration = 0

        # Avoid if any tiles are detected
        viewColour()