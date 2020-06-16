from controller import Robot
import time
import math
import struct

"""
Example erebus robot controller
Written by Alfred Roberts - 2020

PLEASE NOTE THIS IS A WIP AND CURRENTLY ISN'T FULLY FINISHED AND DOESN'T WORK PROPERLY
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
        self.maxSpeed = 6.28
        
        self.mode = MOVE_FORWARD
        self.wheels = []
        self.distanceSensors = []
        self.leftSensors = []
        self.rightSensors = []
        self.frontSensors = []
        
        self.speeds = [0.0,0.0]

        self.emitter = self.getEmitter('emitter')
        self.gps = self.getGPS('gps')
        
        self.humanLoaded = False
        self.activityLoaded = False
        self.collecting = False
        self.collectingActivity = False
        self.depositing = False
        self.timerStartTime = 0
        self.loadedActivityColour = [0,0,0]
        
        #config camera
        self.camera = self.getCamera('camera')
        self.camera.enable(self.timeStep)
        self.camera.recognitionEnable(self.timeStep)
        
        #config wheels
        self.wheels.append(self.getMotor("left wheel motor"))
        self.wheels.append(self.getMotor("right wheel motor"))
        
        #move forever
        self.wheels[0].setPosition(float("inf"))
        self.wheels[1].setPosition(float("inf"))
        
        #config sensors
        
        self.frontSensors.append(self.getDistanceSensor('ps7'))
        self.frontSensors[0].enable(self.timeStep)
        
        self.frontSensors.append(self.getDistanceSensor('ps0'))
        self.frontSensors[1].enable(self.timeStep)

        self.leftSensors.append(self.getDistanceSensor('ps5'))
        self.leftSensors[0].enable(self.timeStep)
        
        self.leftSensors.append(self.getDistanceSensor('ps7'))
        self.leftSensors[1].enable(self.timeStep)

        self.rightSensors.append(self.getDistanceSensor('ps1'))
        self.rightSensors[0].enable(self.timeStep)
        
        self.rightSensors.append(self.getDistanceSensor('ps2'))
        self.rightSensors[1].enable(self.timeStep)
        
        #idk
        self.wheels[0].setVelocity(0.0)
        self.wheels[1].setVelocity(0.0)
    
    def getDetectedObjects(self):
        '''Get detected objects from camera'''
        objects = self.camera.getRecognitionObjects()
        return objects
    
    def getBaseObjects(self):
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
    
    def getHumanObjects(self):
        '''Get human objects from detected objects'''
        objects = self.getDetectedObjects()
        
        humans = []
        
        #for all objects in detected objects
        for item in objects:
            #if its the colour of the human recongition colour
            if item.get_colors() == [1,1,1]:
                #get its position relative to robot
                human_pos = item.get_position()
                #get its position in the image
                human_image_pos = item.get_position_on_image()
                #append to array as [relative [x,y,z] position, position on camera view]
                humans.append([human_pos,human_image_pos])
        
        return humans
    
    def getWallObjects(self):
        '''Get human objects from detected objects'''
        objects = self.getDetectedObjects()
        
        walls = []
        
        #for all objects in detected objects
        for item in objects:
            #if its the colour of the wall recongition colour
            if item.get_colors() == [0.33,0.33,0.33]:
                #get its position relative to robot
                wall_pos = item.get_position()
                #get its position in the image
                wall_image_pos = item.get_position_on_image()
                #get its size in the image in pixels
                wall_image_size = item.get_size_on_image()
                #append to array as [relative [x,y,z] position, position on camera view, size on camera]
                walls.append([wall_pos,wall_image_pos, wall_image_size])
        
        return walls

    def nearObject(self, objPos: list):
        '''Return true if relative object is < 0.5 metres away'''
        #TODO make 0.5 a constant that can change
        return abs(objPos[0]) < 0.08 and abs(objPos[2]) < 0.08
    
    def findClosestObject(self, objects: list):
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
    
    def moveToHuman(self):
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

            print('doing things')
            
            if dx < 0:
                # Human on the right
                self.mode = TURN_RIGHT_OBJECT
            else:
                # Human on the left
                self.mode = TURN_LEFT_OBJECT
                
    def moveToBase(self):
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
                    
    def moveToDoorWay(self):
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
            
            print('wall1',wall1)
            print('wall2',wall2)

            doorWayCenter = (wall1[1][0] + wall2[1][0]) / 2
            
            #Find the difference in x values between centre of camera and human image position
            dx = center - doorWayCenter
            
            if dx < 0:
                # Human on the right
                self.mode = TURN_RIGHT_OBJECT
            else:
                # Human on the left
                self.mode = TURN_LEFT_OBJECT

    def getActivityBlocks(self):
        '''Get human objects from detected objects'''
        objects = self.getDetectedObjects()
        
        blocks = []
        
        #for all objects in detected objects
        for item in objects:
            #if its the colour of the wall recongition colour
            if item.get_colors() != [0.33,0.33,0.33] and item.get_colors() != [0.3,0,1]:
                
                colour_validate = [i % 1 for i in item.get_colors()]

                print('Validation:',item.get_colors(),colour_validate)

                if colour_validate == [0,0,0]:
                    block_pos = item.get_position()

                    block_image_pos = item.get_position_on_image()

                    block_image_size = item.get_size_on_image()
                    
                    block_colour = item.get_colors()

                    blocks.append([block_pos,block_image_pos,block_image_size,block_colour])
        
        return blocks    

    def moveToActivity(self):
        #Get activity block objects
        blocks = self.getActivityBlocks()
        #Get camera width
        width = self.camera.getWidth()

        activityColour = [0,0,0]
        
        center = width / 2
        
        if len(blocks) > 0:
            #Find closest activity block as an index
            closestActivityIndex = self.findClosestObject(blocks)
            #Get activity position in image
            activityImagePos = blocks[closestActivityIndex][1][0]

            activityColour = blocks[closestActivityIndex][3]
            
            #Find the difference in x values between centre of camera and activity block image position
            dx = center - activityImagePos
            
            if dx < 0:
                # Base on the right
                self.mode = TURN_RIGHT_OBJECT
            else:
                # Base on the left
                self.mode = TURN_LEFT_OBJECT
        
        print('Colour',activityColour)
        return activityColour
    
    def update(self):
        '''Update robot movement mode'''
        
        #Set mode to forward incase nothing else passes in the function
        self.mode = MOVE_FORWARD

        activityHeading = [0,0,0]

        #self.moveToDoorWay()
        
        #If a human is loaded and not collecting or depositing
        #if self.humanLoaded and not self.collecting and not self.depositing:
            #Move to base
        #    self.moveToBase()
            
        #for all sensors (greater value means obstical is closer)
        for i in range(2):
            #For sensors of the left
            #print(self.leftSensors[i].getValue())
            if self.leftSensors[i].getValue() > 80:
                self.mode = TURN_RIGHT
            #For sensors of the right
            elif self.rightSensors[1-i].getValue() > 80:
                self.mode = TURN_LEFT
                
        #for i in range(2):
            #For front two sensors
        #    if self.frontSensors[i].getValue() > 80:
        #        self.mode = MOVE_BACKWARDS
        
        #If no human is loaded and not collecting or depositing
        if not self.humanLoaded and not self.collecting and not self.depositing:
            #Move to human
            self.moveToHuman()

        #if not self.activityLoaded and not self.collectingActivity and not self.depositing and not self.collecting:
        #    activityHeading = self.moveToActivity()
        
        
        
        #Get base and human objects
        bases = self.getBaseObjects()
        humans = self.getHumanObjects()
        #activities = self.getActivityBlocks()
        #print('activities',activities)
                
        
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
        #TODO move humanloaded to after time is up
        for human in humans:
            #If near human and human is not loaded and not already collecting
            if self.nearObject(human[0]) and not self.humanLoaded and not self.collecting:
                self.collecting = True
                self.mode = STOP
                self.humanLoaded = True
                #Get start time for picking up human so it can used for calculating how long its been picking up for.
                self.timerStartTime = self.getTime()
                break

        # for block in activities:
        #     #If near activity block and activity is not loaded and not already collecting
        #     if self.nearObject(block[0]) and not self.activityLoaded and not self.collectingActivity and not self.collecting:
        #         self.collectingActivity = True
        #         self.mode = STOP
        #         self.activityLoaded = True
        #         #Get start time for picking up human so it can used for calculating how long its been picking up for.
        #         self.timerStartTime = self.getTime()
        #         break
            
        # if self.depositing:
        #     self.mode = STOP
        #     #Get current time
        #     currentTime = self.getTime()
            
        #     #If time passed is greater than 3.5 seconds (to account for how long the robot takes to become still)
        #     #TODO use velocity to start timer
        #     if currentTime - self.timerStartTime > 3.5:
        #         #Robot has deposited
        #         #Once time has passed, reset everything
        #         self.timerStartTime = 0
        #         self.mode = MOVE_FORWARD
        #         self.depositing = False
        #         self.humanLoaded = False
        
        #if collecting a human        
        if self.collecting:
            self.mode = STOP
            #Get current time
            currentTime = self.getTime()
            message = struct.pack('i i i c', 0, 27, -37, b'H')
            self.emitter.send(message)
            
            #If time passed is greater than 3.5 seconds (to account for how long the robot takes to become still)
            #TODO use velocity to start timer
            if currentTime - self.timerStartTime > 5.5:
                #Robot has picked up human
                #Once time has passed, reset everything
                self.timerStartTime = 0
                self.mode = MOVE_FORWARD
                self.collecting = False

        # elif self.collectingActivity:
        #     self.mode = STOP
        #     #Get current time
        #     currentTime = self.getTime()
            
        #     #If time passed is greater than 3.5 seconds (to account for how long the robot takes to become still)
        #     #TODO use velocity to start timer
        #     if currentTime - self.timerStartTime > 3.5:
        #         #Robot has picked up human
        #         #Once time has passed, reset everything
        #         self.timerStartTime = 0
        #         self.mode = MOVE_FORWARD
        #         self.collectingActivity = False
        #         self.loadedActivityColour = activityHeading
        
        
      
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
                self.speeds[0] = 0
                self.speeds[1] = 0
                
                
            self.wheels[0].setVelocity(self.speeds[0])
            self.wheels[1].setVelocity(self.speeds[1])

            # Perform a simulation step, quit the loop when
            # Webots is about to quit.
            if self.step(self.timeStep) == -1:
                break


controller = Player()
controller.run()
