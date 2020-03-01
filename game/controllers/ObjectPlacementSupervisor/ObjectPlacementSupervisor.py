"""Object Placing Supervisor Prototype v3
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
"""

from controller import Supervisor
import random

#Create the instance of the supervisor class
supervisor = Supervisor()

#Get field to output information to
outputField = supervisor.getFromDef("OBJECTPLACER").getField("customData")

#Standard human radius
humanRadius = 0.35


def getAllWalls(numberWalls: int) -> list:
    '''Returns a 3D list of each wall, containing a x,y,z position and x,y,z scale'''
    #List to contain all the walls
    walls = []
    
    #Iterate for each of the walls
    for wallNumber in range(0, numberWalls):
        #Get the wall's position from the wall solid object
        wallObj = supervisor.getFromDef("WALL" + str(wallNumber))
        position = wallObj.getField("translation").getSFVec3f()
        #Get the wall's scale from the geometry
        wallBoxObj = supervisor.getFromDef("WALLBOX" + str(wallNumber))
        scale = wallBoxObj.getField("size").getSFVec3f()
        #Create the wall 2D list
        wall = [position, scale]
        #Add to complete wall list
        walls.append(wall)
    
    return walls
    
    
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

    #Iterate for box IDs
    for boxNum in range(0, numActivityBoxes):
        #Add the box to the list
        activityObjects.append(supervisor.getFromDef("ACT" + str(boxNum)))
        activitySizes.append(supervisor.getFromDef("ACTIVITYBOX" + str(boxNum)).getField("size").getSFVec3f())

    #Iterate for pad IDs
    for padNum in range(0, numActivityPads):
        #Add the pad to the list
        activityObjects.append(supervisor.getFromDef("ACT" + str(padNum) + "MAT"))
        activitySizes.append(supervisor.getFromDef("ACTIVITYPAD" + str(padNum)).getField("size").getSFVec3f())
        
    #Return the full object list and size list
    return activityObjects, activitySizes
    

def convertWallsToBoundaries(walls: list) -> list:
    '''Takes in list of walls as positions and scales then returns minimum and maximum wall positions'''
    #List of wall min and max positions
    wallBounds = []
    
    #Iterate for the walls
    for wall in walls:
        #Get the position and scale
        position = wall[0]
        scale = wall[1]
        #Calculate the minimum and maximum
        min = [position[0] - (float(scale[0]) / 2.0), position[1] - (float(scale[1]) / 2.0), position[2] - (float(scale[2]) / 2.0)]
        max = [position[0] + (float(scale[0]) / 2.0), position[1] + (float(scale[1]) / 2.0), position[2] + (float(scale[2]) / 2.0)]
        #Create the boundary list and append to the full list
        wallBound = [min, max]
        wallBounds.append(wallBound)
    
    return wallBounds
    
    
def generatePosition(radius: int, walls: list, humans: list, obstacles: list, bases: list):
    '''Returns a random x and z position within the area, that is valid'''
    #Round the radius to 2dp
    radius = round(float(radius), 2)
    #Get a random x and z position -12.4 <= x <= 12.4, -9.9 <= y <= 9.9 (with offset for radius)
    randomX = random.randrange(-1240 + (radius * 100), 1240 - (radius * 100)) / 100.0
    randomZ = random.randrange(-990 + (radius * 100), 990 - (radius * 100)) / 100.0
    
    #Not yet ready to be added
    done = False
    
    #Repeat until a valid position is found (need to limit max objects to make sure this ends)
    '''TODO: Add reject counter to skip adding object if it cannot find a location (if needed)'''
    while not done:
        done = True
        #Iterate through the walls
        for wall in walls:
            #If the left side and right side of the object are not both the same side of the wall
            if not ((randomX + radius < wall[0][0] and randomX - radius < wall[0][0]) or (randomX + radius > wall[1][0] and randomX - radius > wall[1][0])):
                #If the top side and bottom side of the object are not both the same side of the wall
                if not ((randomZ + radius < wall[0][2] and randomZ - radius < wall[0][2]) or (randomZ + radius > wall[1][2] and randomZ - radius > wall[1][2])):
                    #It intersects a wall and cannot be placed here
                    done = False
        
        #Iterate through the humans
        for human in humans:
            #Get the distance to the human
            distance = (((randomX - human[0]) ** 2) + ((randomZ - human[1]) ** 2)) ** (1/2)
            #If the distance is less than the two radii added together
            if distance <= radius + humanRadius:
                #It intersects a human and cannot be placed here
                done = False
        
        #Iterate through the obstacles
        for obstacle in obstacles:
            #Find maximum and minimum positions of obstacle
            obstacleMax = [obstacle[0] + (obstacle[3][0] / 2.0), obstacle[2] + (obstacle[3][2] / 2.0)]
            obstacleMin = [obstacle[0] - (obstacle[3][0] / 2.0), obstacle[2] - (obstacle[3][2] / 2.0)]
            #If the left side and right side of the object are not both the same side of the obstacle
            if not ((randomX + radius < obstacleMin[0] and randomX - radius < obstacleMin[0]) or (randomX + radius > obstacleMax[0] and randomX - radius > obstacleMax[0])):
                #If the top side and bottom side of the object are not both the same side of the obstacle
                if not ((randomZ + radius < obstacleMin[1] and randomZ - radius < obstacleMin[1]) or (randomZ + radius > obstacleMax[1] and randomZ - radius > obstacleMax[1])):
                    #It intersects an obstacle and cannot be placed here
                    done = False
        
        #Iterarte through the bases
        for base in bases:
            #If the distance to the base is less than 4
            if (((base[0] - randomX) ** 2) + ((base[1] - randomZ) ** 2)) ** (1/2) <= 4:
                #It is within the base exclusion zone and cannot be placed here
                done = False
        
        #If it cannot be placed at this point
        if not done:
            #Generate a new point for the next pass
            randomX = random.randrange(-1250 + (radius * 100), 1250 - (radius * 100)) / 100.0
            randomZ = random.randrange(-1000 + (radius * 100), 1000 - (radius * 100)) / 100.0
    
    #Returns the correct coordinates
    return randomX, randomZ
    

def setObstaclePositions(obstaclesList: list, obstacleNodes: list, walls: list, bases: list) -> list:
    '''Place the obstacles in generated positions and return the placed obstacles'''
    #List to contain all obstacles
    obstacles = []
    #Iterate for each obstacle
    for i in range(len(obstaclesList)):
        #Get each obstacle from children field in the obstacle root node OBSTACLEGROUP
        obstacle = obstacleNodes.getMFNode(i)
        #Get obstacle translation
        obstaclePos = obstacle.getField("translation")
        #Get random valid position
        x, z = generatePosition(max(obstaclesList[i][0], obstaclesList[i][2]), walls, [], obstacles, bases)
        y = (obstaclesList[i][1] / 2.0) + 0.05
        #Move humans to random positions in the building
        obstaclePos.setSFVec3f([x,y,z])
        obstacles.append([x, y, z, obstaclesList[i]])
    
    #Formatted as: [xPos, yPos, zPos, [xScale, yScale, zScale]]
    return obstacles


def setActivityPositions(activityItemList: list, activitySizeList: list, walls: list, bases: list, obstacles: list):
    '''Place the activities in generated positions and return the placed items position and scale'''
    #List to contain all activities
    activityItems = []
    #List position of current object
    itemId = 0
    #Iterate for each obstacle
    for item in activityItemList:
        #Get obstacle translation
        itemPosition = item.getField("translation")
        itemScale = activitySizeList[itemId]
        #Get random valid position
        x, z = generatePosition(max(itemScale[0], itemScale[2]), walls, [], obstacles + activityItems, bases)
        y = (itemScale[1] / 2.0) + 0.05
        #Move activity element to random position in the building
        itemPosition.setSFVec3f([x,y,z])
        activityItems.append([x, y, z, itemScale])
        itemId = itemId + 1
    
    #Formatted as: [xPos, yPos, zPos, [xScale, yScale, zScale]]
    return activityItems

def setHumanPositions(numberHumans: int, humanNodes: list, walls: list, obstacles: list, bases: list) -> list:
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
        x, z = generatePosition(humanRad, walls, humans, obstacles, bases)
        #Move humans to random positions in the building
        humanPos.setSFVec3f([x,humanY,z])
        humans.append([x, z])
    
    #Returns the placed humans as: [xPosition, zPosition]
    return humans

def performGeneration ():
    '''Generate a position for all the objects and place them in the world'''
    #Get group node containing humans 
    humanGroup = supervisor.getFromDef('HUMANGROUP')
    humanNodes = humanGroup.getField("children")
    #Get number of humans in map
    numberOfHumans = humanNodes.getCount()

    #Get group node containing bases
    baseGroup = supervisor.getFromDef("BASEGROUP")
    baseNodes = baseGroup.getField("children")
    #Get number of bases in map (divide by three as there is a min and max node for each too)
    numberOfBases = int(baseNodes.getCount() / 3)

    #Get group node containing obstacles 
    obstacleGroup = supervisor.getFromDef('OBSTACLEGROUP')
    obstacleNodes = obstacleGroup.getField("children")
    #Get number of obstacles in map
    numberOfObstacles = obstacleNodes.getCount()

    #Get group node containing walls 
    wallGroup = supervisor.getFromDef('WALLGROUP')
    wallNodes = wallGroup.getField("children")
    #Get number of walls in map
    numberOfWalls = wallNodes.getCount() - 5

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

    #Get all the walls
    allWallBlocks = getAllWalls(numberOfWalls)
    #Convert all the walls to boundaries
    allWallBounds = convertWallsToBoundaries(allWallBlocks)
    #Get all the obstacles
    allObstacles = getAllObstacles(numberOfObstacles)
    #Get all the activity items
    allActivityItems, allActivitySizes = getAllActivities(numberOfActivityBoxes, numberOfActivityPads)
    #Get all the base positions
    allBases = getAllBases(numberOfBases, baseNodes)

    #Place all the obstacles
    finalObstacles = setObstaclePositions(allObstacles, obstacleNodes, allWallBounds, allBases)
    #Place all the activities
    finalActivities = setActivityPositions(allActivityItems, allActivitySizes, allWallBounds, allBases, finalObstacles)
    #Place all the humans
    finalHumans = setHumanPositions(numberOfHumans, humanNodes, allWallBounds, finalObstacles + finalActivities, allBases)

    #Send signal to say that items have been placed
    outputField.setSFString("done")


#Check if a generation is being called
if outputField.getSFString() == "startGen":
    #Generate positions
    performGeneration()
    #Generation done - terminates loop and script
    notGenerated = False