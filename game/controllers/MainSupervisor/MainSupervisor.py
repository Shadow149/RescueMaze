"""Supervisor Controller Prototype v6
   Written by Robbie Goldman and Alfred Roberts

Changelog:
 - Only get points if you have a human loaded and enter a base
 - Robots can only pick up one human at a time
 - Robot must have stopped for 2 seconds to deposit and pick up human
 - Added check for message from position supervisor before taking human positions
 - Added restart to object placement controller to allow obstacles to be placed on reset
"""

from controller import Supervisor
import os
import random

#Create the instance of the supervisor class
supervisor = Supervisor()

#Get the robot nodes by their DEF names
robot0 = supervisor.getFromDef("ROBOT0")
robot1 = supervisor.getFromDef("ROBOT1")

#Get the translation fields
robot0Pos = robot0.getField("translation")
robot1Pos = robot1.getField("translation")

#Get the output from the object placement supervisor
objectPlacementOutput = supervisor.getFromDef("OBJECTPLACER").getField("customData")
#Restart object placement supervisor (so that when reset it runs again)
supervisor.getFromDef("OBJECTPLACER").restartController()

#Get this supervisor node - so that it can be rest when game restarts
mainSupervisor = supervisor.getFromDef("MAINSUPERVISOR")

#Maximum time for a match
maxTime = 120

class Robot:
    '''Robot object to hold values whether its in a base or holding a human'''
    def __init__(self):
        '''Initialises the in a base, has a human loaded and score values'''
        self.inBase = True
        self._humanLoaded = False
        self._score = 0
    
        self._timeStopped = 0
        self._stopped = False
        self._stoppedTime = None
        
        
    @staticmethod
    def _isStopped(robotNode) -> bool:
        vel: list = robotNode.getVelocity()
        robotStopped = abs(vel[0]) < 0.01 and abs(vel[1]) < 0.01 and abs(vel[2]) < 0.01
        return robotStopped
        
    def timeStopped(self,robotNode) -> float:
        self._stopped = Robot._isStopped(robotNode)
        
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
            
    
    def hasHumanLoaded(self) -> bool:
        return self._humanLoaded

    def loadHuman(self) -> None:
        self._humanLoaded = True
        
    def unLoadHuman(self) -> None:
        self._humanLoaded = False
        
    def increaseScore(self, score: int) -> None:
        #TODO add win condition
        self._score += score
    
    def getScore(self) -> None:
        return self._score

class Human:
    '''Human object holding the boundaries'''
    def __init__(self, pos: list, ap: int):
        '''Initialises the radius and position of the human'''
        self.position = pos
        self.arrayPosition = ap
    
    def checkPosition(self, pos: list, min_dist: float) -> bool:
        '''Check if a position is near a human, based on the min_dist value'''
        #Get distance from the human to the passed position using manhattan distance for speed
        #TODO Check if we want to use euclidian or manhattan distance -- currently manhattan
        distance = abs(self.position[0] - pos[0]) + abs(self.position[2] - pos[2])
        return distance < min_dist
    
    def setPosition(self, position: list) -> None:
        '''Set position of human in object and in scene'''
        #Get human from scene nodes
        human = humanNodes.getMFNode(self.arrayPosition)
        #Set human object's position and in the scene 
        humanPos = human.getField("translation")
        humanPos.setSFVec3f(position)
        self.position = position
        

class base ():
    '''Base object holding the boundaries'''
    def __init__(self, min: list, max: list):
        '''Initialize the maximum and minimum corners for the base'''
        self.min = min
        self.max = max
    
    def checkPosition(self, pos: list) -> bool:
        '''Check if a position is in this base'''
        #If the x position is within the bounds
        if pos[0] >= self.min[0] and pos[0] <= self.max[0]:
            #if the z position is within the bounds
            if pos[2] >= self.min[1] and pos[2] <= self.max[1]:
                #It is in this base
                return True
        
        #It is not in this base
        return False

#Empty list to contain bases
bases = []

#Global empty list to contain human objects
humans = []
#Boolean value stating whether or not humans have been placed in the map
humansLoaded = False
#Get group node containing humans 
humanGroup = supervisor.getFromDef('HUMANGROUP')
humanNodes = humanGroup.getField("children")
#Get number of humans in map
numberOfHumans = humanNodes.getCount()

def getHumans():
    #Iterate for each human
    for i in range(numberOfHumans):
        #Get each human from children field in the human root node HUMANGROUP
        human = humanNodes.getMFNode(i)
        #Get human translation
        humanPos = human.getField("translation")
        #Create Human Object from human position
        humanObj = Human(humanPos.getSFVec3f(),i)
        humans.append(humanObj)


#Iterate for each base
for i in range(0, 3):
    #Get the base minimum node and translation
    baseMin = supervisor.getFromDef("base" + str(i) + "Min")
    minPos = baseMin.getField("translation")
    #Get maximum node and translation
    baseMax = supervisor.getFromDef("base" + str(i) + "Max")
    maxPos = baseMax.getField("translation")
    #Get the vector positons
    minPos = minPos.getSFVec3f()
    maxPos = maxPos.getSFVec3f()
    #Create a base object using the min and max (x,z)
    baseObj = base([minPos[0], minPos[2]], [maxPos[0], maxPos[2]])
    bases.append(baseObj)

def getPath(number: int) -> str:
    '''Get the path to the correct controller'''
    #The current path to this python file
    filePath = os.path.dirname(os.path.abspath(__file__))
    
    #Split into parts on \
    pathParts = filePath.split("\\")
    
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

#Not currently running the match
currentlyRunning = False
previousRunState = False

#The game has not yet started
gameStarted = False

#Init both robots as objects to hold their info
robot0Obj = Robot()
robot1Obj = Robot()

#Both robots start in bases
#robot0InBase = True
#robot1InBase = True

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
    for b in bases:
        if b.checkPosition(robot0Pos.getSFVec3f()):
            r0 = True
        if b.checkPosition(robot1Pos.getSFVec3f()):
            r1 = True
            
    #Test if the robots are near a human
    #TODO finish full human pickup function -- Require stop
    for i, h in enumerate(humans):
        #If within 0.5 metres of human
        if h.checkPosition(robot0Pos.getSFVec3f(),1):
            if not robot0Obj.hasHumanLoaded():
                #if the robot has stopped for more than 2 seconds
                if robot0Obj.timeStopped(robot0) >= 2:
                    print("Robot 0 is near a human")
                    robot0Obj.increaseScore(1)
                    robot0Obj.loadHuman()
                    
                    #send message to robot window saying human is loaded
                    supervisor.wwiSendText("humanLoaded0")
                    
                    #Move human to some position far away
                    newPosition = [0,-1000,0]
                    h.setPosition(newPosition)
                    
        if h.checkPosition(robot1Pos.getSFVec3f(),2):
            if not robot1Obj.hasHumanLoaded():
                #if the robot has stopped for more than 2 seconds
                if robot1Obj.timeStopped(robot1) >= 2:
                    print("Robot 1 is near a human")
                    robot1Obj.increaseScore(1)
                    robot1Obj.loadHuman()
                    
                    #send message to robot window saying human is loaded
                    supervisor.wwiSendText("humanLoaded1")
                    
                    #Move human to some position far away
                    newPosition = [0,-1000,0]
                    h.setPosition(newPosition)
            
    #Print when robot0 enters or exits a base
    if robot0Obj.inBase != r0:
        robot0Obj.inBase = r0
        if robot0Obj.inBase:
            print("Robot 0 entered a base")
        else:
            print("Robot 0 exited a base")

    if robot0Obj.inBase:
        if robot0Obj.hasHumanLoaded():
            #if the robot has stopped for more than 2 seconds
            if robot0Obj.timeStopped(robot0) >= 2:
                #if robot has a human loaded, gain a point
                robot0Obj.increaseScore(1)
                robot0Obj.unLoadHuman()
                
                #send message to robot window saying human is unloaded
                supervisor.wwiSendText("humanUnloaded0")
                
                print("Robot 0 brought a human to safety")
        
    
    #Print when robot1 enters or exits a base
    if robot1Obj.inBase != r1:
        robot1Obj.inBase = r1
        if robot1Obj.inBase:
            print("Robot 1 entered a base")
        else:
            print("Robot 1 exited a base")
            
    if robot1Obj.inBase:
        if robot1Obj.hasHumanLoaded():
            #if the robot has stopped for more than 2 seconds
            if robot1Obj.timeStopped(robot1) >= 2:
                #if robot has a human loaded, gain a point
                robot1Obj.increaseScore(1)
                robot1Obj.unLoadHuman()
                
                #send message to robot window saying human is unloaded
                supervisor.wwiSendText("humanUnloaded1")
                
                print("Robot 1 brought a human to safety")
                
    #If the running state changes
    if previousRunState != currentlyRunning:
        #Update the value and print
        previousRunState = currentlyRunning
        print("Run State:", currentlyRunning)
    
    #Get human positions if game started
    if gameStarted and not humansLoaded:
        #Waiting for the other supervisor to be ready
        if objectPlacementOutput.getSFString() == "done":
            getHumans()
            humansLoaded = True
            #Message to indicate that data has correctly been taken
            objectPlacementOutput.setSFString("received")
        
    
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
                #Reset both controller files
                resetControllerFile(0)
                resetControllerFile(1)
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

