"""e-puck_go_forward controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getMotor('motorname')
#  ds = robot.getDistanceSensor('dsname')
#  ds.enable(timestep)
MAX_SPEED = 6.28

robot.batterySensorEnable(100)

# get a handler to the motors and set target position to infinity (speed control)
leftMotor = robot.getMotor('left wheel motor')
rightMotor = robot.getMotor('right wheel motor')
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

# set up the motor speeds at 10% of the MAX_SPEED.
leftMotor.setVelocity(1 * MAX_SPEED)
rightMotor.setVelocity(1 * MAX_SPEED)


ps0 = robot.getDistanceSensor("ps0")
ps0.enable(timestep)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    """if ps0.getValue() > 50:
        leftMotor.setVelocity(0.1 * MAX_SPEED)
        rightMotor.setVelocity(0.01 * MAX_SPEED)
    else:
        leftMotor.setVelocity(0.1 * MAX_SPEED)
        rightMotor.setVelocity(0.1 * MAX_SPEED)"""

    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    
    pass

# Enter here exit cleanup code.
