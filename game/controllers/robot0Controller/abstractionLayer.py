def get_camera(robot, timeStep : int = 32) -> object:
    '''
    Get camera object/node, enable it and return to allow for use.
    Args:
        robot : robot class being used  
        timeStep (int) : time step being used for the robot simulation steps (if none specified, default is 32)
    '''
    camera = robot.getCamera('camera')
    
    camera.enable(timeStep)
    camera.recognitionEnable(timeStep)
    
    return camera

def get_wheels(robot) -> list:
    '''
    Gets wheel motors from input robot node
    
    Args:
        robot : robot class being used. Created with controller.Robot()
    '''
    wheels = []
    
    wheels.append(robot.getMotor('left wheel'))
    wheels.append(robot.getMotor('right wheel'))
    
    return wheels

def move_forward(robot, speed: float = 10.0) -> None:
    '''
    Moves robot forwards at a constant velocity.  
    NOTE: Wheel velocities must be less than or equal to the max (or greater than the negative max) velocity set by robot (10 by default)
    
    Args:
        robot : robot class being used. Created with controller.Robot()
        speed (float) : The arg is used for setting speed for both wheels.  
    '''
    wheels = get_wheels(robot)
    
    wheels[0].setPosition(float("inf"))
    wheels[1].setPosition(float("inf"))
    
    wheels[0].setVelocity(speed)
    wheels[1].setVelocity(speed)
    
def set_wheels(robot, leftWheelVelocity: float, rightWheelVelocity: float) -> None:
    '''
    Moves robot using input velocities which will move each wheel accordingly.  
    NOTE: Wheel velocities must be less than or equal to the max (or greater than the negative max) velocity set by robot (10 by default)
    
    Args:
        robot : robot class being used. Created with controller.Robot()
        leftWheelVelocity (int) : Used for inputting robot wheels. 
        rightWheelVelocity (int) : Used for inputting robot wheels. 
    '''    
    wheels = get_wheels(robot)
    
    wheels[0].setPosition(float("inf"))
    wheels[1].setPosition(float("inf"))
    
    wheels[0].setVelocity(leftWheelVelocity)
    wheels[1].setVelocity(rightWheelVelocity)
 
def action(robot, startTime: float, duration: float = 3.0, function = None, *args, **kwargs) -> bool:
    #TODO consider using a class so it can store startTime without the user having to.
    '''
    Will call an inputted function for the specified duration, assuming the start time was equated when the function was first called.    
    Args:
        robot : robot class being used. Created with controller.Robot()
        startTime (float) : The time the function was FIRST CALLED, NOTE: Use Robot.getTime() as using Time.time() will not give an accurate simulation time.  
        duration (float) : Specify the duration to perform the action.
        function (func) : Function that will be called during the specified duration.
        *args **kwargs : Arguments to pass into function that will be called 
    ''' 
    currentTime = robot.getTime()    
    timeElapsed = currentTime - startTime
    
    if timeElapsed > duration:
        #print("Finished")
        return True
    else:
        #print("Performing action...")
        if function != None:
            function(*args, **kwargs)
        return False
    
def get_distance_sensors(robot, timeStep : int = 32) -> list:
    #TODO will change with new robot
    '''Gets all the distance sensors to use in the rest of your code
    
    Args:
        robot : robot class being used  
        timeStep (int) : time step being used for the robot simulation steps (if none specified, default is 32)
    '''
    sensors = []
    for i in range(8):
        sensor = robot.getDistanceSensor('so'+str(i))
        sensors.append(sensor)
        sensors[i].enable(timeStep)
    
    return sensors


