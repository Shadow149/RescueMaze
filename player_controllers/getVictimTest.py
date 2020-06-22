"""

getVictimTest.py: Sample program to detect heat victims and try to score them by transmitting to MainSupervisor

by Victor Hu

"""

from controller import Robot
from controller import GPS
from controller import LightSensor
import struct

robot = Robot()
timeStep = 32

emitter = robot.getEmitter("emitter")
gps = robot.getGPS("gps")

# Heat sensors are mimiced as light sensors
leftHeatSensor = robot.getLightSensor("left_heat_sensor")
rightHeatSensor = robot.getLightSensor("right_heat_sensor")

gps.enable(timeStep)
leftHeatSensor.enable(timeStep)
rightHeatSensor.enable(timeStep)

while robot.step(timeStep) != -1:

	robotPos = gps.getValues()

	print("Left heat sensor temperature: " + str(leftHeatSensor.getValue()) + " Right heat sensor temperature: " + str(rightHeatSensor.getValue()))

	# Ambient temperature is ~20C-25C, Victim temperature is ~37C
	if leftHeatSensor.getValue() > 32 or rightHeatSensor.getValue() > 32:
		message = struct.pack('i i i c', 1, int(robotPos[0]*100), int(robotPos[2]*100), b'T')
		emitter.send(message)