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

front_ss = robot.getDistanceSensor('so4')
front_ss.enable(timestep)

leftSensors = []

for i in range(3):
    sensor = robot.getDistanceSensor('so'+str(i))
    leftSensors.append(sensor)
    leftSensors[i].enable(timestep)

rightSensors = []

for i in range(3):
    sensor = robot.getDistanceSensor('so'+str(5+i))
    rightSensors.append(sensor)
    rightSensors[i].enable(timestep)

camera = robot.getCamera('camera')
camera.enable(timestep)
camera.recognitionEnable(timestep)

width = camera.getWidth()

left_wheel.setPosition(999)
right_wheel.setPosition(999) 

red_led = [robot.getLED("red led 1"), robot.getLED("red led 2"), robot.getLED("red led 3")]

delay = 0
led_number = 0
humanLoaded = False
collecting = False
# Main loop:
# - perform simulation steps until Webots is stopping the controller
human_pos = [999,999,999]
human_image_pos = [999,999,999]
deposit_pos = [999,999,999]
deposit_image_pos = [999,999,999]

while robot.step(timestep) != -1:
    depositFound = False
    humanFound = False
    try:
        objects = camera.getRecognitionObjects()
        
        for item in objects:
            if item.get_colors() == [0.3,0,1]:
                depositFound = True
                deposit_pos = item.get_position()
                deposit_image_pos = item.get_position_on_image()
                break

        for item in objects:
            if item.get_colors() == [0,0,0]:
                humanFound = True
                human_pos = item.get_position()
                human_image_pos = item.get_position_on_image()
                break
                
        #print(human_image_pos[0],width/2)
        
        #print(camera.getRecognitionObjects()[0].get_position_on_image())
        if not depositFound:
            deposit_pos = [999,999,999]
            deposit_image_pos = [999,999,999]
        if not humanFound:
            human_pos = [999,999,999]
            human_image_pos = [999,999,999]
    except:
        pass
    
    if humanLoaded and not collecting:
        if abs(deposit_pos[0]) < 0.5 and abs(deposit_pos[1]) < 0.5 and abs(deposit_pos[2]) < 0.5:
            humanLoaded = False
            print("deposited")
            left_wheel.setVelocity(0 * MAX_SPEED)
            right_wheel.setVelocity(0 * MAX_SPEED)

    
    if (abs(human_pos[0]) < 0.5 and abs(human_pos[1]) < 0.5 and abs(human_pos[2]) < 0.5 and not humanLoaded and not collecting):
        collecting_start_time = robot.getTime()
        print("collected")
        #collecting = True
        humanLoaded = True
        
    if collecting:
        current_time = robot.getTime()
        #if current_time - collecting_start_time < 3:
        #    #print("stopping")
        #    left_wheel.setVelocity(0 * MAX_SPEED)
        #    right_wheel.setVelocity(0 * MAX_SPEED)   
        #else:
        #    collecting = False
        #    humanLoaded = True
    else:
        left_wheel.setVelocity(1 * MAX_SPEED)
        right_wheel.setVelocity(1 * MAX_SPEED)        
        
        if not humanLoaded and human_image_pos[0] != 999:
            if human_image_pos[0] > width / 2:
                left_wheel.setVelocity(1 * MAX_SPEED)
                right_wheel.setVelocity(0.8 * MAX_SPEED)
            else:
                left_wheel.setVelocity(0.8 * MAX_SPEED)
                right_wheel.setVelocity(1 * MAX_SPEED)
                
        elif humanLoaded and deposit_image_pos[0] != 999:
            if deposit_image_pos[0] > width / 2:
                left_wheel.setVelocity(1 * MAX_SPEED)
                right_wheel.setVelocity(0.8 * MAX_SPEED)
            else:
                left_wheel.setVelocity(0.8 * MAX_SPEED)
                right_wheel.setVelocity(1 * MAX_SPEED)
        
        if front_ss.getValue() > 900 and not collecting:
            left_wheel.setVelocity(0 * MAX_SPEED)
            right_wheel.setVelocity(1 * MAX_SPEED)
        else:    
            for i in range(3):
                #print(1 - ((2-i) / 5))
                if leftSensors[i].getValue() > 900:
                    left_wheel.setVelocity((1 - (i / 6)) * MAX_SPEED)
                    right_wheel.setVelocity(0 * MAX_SPEED)  
                if rightSensors[2-i].getValue() > 900:
                    left_wheel.setVelocity(0 * MAX_SPEED)
                    right_wheel.setVelocity((1 - ((2-i) / 6)) * MAX_SPEED)
    
# Enter here exit cleanup code.
