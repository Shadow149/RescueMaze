from controller import Robot
import time
import math

"""
Example erebus robot controller
Written by Alfred Roberts - 2020
"""

#RobotName:Aura

MOVE_FORWARD = "MOVE_FORWARD"
MOVE_BACKWARDS = "MOVE_BACKWARDS"
TURN_LEFT = "TURN_LEFT"
TURN_RIGHT = "TURN_RIGHT"
TURN_LEFT_OBJECT = "TURN_LEFT_OBJECT"
TURN_RIGHT_OBJECT = "TURN_RIGHT_OBJECT"
STOP = "STOP"

class Player (Robot):


    def boundSpeed(self, speed):
        return max(-self.maxSpeed, min(self.maxSpeed, speed))

    def __init__(self):
        super(Player, self).__init__()
        
        #set constants
        self.timeStep = 32
        self.maxSpeed = 10.0
        
        self.mode = MOVE_FORWARD
        self.wheels = []
        self.distanceSensors = []
        self.leftSensors = []
        self.rightSensors = []
        self.frontSensors = []
        
        self.speeds = [0.0,0.0]
        
        self.humanLoaded = False
        self.collecting = False
        self.depositing = False
        self.timerStartTime = 0
        
        #config camera
        self.camera = self.getCamera('camera')
        self.camera.enable(self.timeStep)
        self.camera.recognitionEnable(self.timeStep)
        
        #config wheels
        self.wheels.append(self.getMotor("left wheel"))
        self.wheels.append(self.getMotor("right wheel"))
        
        #move forever
        self.wheels[0].setPosition(float("inf"))
        self.wheels[1].setPosition(float("inf"))
        
        #config sensors
        
        self.frontSensors.append(self.getDistanceSensor('so3'))
        self.frontSensors[0].enable(self.timeStep)
        
        self.frontSensors.append(self.getDistanceSensor('so4'))
        self.frontSensors[1].enable(self.timeStep)

        for i in range(3):
            sensor = self.getDistanceSensor('so'+str(i))
            self.leftSensors.append(sensor)
            self.leftSensors[i].enable(self.timeStep)


        for i in range(3):
            sensor = self.getDistanceSensor('so'+str(5+i))
            self.rightSensors.append(sensor)
            self.rightSensors[i].enable(self.timeStep)
        
        #idk
        self.wheels[0].setVelocity(0.0)
        self.wheels[1].setVelocity(0.0)
    
    def getDetectedObjects(self) -> list:
        '''Get detected objects from camera'''
        objects = self.camera.getRecognitionObjects()
        return objects
    
    def getBaseObjects(self) -> list:
        '''Get base objects from detected objects'''
        #get objects
        objects = self.getDetectedObjects()
        
        bases = []
        
        #for all objects in detected objects
        for item in objects:
            #if its the colour of the base recongition colour
            if item.get_colors() == [0.3,0,1]:
                #get its position relative to robot
                deposit_pos = item.get_position()
                #get its position in the image
                deposit_image_pos = item.get_position_on_image()
                #append to array as [relative [x,y,z] position, position on camera view]
                bases.append([deposit_pos,deposit_image_pos])
        
        return bases
    
    def getHumanObjects(self) -> list:
        '''Get human objects from detected objects'''
        objects = self.getDetectedObjects()
        
        humans = []
        
        #for all objects in detected objects
        for item in objects:
            #if its the colour of the human recongition colour
            if item.get_colors() == [0,0,0]:
                #get its position relative to robot
                human_pos = item.get_position()
                #get its position in the image
                human_image_pos = item.get_position_on_image()
                #append to array as [relative [x,y,z] position, position on camera view]
                humans.append([human_pos,human_image_pos])
        
        return humans
    
    def getWallObjects(self) -> list:
        '''Get human objects from detected objects'''
        objects = self.getDetectedObjects()
        
        walls = []
        
        #for all objects in detected objects
        for item in objects:
            #if its the colour of the wall recongition colour
            if item.get_colors() == [0.325,0.325,0.325]:
                #get its position relative to robot
                wall_pos = item.get_position()
                #get its position in the image
                wall_image_pos = item.get_position_on_image()
                #get its size in the image in pixels
                wall_image_size = item.get_size_on_image()
                #append to array as [relative [x,y,z] position, position on camera view, size on camera]
                walls.append([wall_pos,wall_image_pos, wall_image_size])
        
        return walls

    def nearObject(self, objPos: list) -> bool:
        '''Return true if relative object is < 0.5 metres away'''
        #TODO make 0.5 a constant that can change
        return abs(objPos[0]) < 0.5 and abs(objPos[2]) < 0.5
    
    def findClosestObject(self, objects: list) -> int:
        '''Find closest detected object using relative object position values'''
        minDist = 999
        closestObjectIndex = 999
        
        for i, obj in enumerate(objects):
            objectPos = obj[0]
            dist = math.sqrt(abs(objectPos[0]) + abs(objectPos[1]))
            if dist < minDist:
                minDist = dist
                closestObjectIndex = i
        
        return closestObjectIndex
    
    def moveToHuman(self) -> None:
        '''Get movement mode to move robot towards human using human position on image'''
        
        #Get human objects
        humans = self.getHumanObjects()
        #Get camera width
        width = self.camera.getWidth()
        
        center = width / 2
        
        if len(humans) > 0:
            #Find closest human as an index
            closestHumanIndex = self.findClosestObject(humans)
            #Get human position in image
            humanImagePos = humans[closestHumanIndex][1][0]
            
            #Find the difference in x values between centre of camera and human image position
            dx = center - humanImagePos
            
            if dx < 0:
                # Human on the right
                self.mode = TURN_RIGHT_OBJECT
            else:
                # Human on the left
                self.mode = TURN_LEFT_OBJECT
                
    def moveToBase(self) -> None:
        #Get base objects
        base = self.getBaseObjects()
        #Get camera width
        width = self.camera.getWidth()
        
        center = width / 2
        
        if len(base) > 0:
            #Find closest base as an index
            closestBaseIndex = self.findClosestObject(base)
            #Get base position in image
            baseImagePos = base[closestBaseIndex][1][0]
            
            #Find the difference in x values between centre of camera and base image position
            dx = center - baseImagePos
            
            if dx < 0:
                # Base on the right
                self.mode = TURN_RIGHT_OBJECT
            else:
                # Base on the left
                self.mode = TURN_LEFT_OBJECT
                    
    def moveToDoorWay(self) -> None:
        '''Get movement mode to move robot towards human using human position on image'''
        
        #Get human objects
        walls = self.getWallObjects()
        #Get camera width
        width = self.camera.getWidth()
        
        center = width / 2
        
        if len(walls) > 1:
            
            wall1 = max(walls, key=lambda item: item[2])
            walls.remove(wall1)
            wall2 = max(walls, key=lambda item: item[2])
            
            print(wall1)
            print(wall2)

            doorWayCenter = (wall1[1][0] + wall2[1][0]) / 2
            
            #Find the difference in x values between centre of camera and human image position
            dx = center - doorWayCenter
            
            if dx < 0:
                # Human on the right
                self.mode = TURN_RIGHT_OBJECT
            else:
                # Human on the left
                self.mode = TURN_LEFT_OBJECT
    
    def update(self):
        '''Update robot movement mode'''
        
        #Set mode to forward incase nothing else passes in the function
        self.mode = MOVE_FORWARD

        self.moveToDoorWay()
        
        #If a human is loaded and not collecting or depositing
        if self.humanLoaded and not self.collecting and not self.depositing:
            #Move to base
            self.moveToBase()
            
        #for all sensors (greater value means obstical is closer)
        for i in range(3):
            #For sensors of the left
            if self.leftSensors[i].getValue() > 900:
                self.mode = TURN_RIGHT
            #For sensors of the right
            elif self.rightSensors[2-i].getValue() > 900:
                self.mode = TURN_LEFT
                
        for i in range(2):
            #For front two sensors
            if self.frontSensors[i].getValue() > 900:
                self.mode = MOVE_BACKWARDS
        
        #If no human is loaded and not collecting or depositing
        if not self.humanLoaded and not self.collecting and not self.depositing:
            #Move to human
            self.moveToHuman()
        
        
        
        #Get base and human objects
        bases = self.getBaseObjects()
        humans = self.getHumanObjects()
                
        
        #For all bases detected by camera
        for base in bases:
            #If near base and human loaded and not already depositing
            if self.nearObject(base[0]) and self.humanLoaded and not self.depositing:
                self.mode = STOP
                self.depositing = True
                #Get start time for deposit so it can be used for calculating how long its been depositing for.
                self.timerStartTime = self.getTime()
                break
        
        #For all humans detected by camera
        for human in humans:
            #If near human and human is not loaded and not already collecting
            if self.nearObject(human[0]) and not self.humanLoaded and not self.collecting:
                self.collecting = True
                self.mode = STOP
                self.humanLoaded = True
                #Get start time for picking up human so it can used for calculating how long its been picking up for.
                self.timerStartTime = self.getTime()
                break
            
        if self.depositing:
            self.mode = STOP
            #Get current time
            currentTime = self.getTime()
            
            #If time passed is greater than 3.5 seconds (to account for how long the robot takes to become still)
            #TODO use velocity to start timer
            if currentTime - self.timerStartTime > 3.5:
                #Robot has deposited
                #Once time has passed, reset everything
                self.timerStartTime = 0
                self.mode = MOVE_FORWARD
                self.depositing = False
                self.humanLoaded = False
        
        #if collecting a human        
        elif self.collecting:
            self.mode = STOP
            #Get current time
            currentTime = self.getTime()
            
            #If time passed is greater than 3.5 seconds (to account for how long the robot takes to become still)
            #TODO use velocity to start timer
            if currentTime - self.timerStartTime > 3.5:
                #Robot has picked up human
                #Once time has passed, reset everything
                self.timerStartTime = 0
                self.mode = MOVE_FORWARD
                self.collecting = False
        
        
      
    def run(self):
        while True:             
            self.update()
            # Send actuators commands according to the mode
            if self.mode == MOVE_FORWARD:
                self.speeds[0] = 1 * self.maxSpeed
                self.speeds[1] = 1 * self.maxSpeed
            elif self.mode == MOVE_BACKWARDS:
                self.speeds[0] = -0.5 * self.maxSpeed
                self.speeds[1] = -1 * self.maxSpeed
            elif self.mode == TURN_RIGHT:
                #set left wheel speed
                self.speeds[0] = 0.6 * self.maxSpeed
                #set right wheel speed
                self.speeds[1] = -0.2 * self.maxSpeed
            elif self.mode == TURN_LEFT:
                #set left wheel speed
                self.speeds[0] = -0.2 * self.maxSpeed
                #set right wheel speed
                self.speeds[1] = 0.6 * self.maxSpeed
                
            elif self.mode == TURN_RIGHT_OBJECT:
                #set left wheel speed
                self.speeds[0] = 1 * self.maxSpeed
                #set right wheel speed
                self.speeds[1] = 0.8 * self.maxSpeed
                
            elif self.mode == TURN_LEFT_OBJECT:
                #set left wheel speed
                self.speeds[0] = 0.8 * self.maxSpeed
                #set right wheel speed
                self.speeds[1] = 1 * self.maxSpeed
                
            elif self.mode == STOP:
                if self.speeds[0] > 0:
                    self.speeds[0] -= 1
                if self.speeds[0] < 0:
                    self.speeds[0] = 0
                if self.speeds[1] > 0:
                    self.speeds[1] -= 1
                if self.speeds[0] < 0:
                    self.speeds[1] = 0
                
                
            self.wheels[0].setVelocity(self.speeds[0])
            self.wheels[1].setVelocity(self.speeds[1])

            # Perform a simulation step, quit the loop when
            # Webots is about to quit.
            if self.step(self.timeStep) == -1:
                break


controller = Player()
controller.run()
