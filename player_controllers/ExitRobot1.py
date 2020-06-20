from controller import Robot
import struct

robot = Robot()
timeStep = 32
emitter = robot.getEmitter('emitter')

while robot.step(timeStep) != -1:
    message = struct.pack('i i i c', 1, 0, 0, b'E')
    emitter.send(message)