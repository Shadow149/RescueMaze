'''
Updated version of the seminar code from day 2 to be used in release 6 and later.
'''
# Import all relevant libraries
from controller import Robot
import math
import struct


# Set RGB colours of the swamp and hole to avoid them
# These should be calibrated to match the environment
hole_colour = b';;@\xff'
swamp_colour = b'\x8e\xde\xf4\xff'


# Simulation time step and the maximum velocity of the robot
timeStep = 32
max_velocity = 6.28

# Threshold for detecting the wall
sensor_value = 0.05

# Threshold for the victim being close to the wall
victimProximity = 0.05

# Default setting for the "messageSent" variable
messageSent = False

# Variables related to timers and delays
startTime = 0
duration = 0
victimDetectedGlobal = False
victimTimer = 0

# Create a robot instance from the imported robot class
robot = Robot()

# Declare motors/wheels
wheel_left = robot.getMotor("left wheel motor")
wheel_right = robot.getMotor("right wheel motor")

# Declare cameras
camera = robot.getCamera("camera_centre")
camera.enable(timeStep)
camera.recognitionEnable(timeStep)

camerar = robot.getCamera("camera_right")
camerar.enable(timeStep)
camerar.recognitionEnable(timeStep)

cameral = robot.getCamera("camera_left")
cameral.enable(timeStep)
cameral.recognitionEnable(timeStep)

# Declare colour sensor underneith the robot
colour_camera = robot.getCamera("colour_sensor")
colour_camera.enable(timeStep)

# Declare communication link between the robot and the controller
emitter = robot.getEmitter("emitter")

# Declare GPS
gps = robot.getGPS("gps")
gps.enable(timeStep)

# Declare distance sensors around the robot
leftSensors = []
rightSensors = []
frontSensors = []

frontSensors.append(robot.getDistanceSensor("ps7"))
frontSensors[0].enable(timeStep)
frontSensors.append(robot.getDistanceSensor("ps0"))
frontSensors[1].enable(timeStep)

rightSensors.append(robot.getDistanceSensor("ps1"))
rightSensors[0].enable(timeStep)
rightSensors.append(robot.getDistanceSensor("ps2"))
rightSensors[1].enable(timeStep)

leftSensors.append(robot.getDistanceSensor("ps5"))
leftSensors[0].enable(timeStep)
leftSensors.append(robot.getDistanceSensor("ps6"))
leftSensors[1].enable(timeStep)

#        [left wheel speed, right wheel speed]
speeds = [max_velocity,max_velocity]

wheel_left.setPosition(float("inf"))
wheel_right.setPosition(float("inf"))

# Store when the program began
program_start = robot.getTime()


# Sends a message to the game controller
def sendMessage(v1, v2, victimType):
    message = struct.pack('i i c', v1, v2, victimType.encode())
    emitter.send(message)


# Sents a message of the game controller that a victim (of a certain type) has been detected
def sendVictimMessage(victimType='N'):
    global messageSent
    position = gps.getValues()

    if not messageSent:
        #robot type, position x cm, position z cm, victim type
        # The victim type is hardcoded as "H", but this should be changed to different victims for your program
        # Harmed = "H"
        # Stable = "S"
        # Unharmed = "U"
        # Heated (Temperature) = "T"
        sendMessage(int(position[0] * 100), int(position[2] * 100), victimType)
        messageSent = True


# return True/False if the robot is near an object. Change the
def nearObject(position):
    return math.sqrt((position[0] ** 2) + (position[2] ** 2)) < victimProximity


# Get visible victims using the raw camera input and a simple opencv function
def getVisibleVictims():
    #get all objects each camera can see

    victims = []
    cameras = [camera, cameral, camerar]

    for cam in cameras:
        objects = cam.getRecognitionObjects()

        for item in objects:
            if item.get_colors() == [1,1,1]:
                victim_pos = item.get_position()
                victims.append(victim_pos)

    return victims


# Stop at a victim once it is detected
def stopAtVisualVictim():
    global messageSent, victimDetectedGlobal
    #get all the victims the camera can see
    victims = getVisibleVictims()

    foundVictim = False

    #if we are near a victim, stop and send a message to the supervisor
    for victim in victims:
        if nearObject(victim) and not foundVictim and not victimDetectedGlobal:
            stop()
            sendVictimMessage('H') # <- Put detected victim type here
            print("Found visual victim!!")
            foundVictim = True

            victimDetectedGlobal = True

    if not foundVictim:
        messageSent = False


# Avoid holes and swamps by looking at the RBG colour of the camera
def avoidTiles():
    global duration, startTime
    colour = colour_camera.getImage()

    if colour == hole_colour or colour == swamp_colour:
        move_backwards()
        startTime = robot.getTime()
        duration = 2


# Setting the speed to steer right towards the victim
def turn_right_to_victim():
    #set left wheel speed
    speeds[0] = 1 * max_velocity
    #set right wheel speed
    speeds[1] = 0.8 * max_velocity

# Setting the speed to steer left towards the victim
def turn_left_to_victim():
    #set left wheel speed
    speeds[0] = 0.8 * max_velocity
    #set right wheel speed
    speeds[1] = 1 * max_velocity

# Setting the speed to move backwards
def move_backwards():
    #set left wheel speed
    speeds[0] = -0.5 * max_velocity
    #set right wheel speed
    speeds[1] = -0.7 * max_velocity

# Stop the robot
def stop():
    #set left wheel speed
    speeds[0] = 0
    #set right wheel speed
    speeds[1] = 0

# Steer the robot right
def turn_right():
    #set left wheel speed
    speeds[0] = 0.6 * max_velocity
    #set right wheel speed
    speeds[1] = -0.2 * max_velocity

# Steer the robot left
def turn_left():
    #set left wheel speed
    speeds[0] = -0.2 * max_velocity
    #set right wheel speed
    speeds[1] = 0.6 * max_velocity

# Spin the robot on its spot
def spin():
    #set left wheel speed
    speeds[0] = 0.6 * max_velocity
    #set right wheel speed
    speeds[1] = -0.6 * max_velocity



################################################################
###   Main loop starts here   ##################################
################################################################

while robot.step(timeStep) != -1:
    if (robot.getTime() - startTime) < duration:
        pass
    elif victimDetectedGlobal:

        if (robot.getTime() - victimTimer) > 3:
            print("Move away from victim")
            spin()
            wheel_left.setVelocity(speeds[0])
            wheel_right.setVelocity(speeds[1])

            startTime = robot.getTime()
            duration = 0.5
            victimDetectedGlobal = False
    else:
        startTime = 0
        duration = 0

        speeds[0] = max_velocity
        speeds[1] = max_velocity

        for i in range(2):
            #for sensors on the left, either
            if leftSensors[i].getValue() < sensor_value:
                turn_right()
            #for sensors on the right, either
            elif rightSensors[i].getValue() < sensor_value:
                turn_left()

        # See if the front distance sensors are seeing anything ahead of itself
        if frontSensors[0].getValue() < sensor_value and frontSensors[1].getValue() < sensor_value:
            spin()

        # Detect victims
        stopAtVisualVictim()

        if victimDetectedGlobal:
            stop()
            victimTimer = robot.getTime()


        # Avoid if any tiles are detected
        avoidTiles()

        # Set the velocities of the wheels
        wheel_left.setVelocity(speeds[0])
        wheel_right.setVelocity(speeds[1])
