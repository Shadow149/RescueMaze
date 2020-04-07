from controller import Robot
import struct


robot = Robot()
timeStep = 32

startTime = robot.getTime()

messagedSent = False

emitter = robot.getEmitter('emitter')

led = robot.getLED('led8')
led.set(True)

message = struct.pack('i i i c', 0, -30, -15, b'H')

while robot.step(32) != -1:
    currentTime = robot.getTime()

    if currentTime - startTime > 3 and not messagedSent:
        emitter.send(message)

        message = struct.pack('i i i c', 0, -60, 14, b'U')
        emitter.send(message)
        messagedSent = True

    if int(currentTime) % 2 == 0:
        led.set(True)
    else:
        led.set(False)
        