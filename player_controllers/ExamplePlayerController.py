'''
Sample code that can collect heated victims and detect visual victims.
Please note this code doesn't detect when the victim changes to collected so stays stopped forever after collecting a victim.
'''

from controller import Robot
import math
import struct
import cv2
import numpy as np

trap_colour = b'\n\n\n\xff'
swamp_colour = b'\x12\x1b \xff'
exit_colour = b'\x10\xb8\x10\xff'

timeStep = 32
max_velocity = 6.28

sensor_value = 0.07

messageSent = False

startTime = 0
duration = 0

robot = Robot()

wheel_left = robot.getMotor("left wheel motor")
wheel_right = robot.getMotor("right wheel motor")

camera = robot.getCamera("camera_left")
camera.enable(timeStep)

colour_camera = robot.getCamera("colour_sensor")
colour_camera.enable(timeStep)

emitter = robot.getEmitter("emitter")

gps = robot.getGPS("gps")
gps.enable(timeStep)

left_heat_sensor = robot.getLightSensor("left_heat_sensor")
right_heat_sensor = robot.getLightSensor("right_heat_sensor")

left_heat_sensor.enable(timeStep)
right_heat_sensor.enable(timeStep)

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

program_start = robot.getTime()

victim_detection_time = 0

def process(image_data, camera):
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
        coords = list(c[0][0])
        coords_list.append(coords)
        print("Victim at x="+str(coords[0])+" y="+str(coords[1]))
    
    return coords_list

def sendMessage(robot_type, v1, v2):
    message = struct.pack('i i c', robot_type, v1, v2)
    emitter.send(message)

def sendVictimMessage():
    global messageSent
    position = gps.getValues()

    if not messageSent:
        #robot type, position x cm, position z cm, victim type
        sendMessage(int(position[0] * 100), int(position[2] * 100), b'H')
        messageSent = True


def nearObject(position):
    return position < 0.05

def getVisibleVictims():
    victims= []
    img = camera.getImage()
    coords = process(img, camera)

    distance_to_wall = frontSensors[1].getValue()

    for coord in coords:
        victims.append([distance_to_wall,coord])

    return victims

def stopAtHeatedVictim():
    global messageSent
    print(left_heat_sensor.getValue(),right_heat_sensor.getValue())
    
    if left_heat_sensor.getValue() > 37 or right_heat_sensor.getValue() > 37:
        stop()
        sendVictimMessage()
    else:
        messageSent = False

def turnToVictim(victim):
    # [x,y]
    position_on_image = victim[1]

    width = camera.getWidth()
    center = width / 2

    victim_x_position = position_on_image[0]
    dx = center - victim_x_position

    if dx < 0:
        turn_right_to_victim()
    else:
        turn_left_to_victim()


def getClosestVictim(victims):
    shortestDistance = 999
    closestVictim = []

    for victim in victims:
        dist = victim[0]
        if dist < shortestDistance:
            shortestDistance = dist
            closestVictim = victim

    return closestVictim

def stopAtVictim():
    global messageSent
    #get all the victims the camera can see
    victims = getVisibleVictims()

    foundVictim = False

    if len(victims) != 0:
        closest_victim = getClosestVictim(victims)
        turnToVictim(closest_victim)

    #if we are near a victim, stop and send a message to the supervisor
    for victim in victims:
        if nearObject(victim[0]) and not foundVictim:
            stop()
            sendVictimMessage()
            foundVictim = True

    if not foundVictim:
        messageSent = False

def avoidTiles():
    global duration, startTime
    colour = colour_camera.getImage()

    if colour == trap_colour or colour == swamp_colour:
        move_backwards()
        startTime = robot.getTime()
        duration = 2

def turn_right_to_victim():
    #set left wheel speed
    speeds[0] = 1 * max_velocity
    #set right wheel speed
    speeds[1] = 0.8 * max_velocity

def turn_left_to_victim():
    #set left wheel speed
    speeds[0] = 0.8 * max_velocity
    #set right wheel speed
    speeds[1] = 1 * max_velocity

def move_backwards():
    #set left wheel speed
    speeds[0] = -0.5 * max_velocity
    #set right wheel speed
    speeds[1] = -0.7 * max_velocity

def stop():
    #set left wheel speed
    speeds[0] = 0
    #set right wheel speed
    speeds[1] = 0

def turn_right():
    #set left wheel speed
    speeds[0] = 0.6 * max_velocity
    #set right wheel speed
    speeds[1] = -0.2 * max_velocity

def turn_left():
    #set left wheel speed
    speeds[0] = -0.2 * max_velocity
    #set right wheel speed
    speeds[1] = 0.6 * max_velocity

def spin():
    #set left wheel speed
    speeds[0] = 0.6 * max_velocity
    #set right wheel speed
    speeds[1] = -0.6 * max_velocity

while robot.step(timeStep) != -1:
    if (robot.getTime() - startTime) < duration:
        pass
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
        
        #for both front sensors
        if frontSensors[0].getValue() < sensor_value and frontSensors[1].getValue() < sensor_value:
            spin()

        stopAtVictim()
        stopAtHeatedVictim()

        avoidTiles()

        if (robot.getTime() - program_start) > 20:
            if colour_camera.getImage() == exit_colour:
                sendMessage(0,0,0,b'E')

        wheel_left.setVelocity(speeds[0])
        wheel_right.setVelocity(speeds[1])
    
