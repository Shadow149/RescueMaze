"""supervisor controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor

import math

supervisor = Supervisor()

radius = 0.2

def are_colliding(object1, object2):
    p1 = object1.getSFVec3f()
    p2 = object2.getSFVec3f()
    dx = p2[0] - p1[0]
    dz = p2[2] - p1[2]
    return math.sqrt(dx ** 2 + dz ** 2) < 2.0 * radius

robot = supervisor.getFromDef('ROBOT')
robotTrans = robot.getField('translation')

display = supervisor.getDisplay("display")

human = supervisor.getFromDef('HUMAN')
transHuman = human.getField("translation")

freq = 0
humanLoaded = False
score = 0

collecting = False
collecting_start_time = 0

while supervisor.step(32) != -1:
    if freq == 10:
        translation = robotTrans.getSFVec3f()
        #print('position: %g %g %g\n' % (translation[0], translation[1], translation[2]))
        
           
        robot_vel = robot.getVelocity()
        robot_stopped = abs(robot_vel[0]) < 0.0001 and abs(robot_vel[1]) < 0.0001 and abs(robot_vel[2]) < 0.0001
        
        if (are_colliding(robotTrans,transHuman) and not humanLoaded and robot_stopped and not collecting):
            collecting_start_time = supervisor.getTime()
            collecting = True
            
        if are_colliding(robotTrans,transHuman) and not robot_stopped and collecting:
            print("Collection Canceled")
            collecting = False
            
        if collecting:
            print("Collecting...")
            current_time = supervisor.getTime()
            print(current_time - collecting_start_time)
            if current_time - collecting_start_time > 2:
                humanLoaded = True
                score += 100
                display.drawText("Score: " + str(score), 0,0)
            
        freq = 0
        
    if humanLoaded:
        robotPos = robotTrans.getSFVec3f()
        transHuman.setSFVec3f([robotPos[0],1,robotPos[2]]) # cannot currently delete an object during runtime, maybe there is??
        
        
    freq += 1