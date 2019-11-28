"""e-puck_go_forward controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
robot = Robot()

MAX_SPEED = 5.24

DELAY = 70


timestep = int(robot.getBasicTimeStep())
left_wheel = robot.getMotor('left wheel')
right_wheel = robot.getMotor('right wheel')

#left_wheel.setPosition(float('inf'))
#right_wheel.setPosition(float('inf'))    

left_wheel.setPosition(30)
right_wheel.setPosition(30) 

#left_wheel.setVelocity(1 * MAX_SPEED)
#right_wheel.setVelocity(1 * MAX_SPEED)

red_led = [robot.getLED("red led 1"), robot.getLED("red led 2"), robot.getLED("red led 3")]

delay = 0
led_number = 0
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
    
    delay += 1
    if (delay == DELAY):
      red_led[led_number].set(0)
      led_number += 1
      led_number = led_number % 3
      red_led[led_number].set(1)
      delay = 0
    pass

# Enter here exit cleanup code.
