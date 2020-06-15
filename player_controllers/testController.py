from controller import Robot
import struct


robot = Robot()
timeStep = 32

startTime = robot.getTime()

messagedSent = False

emitter = robot.getEmitter('emitter')

cam = robot.getCamera('camera')
cam.enable(32)
cam.recognitionEnable(32)
cam1 = robot.getCamera('colour_sensor')
cam1.enable(32)

led = robot.getLED('led8')
led.set(True)

wheelLeft = robot.getMotor("left wheel motor")
wheelRight = robot.getMotor("right wheel motor")


while robot.step(32) != -1:
    currentTime = robot.getTime()
    #wheelLeft.setPosition(999)
    #wheelRight.setPosition(999)
    cam.getRecognitionObjects()

    if cam1.getImage() != b'\n\n\n\xff' :
        wheelLeft.setVelocity(6.28)
        wheelRight.setVelocity(6.28)
    else:
        wheelLeft.setVelocity(0)
        wheelRight.setVelocity(0)

    message = struct.pack('i i i c', 0, -30, -15, b'H')
    emitter.send(message)

    message = struct.pack('i i i c', 0, 27, -37, b'H')
    emitter.send(message)

    message = struct.pack('i i i c', 0, -60, 14, b'S')
    emitter.send(message)

    message = struct.pack('i i i c', 0, -100, -30, b'S')
    emitter.send(message)

    #message = struct.pack('i i i c', 1, 0, 0, b'E')
    #emitter.send(message)

    if int(currentTime) % 2 == 0:
        led.set(True)
    else:
        led.set(False)
        