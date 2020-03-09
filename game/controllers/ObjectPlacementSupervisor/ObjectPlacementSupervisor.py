"""Object Placing Supervisor Prototype v5
   Written by Robbie Goldman and Alfred Roberts

Features:
 - Places humans and obstacles randomly
 - Will not intersect walls or other objects
 - Will not be within 4 units of bases

Changelog:
 V2:
 - Bases now retrieved from their own group
 - Dynamic obstacles
 - Activity placement
 V3:
 - Waits for main supervisor to call for generation first (prevents double)
 V4:
 - Overhauled to not use walls but rooms instead (will not work with old world files)
 V5:
 - Added identification of adjacent rooms (connected by doors) for future use and relocation
"""

from controller import Supervisor
import random

#Create the instance of the supervisor class
supervisor = Supervisor()

#Get field to output information to
outputField = supervisor.getFromDef("OBJECTPLACER").getField("customData")


def getAllRooms (numberRooms: int) -> list:
    '''Retrieve all the boundaries for the rooms and return the list of minimum and maximum positions'''
    #List to contain all the room boundaries
    rooms = []

    #Iterate for rooms
    for roomNumber in range(0, numberRooms):
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


def getAllAdjacency (roomList: list) -> list:
    '''Returns a 2d array containing boolean values for if those two rooms are connected by a door and not the same'''
    #Empty adjacency array
    adj = []
    #Iterate for rooms
    for roomNumber in range(0, len(roomList)):
        #Empty row
        row = []
        #Iterate for rooms
        for item in range(0, len(roomList)):
            #Add room data
            row.append(False)
        #Add the row to the array
        adj.append(row)

    #Get group node containing doors
    doorGroup = supervisor.getFromDef("DOORGROUP")
    doorNodes = doorGroup.getField("children")
    #Get number of doors
    numberOfDoors = doorNodes.getCount()

    #Iterate through the doors
    for doorId in range(0, numberOfDoors):
        #Get the door node
        door = doorNodes.getMFNode(doorId)
        #List of rooms it connects
        roomIds = []
        #Get the children nodes (room data nodes)
        roomData = door.getField("children")
        #Count the number of room data nodes
        numberOfRooms = roomData.getCount()
        #Iterate for room data nodes
        for room in range(0, numberOfRooms):
            #Get the node
            roomTransform = roomData.getMFNode(room)
            #Retrieve the x translation as an integer (room id)
            roomIds.append(int(roomTransform.getField("translation").getSFVec3f()[0]))

        #If there are at least 2 rooms
        if len(roomIds) > 1:
            #Set the adjacency for the 2 rooms to true
            adj[roomIds[0]][roomIds[1]] = True
            adj[roomIds[1]][roomIds[0]] = True

    #Return the completed adjacency array
    return adj
        
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

    
def getAllObstacles(numberObstacles: int) -> list:
    '''Returns a list of all the obstacles in the world, each obstacle is a 1D array of it's x y and z scale'''
    #List to hold all obstacles
    obstacles = []
    
    #Iterate for obstacles
    for obstacleNumber in range(0, numberObstacles):
        #Obtain the object for the obstacle
        obstacleBoxObj = supervisor.getFromDef("OBSTACLEBOX" + str(obstacleNumber))
        #Get the obstacles scale
        scale = obstacleBoxObj.getField("size").getSFVec3f()
        #Add to list of obstacles
        obstacles.append(scale)
    
    return obstacles
    
    
def getAllBases(numberBases, baseNodes) -> list:
    '''Returns a list of all the bases as a centre position'''
    #List to contain all the bases
    bases = []
    
    #Iterate for the bases
    for i in range(0, numberBases):
        #Get the minimum and maximum position vectors
        minBase = supervisor.getFromDef("base" + str(i) + "Min").getField("translation").getSFVec3f()
        maxBase = supervisor.getFromDef("base" + str(i) + "Max").getField("translation").getSFVec3f()
        #Create the base (midpoint of the min and max: min + (max-min/2))
        base = [((maxBase[0] - minBase[0]) / 2.0) + minBase[0], ((maxBase[2] - minBase[2]) / 2.0) + minBase[2]]
        #Add to list of bases
        bases.append(base)
    
    return bases


def getAllActivities(numActivityBoxes: int, numActivityPads: int) -> list:
    '''Returns a list containing all the boxes and all the pads and a list containing all the scales'''
    #Lists to contain all boxes and pads
    activityObjects = []
    activitySizes = []
    #Which box is connected to which pad
    associations = []

    #Iterate for box IDs
    for boxNum in range(0, numActivityBoxes):
        #Add the box to the list
        activityObjects.append(supervisor.getFromDef("ACT" + str(boxNum)))
        activitySizes.append(supervisor.getFromDef("ACTIVITYBOX" + str(boxNum)).getField("size").getSFVec3f())
        associations.append(boxNum)
        
    #Iterate for pad IDs
    for padNum in range(0, numActivityPads):
        #Add the pad to the list
        activityObjects.append(supervisor.getFromDef("ACT" + str(padNum) + "MAT"))
        activitySizes.append(supervisor.getFromDef("ACTIVITYPAD" + str(padNum)).getField("size").getSFVec3f())
        associations.append(padNum)
        
    #Return the full object list and size list
    return activityObjects, activitySizes, associations
    
    
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

    selectedRoomId = -1
    
    #Not yet ready to be added
    done = False

    #Initial values
    randomX = 0
    randomZ = 0

    #Repeat until a valid position is found (need to limit max objects to make sure this ends)
    '''TODO: Add reject counter to skip adding object if it cannot find a location (if needed)'''
    while not done:

        done = True

        selectedRoomId = validRoomIds[random.randrange(0, len(validRoomIds))]
        selectedRoom = rooms[selectedRoomId]

        roomMin = [selectedRoom[0][0], selectedRoom[0][1]]
        roomMax = [selectedRoom[1][0], selectedRoom[1][1]]

        #Calculate size boundaries
        xMin = int((roomMin[0] * 100) + (radius * 100))
        xMax = int((roomMax[0] * 100) - (radius * 100))
        zMin = int((roomMin[1] * 100) + (radius * 100))
        zMax = int((roomMax[1] * 100) - (radius * 100))

        #If the object is too big for the room
        if xMin >= xMax or zMin >= zMax:
            #Cannot be placed here
            done = False
        else:
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
    return randomX, randomZ, selectedRoomId
    

def setObstaclePositions(obstaclesList: list, obstacleNodes: list, rooms: list, blockedRooms: list) -> list:
    '''Place the obstacles in generated positions and return the placed obstacles'''
    #List to contain all obstacles
    obstacles = []
    #Iterate for each obstacle
    for i in range(len(obstaclesList)):
        #Get each obstacle from children field in the obstacle root node OBSTACLEGROUP
        obstacle = obstacleNodes.getMFNode(i)
        #Get obstacle translation
        obstaclePos = obstacle.getField("translation")
        #Calculate the radius
        radius = ((obstaclesList[i][0] ** 2) + (obstaclesList[i][2] ** 2)) ** 0.50
        #Get random valid position
        x, z, roomNum = generatePosition(radius, rooms, blockedRooms, obstacles)
        y = (obstaclesList[i][1] / 2.0) + 0.05
        #Move obstacle to random position in the building
        obstaclePos.setSFVec3f([x,y,z])
        obstacles.append([[x, z], radius])
    
    #Formatted as: [[xPos, zPos], radius]
    return obstacles


def setActivityPositions(activityItemList: list, activitySizeList: list, activityAssoc: list, rooms: list, unusableRooms: list, unusablePlaces: list) -> list:
    '''Place the activities in generated positions and return the placed items position and scale'''
    #List to contain all activities
    activityItems = []
    #List to contain which room activity parts are in
    roomsUsed = []
    #List position of current object
    itemId = 0
    #Iterate for each obstacle
    for item in activityItemList:
        #Get obstacle translation
        itemPosition = item.getField("translation")
        itemScale = activitySizeList[itemId]
        #Determine the radius of the object
        radius = ((itemScale[0] ** 2) + (itemScale[2] ** 2)) ** 0.50
        #List to contain rooms that cannot be used
        disallowedRooms = []
        #Copy all default data
        for room in unusableRooms:
            disallowedRooms.append(room)
        #Add a room to not allowed if used by another part of the activity
        if len(roomsUsed) > activityAssoc[itemId]:
            disallowedRooms.append(roomsUsed[activityAssoc[itemId]])
        #Get random valid position
        x, z, roomNum = generatePosition(radius, rooms, unusableRooms + disallowedRooms, unusablePlaces + activityItems)
        y = (itemScale[1] / 2.0) + 0.05
        #Add the room number to the list of used rooms
        roomsUsed.append(roomNum)
        #Move activity element to random position in the building
        itemPosition.setSFVec3f([x,y,z])
        activityItems.append([[x, z], radius])
        itemId = itemId + 1
    
    #Formatted as: [[xPos, zPos], radius]
    return activityItems

def setHumanPositions(numberHumans: int, humanNodes: list, rooms: list, unusableRooms: list, unusableSpaces: list) -> list:
    '''Place the humans in generated positions and return the placed humans'''
    #List to contain all humans
    humans = []
    #Iterate for each human
    for i in range(numberHumans):
        #Get each human from children field in the human root node HUMANGROUP
        human = humanNodes.getMFNode(i)
        #Get human translation and radius
        humanPos = human.getField("translation")
        humanRad = human.getField("boundingObject").getSFNode().getField("radius").getSFFloat() + 0.5
        humanY = human.getField("boundingObject").getSFNode().getField("height").getSFFloat()
        #Get random valid position
        x, z, roomNum = generatePosition(humanRad, rooms, unusableRooms, unusableSpaces + humans)
        #Move humans to random positions in the building
        humanPos.setSFVec3f([x,humanY,z])
        humans.append([[x, z], humanRad])
    
    #Returns the placed humans as: [[xPosition, zPosition], radius]
    return humans

def performGeneration ():
    '''Generate a position for all the objects and place them in the world'''
    
    #Get group node containing room boundaries
    roomGroup = supervisor.getFromDef("ROOMBOUNDS")
    roomNodes = roomGroup.getField("children")
    #Get number of rooms
    numberOfRooms = roomNodes.getCount()
    
    #Get group node containing humans 
    humanGroup = supervisor.getFromDef("HUMANGROUP")
    humanNodes = humanGroup.getField("children")
    #Get number of humans in map
    numberOfHumans = humanNodes.getCount()

    #Get group node containing bases
    baseGroup = supervisor.getFromDef("BASEGROUP")
    baseNodes = baseGroup.getField("children")
    #Get number of bases in map (divide by three as there is a min and max node for each too)
    numberOfBases = int(baseNodes.getCount() / 3)

    #Get group node containing obstacles 
    obstacleGroup = supervisor.getFromDef("OBSTACLEGROUP")
    obstacleNodes = obstacleGroup.getField("children")
    #Get number of obstacles in map
    numberOfObstacles = obstacleNodes.getCount()

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

    #Get all the room boundaries
    allRooms = getAllRooms(numberOfRooms)
    #Get all the obstacles
    allObstacles = getAllObstacles(numberOfObstacles)
    #Get all the activity items
    allActivityItems, allActivitySizes, activityAssoc = getAllActivities(numberOfActivityBoxes, numberOfActivityPads)
    #Get all the base positions
    allBases = getAllBases(numberOfBases, baseNodes)
    
    #List of all rooms that cannot be used (the ones containing bases at the time of writing)
    unusableRooms = []

    #Iterate the bases
    for base in allBases:
        #Which room index that base is in
        index = determineRoom(allRooms, base)
        #If a room was found
        if index != -1:
            #Add that index to the list of unusable rooms
            unusableRooms.append(index)

    unusablePlaces = []
    
    #Place all the obstacles
    finalObstacles = setObstaclePositions(allObstacles, obstacleNodes, allRooms, unusableRooms)
    #Add obstacles to the unusables list
    unusablePlaces = unusablePlaces + finalObstacles

    #Place all the activities
    finalActivities = setActivityPositions(allActivityItems, allActivitySizes, activityAssoc, allRooms, unusableRooms, unusablePlaces)
    #Add activities to the unusables list
    unusablePlaces = unusablePlaces + finalActivities
    
    #Place all the humans
    finalHumans = setHumanPositions(numberOfHumans, humanNodes, allRooms, unusableRooms, unusablePlaces)
    #Add humans to the unusables list
    unusablePlaces = unusablePlaces + finalHumans

    #Send signal to say that items have been placed
    outputField.setSFString("done")


#Check if a generation is being called
if outputField.getSFString() == "startGen":
    #Generate positions
    performGeneration()
    #Generation done - terminates loop and script
    notGenerated = False
