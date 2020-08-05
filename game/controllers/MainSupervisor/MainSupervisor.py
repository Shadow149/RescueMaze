"""Supervisor Controller Prototype v1
   Written by Robbie Goldman and Alfred Roberts
"""

from controller import Supervisor
import os
import random
import struct
import math
import datetime


# Create the instance of the supervisor class
supervisor = Supervisor()

# Get this supervisor node - so that it can be rest when game restarts
mainSupervisor = supervisor.getFromDef("MAINSUPERVISOR")

maxTimeMinute = 8
# Maximum time for a match
maxTime = maxTimeMinute * 60

DEFAULT_MAX_VELOCITY = 6.28


class Queue:
    #Simple queue data structure 
    def __init__(self):
        self.queue = []

    def enqueue(self, data):
        return self.queue.append(data)

    def dequeue(self):
        return self.queue.pop(0)

    def peek(self):
        return self.queue[0]

    def is_empty(self):
        return len(self.queue) == 0


class RobotHistory(Queue):
    #Robot history class inheriting a queue structure
    def __init__(self):
        super().__init__()
        #master history to store all events without dequeues
        self.master_history = []

    def enqueue(self, data):
        #update master history when an event happens
        self.update_master_history(data)

        if len(self.queue) > 8:
            self.dequeue()
        
        return self.queue.append(data)

    def update_master_history(self, data):
        #Get time
        time = int(maxTime - timeElapsed)
        minute = str(datetime.timedelta(seconds=time))[2:]
        #update list with data in format [game time, event data]
        record = [minute, data]
        self.master_history.append(record)


class Robot:
    '''Robot object to hold values whether its in a base or holding a human'''

    def __init__(self, node=None):
        '''Initialises the in a base, has a human loaded and score values'''

        #webots node
        self.wb_node = node

        self.wb_translationField = self.wb_node.getField('translation')
        self.wb_rotationField = self.wb_node.getField('rotation')

        self.inCheckpoint = True
        self.inSwamp = True

        self.history = RobotHistory()

        self._score = 0

        self.robot_timeStopped = 0
        self.stopped = False
        self.stoppedTime = None

        self.message = []

        self.lastVisitedCheckPointPosition = []

        self.visitedCheckpoints = []

        self.startingTile = None

        self.inSimulation = True

        self.name = "NO_TEAM_NAME"


    @property
    def position(self) -> list:
        return self.wb_translationField.getSFVec3f()

    @position.setter
    def position(self, pos: list) -> None:
        self.wb_translationField.setSFVec3f(pos)

    @property
    def rotation(self) -> list:
        return self.wb_rotationField.getSFRotation()

    @rotation.setter
    def rotation(self, pos: list) -> None:
        self.wb_rotationField.setSFRotation(pos)

    def setMaxVelocity(self, vel: float) -> None:
        self.wb_node.getField('max_velocity').setSFFloat(vel)

    def _isStopped(self) -> bool:
        vel = self.wb_node.getVelocity()
        return abs(vel[0]) < 0.01 and abs(vel[1]) < 0.01 and abs(vel[2]) < 0.01
        

    def timeStopped(self) -> float:
        self.stopped = self._isStopped()

        # if it isn't stopped yet
        if self.stoppedTime == None:
            if self.stopped:
                # get time the robot stopped
                self.stoppedTime = supervisor.getTime()
        else:
            # if its stopped
            if self.stopped:
                # get current time
                currentTime = supervisor.getTime()
                # calculate the time the robot stopped
                self.robot_timeStopped = currentTime - self.stoppedTime
            else:
                # if it's no longer stopped, reset variables
                self.stoppedTime = None
                self.robot_timeStopped = 0

        return self.robot_timeStopped

    def increaseScore(self, score: int) -> None:
        if self._score + score < 0:
            self._score = 0
        else:
            self._score += score

    def getScore(self) -> int:
        return self._score
    
    def get_log_str(self):
        #Create a string of all events that the robot has done
        history = self.history.master_history
        log_str = ""
        for event in history:
            log_str += str(event[0]) + " " + event[1] + "\n"
            
        return log_str


class Human():
    '''Human object holding the boundaries'''

    def __init__(self, node, ap: int, vtype: str, score: int):
        '''Initialises the radius and position of the human'''

        self.wb_node = node

        self.wb_translationField = self.wb_node.getField('translation')

        self.wb_rotationField = self.wb_node.getField('rotation')

        self.wb_typeField = self.wb_node.getField('type')
        self.wb_foundField = self.wb_node.getField('found')

        self.arrayPosition = ap
        self.scoreWorth = score
        self.radius = 0.06
        self._victim_type = vtype

        self.simple_victim_type = self.get_simple_victim_type()

    @property
    def position(self) -> list:
        return self.wb_translationField.getSFVec3f()

    @position.setter
    def position(self, pos: list) -> None:
        self.wb_translationField.setSFVec3f(pos)

    @property
    def rotation(self) -> list:
        return self.wb_rotationField.getSFRotation()

    @rotation.setter
    def rotation(self, pos: list) -> None:
        self.wb_rotationField.setSFRotation(pos)

    @property
    def victim_type(self) -> list:
        return self.wb_typeField.getSFString()

    @victim_type.setter
    def victim_type(self, v_type: str):
        self.wb_typeField.setSFString(v_type)

    @property
    def identified(self) -> list:
        return self.wb_foundField.getSFBool()

    @identified.setter
    def identified(self, idfy: int):
        self.wb_foundField.setSFBool(idfy)

    def get_simple_victim_type(self):
        # Get victim type via proto node
        if self._victim_type == 'harmed':
            return 'H'
        elif self._victim_type == 'unharmed':
            return 'U'
        elif self._victim_type == 'stable':
            return 'S'
        elif self._victim_type == 'heat': # Temperature victim
            return 'T'
        else:
            return self._victim_type

    def checkPosition(self, pos: list) -> bool:
        '''Check if a position is near an object, based on the min_dist value'''
        # Get distance from the object to the passed position using manhattan distance for speed
        # TODO Check if we want to use euclidian or manhattan distance -- currently manhattan
        distance = math.sqrt(((self.position[0] - pos[0])**2) + ((self.position[2] - pos[2])**2))
        return distance <= self.radius

    def onSameSide(self, pos: list) -> bool:
        #Get side the victim pointing at

        #0 1 0 -pi/2 -> X axis
        #0 1 0 pi/2 -> -X axis
        #0 1 0 pi -> Z axis
        #0 1 0 0 -> -Z axis

        rot = self.rotation[3]
        rot = round(rot, 2)

        if rot == -1.57:
            #X axis
            robot_x = pos[0]
            if robot_x > self.position[0]:
                return True
        elif rot == 1.57:
            #-X axis
            robot_x = pos[0]
            if robot_x < self.position[0]:
                return True
        elif rot == 3.14:
            #Z axis
            robot_z = pos[2]
            if robot_z > self.position[2]:
                return True
        elif rot == 0:
            #-Z axis
            robot_z = pos[2]
            if robot_z < self.position[2]:
                return True

        return False
        



class Tile():
    '''Tile object holding the boundaries'''

    def __init__(self, min: list, max: list, center: list):
        '''Initialize the maximum and minimum corners for the tile'''
        self.min = min
        self.max = max
        self.center = center

    def checkPosition(self, pos: list) -> bool:
        '''Check if a position is in this checkpoint'''
        # If the x position is within the bounds
        if pos[0] >= self.min[0] and pos[0] <= self.max[0]:
            # if the z position is within the bounds
            if pos[2] >= self.min[1] and pos[2] <= self.max[1]:
                # It is in this checkpoint
                return True

        # It is not in this checkpoint
        return False


class Checkpoint(Tile):
    '''Checkpoint object holding the boundaries'''

    def __init__(self, min: list, max: list, center=None):
        super().__init__(min, max, center)


class Swamp(Tile):
    '''Swamp object holding the boundaries'''

    def __init__(self, min: list, max: list, center=None):
        super().__init__(min, max, center)


class StartTile(Tile):
    '''StartTile object holding the boundaries'''

    def __init__(self, min: list, max: list, center=None):
        super().__init__(min, max, center)


def getPath(number: int) -> str:
    '''Get the path to the correct controller'''
    # The current path to this python file
    filePath = os.path.dirname(os.path.abspath(__file__))

    filePath = filePath.replace('\\', '/')

    # Split into parts on \
    pathParts = filePath.split("/")

    filePath = ""
    # Add all parts back together
    for part in pathParts:
        # Except the last one
        if part != pathParts[-1]:
            # Concatenate with / not \ (prevents issues with escape characters)
            filePath = filePath + part + "/"

    # Controller number part added
    if number == 0:
        filePath = filePath + "robot0Controller/robot0Controller.py"
    elif number == 1:
        filePath = filePath + "robot1Controller/robot1Controller.py"
    else:
        # Returns none if id was not valid
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

    # If there is a name in the file
    if "RobotName:" in fileData:
        # Find the name
        name = fileData[fileData.index("RobotName:") + 10:]
        name = name.split("\n")[0]
        # Return data with a name
        return name, number

    # Return data without a name
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
    supervisor.wwiSendText("historyUpdate" + "," + ",".join(robot0Obj.history.queue))

def getHumans(humans, numberOfHumans):
    '''Get humans in simulation'''
    humanNodes = supervisor.getFromDef('HUMANGROUP').getField("children")
    # Iterate for each human
    for i in range(numberOfHumans):
        # Get each human from children field in the human root node HUMANGROUP
        human = humanNodes.getMFNode(i)
        
        victimType = human.getField('type').getSFString()
        scoreWorth = human.getField('scoreWorth').getSFInt32()

        # Create Human Object from human position
        humanObj = Human(human, i, victimType, scoreWorth)
        humans.append(humanObj)

def getSwamps(swamps, numberOfSwamps):
    '''Get swamps in simulation'''
    # Iterate for each swamp
    for i in range(numberOfSwamps):
        # Get the swamp minimum node and translation
        swampMin = supervisor.getFromDef("swamp" + str(i) + "min")
        minPos = swampMin.getField("translation")
        # Get maximum node and translation
        swampMax = supervisor.getFromDef("swamp" + str(i) + "max")
        maxPos = swampMax.getField("translation")
        # Get the vector positions
        minPos = minPos.getSFVec3f()
        maxPos = maxPos.getSFVec3f()

        centerPos = [(maxPos[0]+minPos[0])/2,maxPos[1],(maxPos[2]+minPos[2])/2]
        # Create a swamp object using the min and max (x,z)
        swampObj = Checkpoint([minPos[0], minPos[2]], [maxPos[0], maxPos[2]], centerPos)
        swamps.append(swampObj)

def getCheckpoints(checkpoints, numberOfCheckpoints):
    '''Get checkpoints in simulation'''
    # Iterate for each checkpoint
    for i in range(numberOfCheckpoints):
        # Get the checkpoint minimum node and translation
        checkpointMin = supervisor.getFromDef("checkpoint" + str(i) + "min")
        minPos = checkpointMin.getField("translation")
        # Get maximum node and translation
        checkpointMax = supervisor.getFromDef("checkpoint" + str(i) + "max")
        maxPos = checkpointMax.getField("translation")
        # Get the vector positions
        minPos = minPos.getSFVec3f()
        maxPos = maxPos.getSFVec3f()

        centerPos = [(maxPos[0]+minPos[0])/2,maxPos[1],(maxPos[2]+minPos[2])/2]
        # Create a checkpoint object using the min and max (x,z)
        checkpointObj = Checkpoint([minPos[0], minPos[2]], [maxPos[0], maxPos[2]], centerPos)
        checkpoints.append(checkpointObj)

def resetVictimsTextures():
    # Iterate for each victim
    for i in range(numberOfHumans):
        humans[i].identified = False


def relocate(robotObj):
    '''Relocate robot to last visited checkpoint'''
    # Get last checkpoint visited
    relocatePosition = robotObj.lastVisitedCheckPointPosition

    # Set position of robot
    robotObj.position = [relocatePosition[0], -0.03, relocatePosition[2]]
    robotObj.rotation = [0,1,0,0]

    # Update history with event
    robotObj.history.enqueue("Lack of Progress - 5")
    robotObj.history.enqueue("Relocating to checkpoint")
    robotObj.increaseScore(-5)
    updateHistory()

def robot_quit(robotObj, num, manualExit):
    '''Quit robot from simulation'''
    # Quit robot if present
    if robotObj.inSimulation:
        # Remove webots node
        robotObj.wb_node.remove()
        robotObj.inSimulation = False
        # Send message to robot window to update quit button
        supervisor.wwiSendText("robotNotInSimulation"+str(num))
        # Update history event whether its manual or via exit message
        if manualExit:
            robotObj.history.enqueue("Manual Exit")
        else:
            robotObj.history.enqueue("Successful Exit")

def add_robot():
    '''Add robot via .wbo file'''
    global robot0
    # If robot not present
    if robot0 == None:
        # Get relative path
        filePath = os.path.dirname(os.path.abspath(__file__))
        filePath = filePath.replace('\\', '/')
        
        # Get webots root
        root = supervisor.getRoot()
        root_children_field = root.getField('children')
        # Get .wbo file to insert into world
        root_children_field.importMFNode(12,filePath + '/../../nodes/robot0.wbo')
        # Update robot0 variable
        robot0 = supervisor.getFromDef("ROBOT0")
        # Update robot window to say robot is in simulation
        supervisor.wwiSendText("robotInSimulation0")

def create_log_str():
    '''Create log text for log file'''
    # Get robot events
    r0_str = robot0Obj.get_log_str()
    
    # Create log text
    log_str = ""
    log_str += "MAX_GAME_DURATION: "+str(maxTimeMinute)+":00\n"
    log_str += "ROBOT_0_SCORE: "+str(robot0Obj.getScore())+"\n"
    log_str += "\n"
    log_str += "ROBOT_0: "+str(robot0Obj.name)+"\n"
    log_str += r0_str
    log_str += "\n"
    
    return log_str

def write_log():
    '''Write log file'''
    # Get log text
    log_str = create_log_str()
    # Get relative path to logs dir
    filePath = os.path.dirname(os.path.abspath(__file__))
    filePath = filePath.replace('\\', '/')
    filePath = filePath + "/../../logs/"
    
    # Create file name using date and time
    file_date = datetime.datetime.now()
    logFileName = file_date.strftime("log %m-%d-%y %H,%M,%S")
    
    filePath += logFileName + ".txt"

    try:
        # Write file
        logsFile = open(filePath, "w")
        logsFile.write(log_str)
        logsFile.close()
    except:
        # If write file fails, most likely due to missing logs dir
        print("Couldn't write log file, no log directory ./game/logs")

def set_robot_start_pos():
    '''Set robot starting position'''
    # Get the starting tile minimum node and translation
    starting_PointMin = supervisor.getFromDef("start0min")
    starting_minPos = starting_PointMin.getField("translation")

    # Get maximum node and translation
    starting_PointMax = supervisor.getFromDef("start0max")
    starting_maxPos = starting_PointMax.getField("translation")

    # Get the vector positons
    starting_minPos = starting_minPos.getSFVec3f()
    starting_maxPos = starting_maxPos.getSFVec3f()
    starting_centerPos = [(starting_maxPos[0]+starting_minPos[0])/2,starting_maxPos[1],(starting_maxPos[2]+starting_minPos[2])/2]

    startingTileObj = StartTile([starting_minPos[0], starting_minPos[2]], [starting_maxPos[0], starting_maxPos[2]], starting_centerPos)

    robot0Obj.startingTile = startingTileObj
    robot0Obj.lastVisitedCheckPointPosition = startingTileObj.center
    robot0Obj.visitedCheckpoints.append(startingTileObj.center)

    robot0Obj.position = [startingTileObj.center[0], startingTileObj.center[1], startingTileObj.center[2]]

# -------------------------------
# CODED LOADED BEFORE GAME STARTS

# Empty list to contain checkpoints
checkpoints = []
# Empty list to contain swamps
swamps = []
# Global empty list to contain human objects
humans = []

# Get number of humans in map
numberOfHumans = supervisor.getFromDef('HUMANGROUP').getField("children").getCount()

# Get number of checkpoints in map
numberOfCheckpoints = supervisor.getFromDef('CHECKPOINTBOUNDS').getField('children').getCount()

# Get number of swamps in map
numberOfSwamps = supervisor.getFromDef('SWAMPBOUNDS').getField('children').getCount()

#get swamps in world
getSwamps(swamps, numberOfSwamps)

#get checkpoints in world
getCheckpoints(checkpoints, numberOfCheckpoints)

#get humans in world
getHumans(humans, numberOfHumans)

# Not currently running the match
currentlyRunning = False
previousRunState = False

# The game has not yet started
gameStarted = False

# Get the robot nodes by their DEF names
robot0 = supervisor.getFromDef("ROBOT0")

# Add robot into world
add_robot()

# Init both robots as objects to hold their info
robot0Obj = Robot(robot0)

# The simulation is running
simulationRunning = True
finished = False

# Reset the controllers
resetControllerFile(0)

# How long the game has been running for
timeElapsed = 0
lastTime = -1

# Send message to robot window to perform setup
supervisor.wwiSendText("startup")

# For checking the first update with the game running
first = True

receiver = supervisor.getReceiver('receiver')
receiver.enable(32)

# Set robots starting position in world
set_robot_start_pos()

# -------------------------------

# Until the match ends (also while paused)
while simulationRunning:

    r0 = False
    r0s = False

    # The first frame of the game running only
    if first and currentlyRunning:
        # Restart controller code
        robot0.restartController()
        first = False

    # Test if the robots are in checkpoints
    for checkpoint in checkpoints:
        if robot0Obj.inSimulation:
            # Check position of checkpoint with the robots position
            if checkpoint.checkPosition(robot0Obj.position):
                r0 = True
                # Update the robot's last visited position 
                robot0Obj.lastVisitedCheckPointPosition = checkpoint.center

                alreadyVisited = False

                # Dont update if checkpoint is already visited
                # TODO could change this to edit webots node to reduce compute time
                if len(robot0Obj.visitedCheckpoints) > 0:
                    for visitedCheckpoint in robot0Obj.visitedCheckpoints:
                        if visitedCheckpoint == checkpoint.center:
                            alreadyVisited = True

                # Update robot's points and history
                if not alreadyVisited:
                    robot0Obj.visitedCheckpoints.append(checkpoint.center)
                    robot0Obj.increaseScore(10)
                    robot0Obj.history.enqueue("Found checkpoint  +10")
                    updateHistory()

    # Print when robot0 enters or exits a checkpoint
    # Not really needed
    if robot0Obj.inSimulation:
        if robot0Obj.inCheckpoint != r0:
            robot0Obj.inCheckpoint = r0
            if robot0Obj.inCheckpoint:
                print("Robot 0 entered a checkpoint")
            else:
                print("Robot 0 exited a checkpoint")

    # Check if the robots are in swamps
    for swamp in swamps:
        if robot0Obj.inSimulation:
            if swamp.checkPosition(robot0Obj.position):
                r0s = True

    # Check if robot is in swamp
    if robot0Obj.inSimulation:
        if robot0Obj.inSwamp != r0s:
            robot0Obj.inSwamp = r0s
            if robot0Obj.inSwamp:
                # Cap the robot's velocity to 2
                robot0Obj.setMaxVelocity(2)
                # Update history
                robot0Obj.history.enqueue("Entered swamp")
                updateHistory()
            else:
                # If not in swamp, reset max velocity to default
                robot0Obj.setMaxVelocity(DEFAULT_MAX_VELOCITY)

    # If receiver has got a message
    if receiver.getQueueLength() > 0:
        # Get receiver data
        receivedData = receiver.getData()
        # Unpack data
        tup = struct.unpack('i i c', receivedData)

        # Get data in format (est. x position, est. z position, est. victim type)
        x = tup[0]
        z = tup[1]

        estimated_victim_position = (x / 100, 0, z / 100)
        
        victimType = tup[2].decode("utf-8")


        if robot0Obj.inSimulation:
            # Store data recieved
            robot0Obj.message = [estimated_victim_position, victimType]

        receiver.nextPacket()

    if robot0Obj.inSimulation:
        # If data sent to receiver
        if robot0Obj.message != []:
            
            r0_exitmessage = robot0Obj.message[1]
            
            # If exit message is correct
            if r0_exitmessage == 'E':

                robot0Obj.message = []
                
                # Check robot position is on starting tile
                if robot0Obj.startingTile.checkPosition(robot0Obj.position):
                    
                    # Update score and history
                    robot_quit(robot0Obj, 0, False)
                    updateHistory()

                    robot0Obj.increaseScore(10)
                    robot0Obj.increaseScore(int(robot0Obj.getScore() * 0.1))


    if robot0Obj.inSimulation:
        # If robot stopped for 3 seconds
        if robot0Obj.timeStopped() >= 3:

            # If messaged sent
            if robot0Obj.message != []:
                
                # Get estimated values
                r0_est_vic_pos = robot0Obj.message[0]
                r0_est_vic_type = robot0Obj.message[1]
                robot0Obj.message = []

                # For each human
                # TODO optimise
                for i, h in enumerate(humans):
                    # If not already identified
                    if not h.identified:
                        # Check if in range
                        if h.checkPosition(robot0Obj.position):
                            # Check if estimated position is in range
                            if h.checkPosition(r0_est_vic_pos):
                                # If robot on same side
                                if h.onSameSide(robot0Obj.position):
                                    
                                    # Get points scored depending on the type of victim
                                    pointsScored = h.scoreWorth

                                    # Update score and history
                                    if r0_est_vic_type.lower() == h.simple_victim_type.lower():
                                        robot0Obj.history.enqueue("Successful Victim Type Correct Bonus  + 10")
                                        pointsScored += 10

                                    robot0Obj.history.enqueue("Successful Victim Identification " + " +" + str(h.scoreWorth))
                                    robot0Obj.increaseScore(pointsScored)

                                    h.identified = True
                                    updateHistory()
                            else:
                                robot0Obj.history.enqueue("Misidentification of victim  - 5")
                                robot0Obj.increaseScore(-5)

                                updateHistory()

    if robot0Obj.inSimulation:
        # Relocate robot if stationary for 20 sec
        if robot0Obj.timeStopped() >= 20:
            relocate(robot0Obj)
            robot0Obj.robot_timeStopped = 0
            robot0Obj.stopped = False
            robot0Obj.stoppedTime = None

    # If the running state changes
    if previousRunState != currentlyRunning:
        # Update the value and #print
        previousRunState = currentlyRunning

    # Get the message in from the robot window(if there is one)
    message = supervisor.wwiReceiveText()
    # If there is a message
    if message != "":
        # split into parts
        parts = message.split(",")
        # If there are parts
        if len(parts) > 0:
            if parts[0] == "run":
                # Start running the match
                currentlyRunning = True
                lastTime = supervisor.getTime()
                gameStarted = True
            if parts[0] == "pause":
                # Pause the match
                currentlyRunning = False
            if parts[0] == "reset":
                # Reset both controller files
                resetControllerFile(0)
                resetVictimsTextures()
                
                # Reset the simulation
                supervisor.simulationReset()
                simulationRunning = False
                finished = True
                # Restart this supervisor
                mainSupervisor.restartController()

            if parts[0] == "robot0File":
                # Load the robot controller
                if not gameStarted:
                    data = message.split(",", 1)
                    if len(data) > 1:
                        name, id = createController(0, data[1])
                        if name != None:
                            robot0Obj.name = name
                        assignController(id, name)
                else:
                    print("Please choose controllers before simulation starts.")

            if parts[0] == "robot0Unload":
                # Unload the robot 0 controller
                if not gameStarted:
                    resetController(0)

            if parts[0] == 'relocate':
                data = message.split(",", 1)
                if len(data) > 1:
                    if int(data[1]) == 0:
                        relocate(robot0Obj)

            if parts[0] == 'quit':
                data = message.split(",", 1)
                if len(data) > 1:
                    if int(data[1]) == 0:
                        if gameStarted:
                            robot_quit(robot0Obj, 0, True)
                    updateHistory()

    # Send the update information to the robot window
    supervisor.wwiSendText("update," + str(robot0Obj.getScore()) + "," + str(timeElapsed))

    # If the time is up
    if timeElapsed >= maxTime:
        finished = True
        supervisor.wwiSendText("ended")

    # If the match is running
    if currentlyRunning and not finished:
        # Get the time since the last frame
        frameTime = supervisor.getTime() - lastTime
        # Add to the elapsed time
        timeElapsed = timeElapsed + frameTime
        # Get the current time
        lastTime = supervisor.getTime()
        # Step the simulation on
        step = supervisor.step(32)
        # If the simulation is terminated or the time is up
        if step == -1:
            # Stop simulating
            simulationRunning = False
            finished = True
            
    if not simulationRunning and timeElapsed > 0:
        #write log for game if the game ran for more than 0 seconds
        write_log()
        
