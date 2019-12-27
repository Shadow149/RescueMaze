def move_forward(*args, speed: float = 10.0) -> None:
    '''
    Moves robot forwards at a constant velocity.  
    
    Args:
        *args : Used for inputting robot wheels. 
        speed (float) : The arg is used for setting speed for both wheels.  
    '''
    args[0].setVelocity(speed)
    args[1].setVelocity(speed)
    
def set_wheels(leftWheelVelocity: float, rightWheelVelocity: float, *args) -> None:
    '''
    Moves robot using input velocities which will move each wheel accordingly.  
    NOTE: Wheel velocities must be less than max velocity set by robot (<10 by default)
    
    Args:
        leftWheelVelocity (int) : Used for inputting robot wheels. 
        rightWheelVelocity (int) : Used for inputting robot wheels. 
        *args : Used for inputting robot wheels. In the form leftWheel,rightWheel
    '''    
    args[0].setVelocity(leftWheelVelocity)
    args[1].setVelocity(rightWheelVelocity)
 
def action(robot, startTime: float, duration: float = 3.0, function = None, *args, **kwargs) -> bool:
    #TODO considor using a class so it can store startTime without the user having to.
    '''
    Will call an inputted function for the specified duration, assuming a start time the function was first called in inputted
    
    Args:
        robot: robot class being used
        startTime (float) : The time the function was FIRST CALLED, NOTE: Use Robot.getTime() as using Time.time() will not give an accurate simulation time.  
        duration (float) : Specify the duration to perform the action.
        function (func) : Function that will be called after the specified duration.
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


