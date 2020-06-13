from abstractionLayer import *
from controller import Robot

myRobot = Robot()
robotMaxSpeed = 10

timeStep = 32

#get distance sensors
sensors = get_distance_sensors(myRobot, timeStep)
#get camera node
camera = get_camera(myRobot)

collecting = False
startTime = 99999999999

def collectingHuman(message: str):
    set_wheels(myRobot, 0, 0)
    print(message)

while myRobot.step(timeStep) != -1:
    
    objects = camera.getRecognitionObjects()
    
    if not collecting:
        if sensors[4].getValue() > 400 or sensors[5].getValue() > 400 :
            #left sensors
            set_wheels(myRobot, -0.5 * robotMaxSpeed, -1 * robotMaxSpeed)
        elif sensors[0].getValue() > 900 or sensors[1].getValue() > 900 or sensors[2].getValue() > 900 :
            #left sensors
            set_wheels(myRobot, 0.6 * robotMaxSpeed, -0.2 * robotMaxSpeed)
        elif sensors[5].getValue() > 900 or sensors[6].getValue() > 900 or sensors[7].getValue() > 900:
            #right sensors
            set_wheels(myRobot, -0.2 * robotMaxSpeed, 0.6 * robotMaxSpeed)
        else:
            #move forward
            move_forward(myRobot, robotMaxSpeed)   
            
        
        #for all found objects detected
        for item in objects:
            #if item is color of human
            if item.get_colors() == [0,0,0]:
                #get relative object position from robot
                position = item.get_position()
                
                #if objects within 0.5 meters
                if abs(position[0]) < 0.5 and abs(position[2]) < 0.5:
                    #get start time for action
                    startTime = myRobot.getTime()
                    collecting = True 
    
    else:
        if action(myRobot, startTime, 4, collectingHuman, "collecting..."):
            collecting = False
