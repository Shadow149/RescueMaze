"""Relocate Position Calculator Prototype v2
   Written by Robbie Goldman

Features:
 - Selects a random place for a relocate
 - Will not be in the room the robot is currently in
 - Will not be in the same room as the other robot
 - Will not be inside any of the other map features (walls, obstacles, activities, bases)

Changelog:
 - Fixed rounding issue with boundaries

To use:
 import RelocateCalculator
 [xPos, zPos] = RelocateCalculator(supervisor)
"""

import random

def getAllRooms (supervisor) -> list:
    '''Retrieve all the boundaries for the rooms and return the list of minimum and maximum positions'''
    #List to contain all the room boundaries
    rooms = []

    #Get group node containing room boundaries
    roomGroup = supervisor.getFromDef("ROOMBOUNDS")
    roomNodes = roomGroup.getField("children")
    #Get number of rooms
    numberOfRooms = roomNodes.getCount()

    #Iterate for rooms
    for roomNumber in range(0, numberOfRooms):
        #Get max and min nodes
        minNode = supervisor.getFromDef("room" + str(roomNumber) + "Min")
        maxNode = supervisor.getFromDef("room" + str(roomNumber) + "Max")
        #Get the positions from the nodes
        minPos = minNode.getField("translation").getSFVec3f()
        maxPos = maxNode.getField("translation").getSFVec3f()
        #Append the max and min positions to the room data
        rooms.append([[minPos[0], minPos[2]], [maxPos[0], maxPos[2]]])

    #Return the list of the rooms
    return rooms


def determineRoom(roomList: list, objectPosition: list) -> int:
    '''Determine the room index that a position in inside of'''
    #Id to determine which room is being looked at
    roomId = 0

    #Iterate through the rooms
    for room in roomList:
        #Get the maximum and minimum position
        minPos = room[0]
        maxPos = room[1]
        #If it is between the x positions of the boundaries
        if minPos[0] <= objectPosition[0] and maxPos[0] >= objectPosition[0]:
            #If it is between the y positions of the boundaries
            if minPos[1] <= objectPosition[1] and maxPos[1] >= objectPosition[1]:
                #This is the room it is in
                return roomId
        #Increment room counter
        roomId = roomId + 1

    #It was not found so return -1
    return -1


def getAllObstacles(supervisor) -> list:
    '''Returns a list of all the obstacles in the world, each obstacle is a 1D array of it's x y and z scale'''
    #List to hold all obstacles
    obstacles = []

    #Get group node containing obstacles 
    obstacleGroup = supervisor.getFromDef("OBSTACLEGROUP")
    obstacleNodes = obstacleGroup.getField("children")
    #Get number of obstacles in map
    numberOfObstacles = obstacleNodes.getCount()
    
    #Iterate for obstacles
    for obstacleNumber in range(0, numberOfObstacles):
        #Get the object
        obstacleObj = obstacleNodes.getMFNode(obstacleNumber)
        #Obtain the object for the obstacle
        obstacleBoxObj = obstacleObj.getField("boundingObject").getSFNode()
        #Get the obstacles scale
        scale = obstacleBoxObj.getField("size").getSFVec3f()
        #Get the obstacles radius
        radius = ((scale[0] ** 2) + (scale[2] ** 2)) ** 0.5
        #Get the obstacles position
        obstaclePos = obstacleObj.getField("translation").getSFVec3f()
        #Add to list of obstacles
        obstacles.append([[obstaclePos[0], obstaclePos[2]], radius])
    
    return obstacles
    
    
def getAllBases(supervisor) -> list:
    '''Returns a list of all the bases as a centre position'''
    #List to contain all the bases
    bases = []

    #Get group node containing bases
    baseGroup = supervisor.getFromDef("BASEGROUP")
    baseNodes = baseGroup.getField("children")
    #Get number of bases in map (divide by three as there is a min and max node for each too)
    numberOfBases = int(baseNodes.getCount() / 3)
    
    #Iterate for the bases
    for i in range(0, numberOfBases):
        #Get the minimum and maximum position vectors
        minBase = supervisor.getFromDef("base" + str(i) + "Min").getField("translation").getSFVec3f()
        maxBase = supervisor.getFromDef("base" + str(i) + "Max").getField("translation").getSFVec3f()
        #Create the base (midpoint of the min and max: min + (max-min/2)) and the radius
        base = [[((maxBase[0] - minBase[0]) / 2.0) + minBase[0], ((maxBase[2] - minBase[2]) / 2.0) + minBase[2]], (maxBase[0] - minBase[0]) / 2]
        #Add to list of bases
        bases.append(base)
    
    return bases


def getAllActivities(supervisor) -> list:
    '''Returns a list containing all the boxes and all the pads and a list containing all the scales'''
    #Lists to contain all boxes and pads
    activities = []

    #Get group node containing activity boxes
    activityBoxGroup = supervisor.getFromDef("ACTOBJECTSGROUP")
    activityBoxNodes = activityBoxGroup.getField("children")
    #Get number of activity boxes in map
    numberOfActivityBoxes = activityBoxNodes.getCount()

    #Get group node containing activity pads
    activityPadGroup = supervisor.getFromDef("ACTMATGROUP")
    activityPadNodes = activityPadGroup.getField("children")
    #Get number of activity boxes in map
    numberOfActivityPads = activityPadNodes.getCount()

    #Iterate for box IDs
    for boxNum in range(0, numberOfActivityBoxes):
        #Get the box and the bounding object
        boxObject = activityBoxNodes.getMFNode(boxNum)
        boxPos = boxObject.getField("translation").getSFVec3f()
        boxBounds = boxObject.getField("boundingObject").getSFNode()
        boxScale = boxBounds.getField("size").getSFVec3f()
        #Calculate the radius
        radius = ((boxScale[0] ** 2) + (boxScale[2] ** 2)) ** 0.5
        #Add the box to the list
        activities.append([[boxPos[0], boxPos[2]], radius])
        
    #Iterate for pad IDs
    for padNum in range(0, numberOfActivityPads):
        #Get the pad and the bounding object
        padObject = activityPadNodes.getMFNode(boxNum)
        padPos = padObject.getField("translation").getSFVec3f()
        padBounds = padObject.getField("boundingObject").getSFNode()
        padScale = padBounds.getField("size").getSFVec3f()
        #Calculate the radius
        radius = ((padScale[0] ** 2) + (padScale[2] ** 2)) ** 0.5
        #Add the box to the list
        activities.append([[padPos[0], padPos[2]], radius])
        
    #Return the full object list and size list
    return activities


def getAllHumans(supervisor) -> list:
    '''Returns a list of all human objects'''
    #Get group node containing humans 
    humanGroup = supervisor.getFromDef("HUMANGROUP")
    humanNodes = humanGroup.getField("children")
    #Get number of humans in map
    numberOfHumans = humanNodes.getCount()

    humans = []

    #Iterate humans
    for humanNum in range(0, numberOfHumans):
        #Get the human node
        human = humanNodes.getMFNode(humanNum)
        #Get position and calculate radius
        humanPos = human.getField("translation").getSFVec3f()
        humanRad = human.getField("boundingObject").getSFNode().getField("radius").getSFFloat() + 0.5
        #Add the human to the list
        humans.append([[humanPos[0], humanPos[2]], humanRad])

    #Return full list of all humans
    return humans


def getRobotPositions(supervisor) -> list:
    '''Get the positions of both robots and return them as a list'''
    robot0Pos = supervisor.getFromDef("ROBOT0").getField("translation").getSFVec3f()
    robot1Pos = supervisor.getFromDef("ROBOT1").getField("translation").getSFVec3f()
    return [robot0Pos, robot1Pos]


def generatePosition(radius: int, rooms: list, blockedRooms: list, usedSpaces: list):
    '''Returns a random x and z position within the area, that is valid'''
    #Round the radius to 2dp
    radius = round(float(radius), 2)

    #List to contain rooms that may be generated
    validRoomIds = []
    #Iterate through all the rooms
    for index in range(0, len(rooms)):
        #If the room is allowed then add it to the list
        if index not in blockedRooms:
            validRoomIds.append(index)

    selectedRoom = -1
    
    #Not yet ready to be added
    done = False

    #Repeat until a valid position is found (need to limit max objects to make sure this ends
    while not done:

        done = True

        selectedRoom = rooms[validRoomIds[random.randrange(0, len(validRoomIds))]]

        roomMin = [selectedRoom[0][0], selectedRoom[0][1]]
        roomMax = [selectedRoom[1][0], selectedRoom[1][1]]

        #Calculate size boundaries
        xMin = int((roomMin[0] * 100) + (radius * 100))
        xMax = int((roomMax[0] * 100) - (radius * 100))
        zMin = int((roomMin[1] * 100) + (radius * 100))
        zMax = int((roomMax[1] * 100) - (radius * 100))
        
        #Get a random x and z position between min and max (with offset for radius)
        randomX = random.randrange(xMin, xMax) / 100.0
        randomZ = random.randrange(zMin, zMax) / 100.0
        
        #Iterate through the placed items
        for item in usedSpaces:
            #Get the distance to the item
            distance = (((randomX - item[0][0]) ** 2) + ((randomZ - item[0][1]) ** 2)) ** 0.5
            #If the distance is less than the two radii added together
            if distance <= radius + item[1]:
                #It intersects a placed object and cannot be placed here
                done = False
    
    #Returns the correct coordinates
    return randomX, randomZ, selectedRoom


def generateRelocatePosition(supervisor) -> list:
    '''Generate a random position to relocate a robot to'''
    #Get all the room data
    rooms = getAllRooms(supervisor)
    #Get all the obstacles in the rooms
    unusable = getAllObstacles(supervisor)
    unusable = unusable + getAllActivities(supervisor)
    unusable = unusable + getAllBases(supervisor)
    unusable = unusable + getAllHumans(supervisor)
    #Calculate the robot positions
    robotPos = getRobotPositions(supervisor)
    #List to contain rooms that are not allowed
    unusableRooms = []
    #Iterate robots
    for pos in robotPos:
        #Get the id of the position
        roomId = determineRoom(rooms, pos)
        #If it is a room
        if roomId != -1:
            #Add to the unusable list
            unusableRooms.append(roomId)

    x, z, roomId = generatePosition(1, rooms, unusableRooms, unusable)
    return [x, z]
