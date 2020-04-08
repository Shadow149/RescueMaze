"""Supervisor Controller Prototype v1
   Written by Robbie Goldman and Alfred Roberts
"""

from controller import Supervisor
import os
import random
import struct
from RelocateCalculator import generateRelocatePosition

#Create the instance of the supervisor class
supervisor = Supervisor()

#Get this supervisor node - so that it can be rest when game restarts
mainSupervisor = supervisor.getFromDef("MAINSUPERVISOR")

#Maximum time for a match
maxTime = 8 * 60

class Queue:
    def __init__(self):
        self.queue = []
    def enqueue(self,data):
        return self.queue.append(data)
    def dequeue(self):
        return self.queue.pop(0)
    def peek(self):
        return self.queue[0]
    def is_empty(self):
        return len(self.queue) == 0

class RobotHistory(Queue):
    def __init__(self):
        super().__init__()
    def enqueue(self,data):
        if len(self.queue) > 8:
            self.dequeue()
        return self.queue.append(data)
    
class Robot:
    '''Robot object to hold values whether its in a base or holding a human'''
    def __init__(self, node):
        '''Initialises the in a base, has a human loaded and score values'''

        self.wb_node = node

        self.wb_translationField = self.wb_node.getField('translation')

        self.inCheckpoint = True

        self.history = RobotHistory()

        self._score = 0
    
        self._timeStopped = 0
        self._stopped = False
        self._stoppedTime = None

        self.messages = Queue()

        self.lastVisitedCheckPointPosition = []

        self.visitedCheckpoints = []
    
    @property
    def position(self) -> list:
        return self.wb_translationField.getSFVec3f()
    
    @position.setter
    def position(self, pos: list) -> None:
        self.wb_translationField.setSFVec3f(pos)

    def _isStopped(self) -> bool:
        vel = self.wb_node.getVelocity()
        robotStopped = abs(vel[0]) < 0.01 and abs(vel[1]) < 0.01 and abs(vel[2]) < 0.01
        return robotStopped
        
    def timeStopped(self) -> float:
        self._stopped = self._isStopped()
        
        #if it isn't stopped yet
        if self._stoppedTime == None:
            if self._stopped:
                #get time the robot stopped
                self._stoppedTime = supervisor.getTime()
        else:
            #if its stopped
            if self._stopped:
                #get current time
                currentTime = supervisor.getTime()
                #calculate the time the robot stopped
                self._timeStopped = currentTime - self._stoppedTime
            else:
                #if it's no longer stopped, reset variables
                self._stoppedTime = None
                self._timeStopped = 0
        
        return self._timeStopped
        
    def increaseScore(self, score: int) -> None:
        self._score += score
    
    def getScore(self) -> None:
        return self._score

class Human():
    '''Human object holding the boundaries'''
    def __init__(self, node, ap: int, vtype: str, score: int):
        '''Initialises the radius and position of the human'''
    
        self.wb_node = node

        self.wb_translationField = self.wb_node.getField('translation')

        self.arrayPosition = ap
        self.scoreWorth = score
        self.radius = 0.15
        self.victim_type = vtype

        self.simple_victim_type = self.get_simple_victim_type()

        self.identified = False

    @property
    def position(self) -> list:
        return self.wb_translationField.getSFVec3f()
    
    @position.setter
    def position(self, pos: list) -> None:
        self.wb_translationField.setSFVec3f(pos)

    def identify(self):
        supervisor.getFromDef('human'+str(self.arrayPosition)+'texture').getField('url').setMFString(0,'./textures/'+self.victim_type+'_found.png')
        self.identified = True

    def get_simple_victim_type(self):
        if self.victim_type == 'victim_harmed':
            return 'H'
        elif self.victim_type == 'victim_unharmed':
            return 'U'
        elif self.victim_type == 'victim_stable':
            return 'S'

    def getType(self) -> int:
        '''Set type of human (adult or child) through object size'''
        #Get human size
        humanSize = self.wb_node.getField("scale").getSFVec3f()

        if humanSize[1] == 0.5:
            return 2  
        else:
            return 1  

    def checkPosition(self, pos: list, min_dist: float) -> bool:
        '''Check if a position is near an object, based on the min_dist value'''
        #Get distance from the object to the passed position using manhattan distance for speed
        #TODO Check if we want to use euclidian or manhattan distance -- currently manhattan
        distance = abs(self.position[0] - pos[0]) + abs(self.position[2] - pos[2])
        return distance < min_dist

class Checkpoint:
    '''Checkpoint object holding the boundaries'''
    def __init__(self, min: list, max: list, center: list):
        '''Initialize the maximum and minimum corners for the checkpoint'''
        self.min = min
        self.max = max
        self.center = center
    
    def checkPosition(self, pos: list) -> bool:
        '''Check if a position is in this checkpoint'''
        #If the x position is within the bounds
        if pos[0] >= self.min[0] and pos[0] <= self.max[0]:
            #if the z position is within the bounds
            if pos[2] >= self.min[1] and pos[2] <= self.max[1]:
                #It is in this checkpoint
                return True
        
        #It is not in this checkpoint
        return False

def getPath(number: int) -> str:
    '''Get the path to the correct controller'''
    #The current path to this python file
    filePath = os.path.dirname(os.path.abspath(__file__))
    
    filePath = filePath.replace('\\','/')

    #Split into parts on \
    pathParts = filePath.split("/")
    
    filePath = ""
    #Add all parts back together
    for part in pathParts:
        #Except the last one
        if part != pathParts[-1]:
            #Concatenate with / not \ (prevents issues with escape characters)
            filePath = filePath + part + "/"
    
    #Controller number part added
    if number == 0:
        filePath = filePath + "robot0Controller/robot0Controller.py"
    elif number == 1:
        filePath = filePath + "robot1Controller/robot1Controller.py"
    else:
        #Returns none if id was not valid
        filePath = None
    
    return filePath

def resetControllerFile(number: int) -> None:
    '''Open the controller at the file location and blanks it'''
    filePath = getPath(number)
    
    if filePath != None:
        controllerFile = open(filePath, "w")
        controllerFile.close()

def createController(number: int, fileData: list) -> list:
    '''Opens the controller at the file location and writes the data to it'''
    filePath = getPath(number)
    
    if filePath == None:
        return None, None
    
    controllerFile = open(filePath, "w")
    controllerFile.write(fileData)
    controllerFile.close()
    
    #If there is a name in the file
    if "RobotName:" in fileData:
        #Find the name
        name = fileData[fileData.index("RobotName:") + 10:]
        name = name.split("\n")[0]
        #Return data with a name
        return name, number
    #Return data without a name
    return None, number
    
def assignController(num: int, name: str) -> None:
    '''Send message to robot window to say that controller has loaded and with what name'''
    if name == None:
        name = "None"
    else:
        name = name[:-1]
    if num == 0:
        supervisor.wwiSendText("loaded0," + name)
    if num == 1:
        supervisor.wwiSendText("loaded1," + name)

def resetController(num: int) -> None:
    '''Send message to robot window to say that controller has been unloaded'''
    if num == 0:
        resetControllerFile(0)
        supervisor.wwiSendText("unloaded0")
    if num == 1:
        resetControllerFile(1)
        supervisor.wwiSendText("unloaded1")

def updateHistory():
    supervisor.wwiSendText("historyUpdate"+","+",".join(robot0Obj.history.queue)+":"+",".join(robot1Obj.history.queue))

def getHumans():
    print('yeet')
    #Iterate for each human
    for i in range(numberOfHumans):
        #Get each human from children field in the human root node HUMANGROUP
        human = humanNodes.getMFNode(i)

        victimDescription = supervisor.getFromDef('human'+str(i)+'solid').getField('description').getSFString()
        textureType = victimDescription.split(',')[0]
        scoreWorth = int(victimDescription.split(',')[1])
        print(textureType)

        #Create Human Object from human position
        humanObj = Human(human ,i, textureType,scoreWorth)
        humans.append(humanObj)

def resetVictimsTextures():
    #Iterate for each victim
    for i in range(numberOfHumans):
        print(i)
        victimDescription = supervisor.getFromDef('human'+str(i)+'solid').getField('description').getSFString()
        textureType = victimDescription.split(',')[0]
        print(textureType)
        supervisor.getFromDef('human'+str(i)+'texture').getField('url').setMFString(0,'./textures/'+textureType+'_not_found.png')

def relocate(num):
    if int(num) == 0:
        relocatePosition = robot0Obj.lastVisitedCheckPointPosition
        print(relocatePosition)

        if relocatePosition == []:
            print('No checkpoint visited')
        else:
            robot0Obj.position = [relocatePosition[0],-0.0751,relocatePosition[2]]
    elif int(num) == 1:
        relocatePosition = robot1Obj.lastVisitedCheckPointPosition

        if relocatePosition == []:
            print('No checkpoint visited')
        else:
            robot1Obj.position = [relocatePosition[0],-0.0751,relocatePosition[2]]


#Get the output from the object placement supervisor
#objectPlacementOutput = supervisor.getFromDef("OBJECTPLACER").getField("customData")

#Empty list to contain bases
checkpoints = []

#Global empty list to contain human objects
humans = []
#Boolean value stating whether or not humans have been placed in the map
humansLoaded = False
#Get group node containing humans 
humanGroup = supervisor.getFromDef('HUMANGROUP')
humanNodes = humanGroup.getField("children")
#Get number of humans in map
numberOfHumans = humanNodes.getCount()
        

# activity0 = supervisor.getFromDef('ACT0')
# activity0_mat = supervisor.getFromDef('ACT0MAT')
# activity0_matobj = ActivityBlock(activity0_mat.getField("translation").getSFVec3f(),activity0_mat,None)
# activity0obj = ActivityBlock(activity0.getField("translation").getSFVec3f(),activity0,activity0_matobj)


#Iterate for each checkpoint
numberOfCheckpoints = int(supervisor.getFromDef('CHECKPOINTS').getField('children').getCount() / 3)

for i in range(0, numberOfCheckpoints):
    #Get the checkpoint minimum node and translation
    checkpointMin = supervisor.getFromDef("checkpoint" + str(i) + "min")
    minPos = checkpointMin.getField("translation")
    #Get maximum node and translation
    checkpointMax = supervisor.getFromDef("checkpoint" + str(i) + "max")
    maxPos = checkpointMax.getField("translation")
    #Get the vector positons
    minPos = minPos.getSFVec3f()
    maxPos = maxPos.getSFVec3f()

    checkpointCenter = supervisor.getFromDef('checkpoint'+str(i))
    centerPos = checkpointCenter.getField("translation")

    centerPos = centerPos.getSFVec3f()
    #Create a checkpoint object using the min and max (x,z)
    checkpointObj = Checkpoint([minPos[0], minPos[2]], [maxPos[0], maxPos[2]], centerPos)
    checkpoints.append(checkpointObj)


#Not currently running the match
currentlyRunning = False
previousRunState = False

#The game has not yet started
gameStarted = False

#Get the robot nodes by their DEF names
robot0 = supervisor.getFromDef("ROBOT0")
robot1 = supervisor.getFromDef("ROBOT1")

#Init both robots as objects to hold their info
robot0Obj = Robot(robot0)
robot1Obj = Robot(robot1)

#Both robots start in bases
#robot0InCheckpoint = True
#robot1InCheckpoint = True

#The simulation is running
simulationRunning = True
finished = False

#Reset the controllers
resetControllerFile(0)
resetControllerFile(1)

#Starting scores
#score0 = 0
#score1 = 0

#How long the game has been running for
timeElapsed = 0
lastTime = -1

#Send message to robot window to perform setup
supervisor.wwiSendText("startup")

#For checking the first update with the game running
first = True

receiver = supervisor.getReceiver('receiver')
receiver.enable(32)

#Until the match ends (also while paused)
while simulationRunning:

    #The first frame of the game running only
    if first and currentlyRunning:
        #Restart both controllers
        robot0.restartController()
        robot1.restartController()
        first = False

    r0 = False
    r1 = False
    #Test if the robots are in bases
    for checkpoint in checkpoints:
        if checkpoint.checkPosition(robot0Obj.position):
            r0 = True
            robot0Obj.lastVisitedCheckPointPosition = checkpoint.center

            alreadyVisited = False

            if len(robot0Obj.visitedCheckpoints) > 0:
                for visitedCheckpoint in robot0Obj.visitedCheckpoints:
                    if visitedCheckpoint == checkpoint.center:
                        alreadyVisited = True
            
            if not alreadyVisited:
                robot0Obj.visitedCheckpoints.append(checkpoint.center)
                robot0Obj.increaseScore(10)
                robot0Obj.history.enqueue("Found checkpoint  +10")
                updateHistory()


        if checkpoint.checkPosition(robot1Obj.position):
            r1 = True
            robot1Obj.lastVisitedCheckPointPosition = checkpoint.center

            alreadyVisited = False

            if len(robot1Obj.visitedCheckpoints) > 0:
                for visitedCheckpoint in robot1Obj.visitedCheckpoints:
                    if visitedCheckpoint == checkpoint.center:
                        alreadyVisited = True
            
            if not alreadyVisited:
                robot1Obj.visitedCheckpoints.append(checkpoint.center)
                robot1Obj.increaseScore(10)
                robot1Obj.history.enqueue("Found checkpoint  +10")
                updateHistory()

    #Print when robot0 enters or exits a checkpoint
    if robot0Obj.inCheckpoint != r0:
        robot0Obj.inCheckpoint = r0
        if robot0Obj.inCheckpoint:
            print("Robot 0 entered a checkpoint")
        else:
            print("Robot 0 exited a checkpoint")

    #Print when robot1 enters or exits a checkpoint
    if robot1Obj.inCheckpoint != r1:
        robot1Obj.inCheckpoint = r1
        if robot1Obj.inCheckpoint:
            print("Robot 1 entered a checkpoint")
        else:
            print("Robot 1 exited a checkpoint")
    
    if receiver.getQueueLength() > 0:
        receivedData = receiver.getData()
        tup = struct.unpack('i i i c',receivedData)

        robotNumber = tup[0]
        x = tup[1]
        z = tup[2]

        estimated_victim_position = (x/100,0,z/100)

        victimType = tup[3].decode("utf-8")

        if robotNumber == 0:
            print('message updated')
            robot0Obj.messages.enqueue((estimated_victim_position,victimType))
            print(robot0Obj.messages.queue)
        else:
            robot1Obj.messages.enqueue((estimated_victim_position,victimType))

        receiver.nextPacket()

    

    #TODO NEED TO ADD LED FUNCTIONALITY
    if robot0Obj.timeStopped() >= 5:

        if not robot0Obj.messages.is_empty():

            print('peek',robot0Obj.messages.peek())
            r0_est_vic_pos = robot0Obj.messages.peek()[0]
            r0_est_vic_type = robot0Obj.messages.peek()[1]

            robot0Obj.messages.dequeue()

            for i, h in enumerate(humans):
                if not h.identified:
                    if h.checkPosition(r0_est_vic_pos,0.15):

                        print("Robot 0 Successful Victim Identification")

                        pointsScored = h.scoreWorth

                        if r0_est_vic_type.lower() == h.simple_victim_type.lower():
                            robot0Obj.history.enqueue("Successful Vitim Type Correct  Bonus + 10")
                            pointsScored += 10

                        robot0Obj.history.enqueue("Successful Victim Identification "+" +"+str(h.scoreWorth))
                        robot0Obj.increaseScore(pointsScored)
                                        
                        h.identify()
                        updateHistory()

    #TODO copy for robot 1 ^^^^^
                
    #If the running state changes
    if previousRunState != currentlyRunning:
        #Update the value and print
        previousRunState = currentlyRunning
        print("Run State:", currentlyRunning)
    
    #Get human positions if game started
    if gameStarted and not humansLoaded:
        
        getHumans()
        humansLoaded = True
        
    
    #Get the message in from the robot window(if there is one)
    message = supervisor.wwiReceiveText()
    #If there is a message
    if message != "":
        #split into parts
        parts = message.split(",")
        #If there are parts
        if len(parts) > 0:
            if parts[0] == "run":
                #Start running the match
                currentlyRunning = True
                lastTime = supervisor.getTime()
                gameStarted = True
            if parts[0] == "pause":
                #Pause the match
                currentlyRunning = False
            if parts[0] == "reset":
                print("Reset message Received")
                #Reset both controller files
                resetControllerFile(0)
                resetControllerFile(1)
                resetVictimsTextures()
                #Reset the simulation
                supervisor.simulationReset()
                simulationRunning = False
                #Restart this supervisor
                mainSupervisor.restartController()

            if parts[0] == "robot0File":
                #Load the robot 0 controller
                if not gameStarted:
                    data = message.split(",", 1)
                    if len(data) > 1:
                        name, id = createController(0, data[1])
                        assignController(id, name)
                else:
                    print("Please choose controllers before simulation starts.")
            if parts[0] == "robot1File":
                #Load the robot 1 controller
                if not gameStarted:
                    data = message.split(",", 1)
                    if len(data) > 1:
                        name, id = createController(1, data[1])
                        assignController(id, name)
                else:
                    print("Please choose controllers before simulation starts.")
            if parts[0] == "robot0Unload":
                #Unload the robot 0 controller
                if not gameStarted:
                    resetController(0)
            if parts[0] == "robot1Unload":
                #Unload the robot 1 controller
                if not gameStarted:
                    resetController(1)
            if parts[0] == 'relocate':
                data = message.split(",", 1)
                if len(data) > 1:
                    relocate(data[1])
                pass
    
    #Send the update information to the robot window
    supervisor.wwiSendText("update," + str(robot0Obj.getScore()) + "," + str(robot1Obj.getScore()) + "," + str(timeElapsed))

    #If the time is up
    if timeElapsed >= maxTime:
        finished = True
        supervisor.wwiSendText("ended")
    
    #If the match is running
    if currentlyRunning and not finished:
        #Get the time since the last frame
        frameTime = supervisor.getTime() - lastTime
        #Add to the elapsed time
        timeElapsed = timeElapsed + frameTime
        #Get the current time
        lastTime = supervisor.getTime()
        #Step the simulation on
        step = supervisor.step(32)
        #If the simulation is terminated or the time is up
        if step == -1:
            #Stop simulating
            simulationRunning = False