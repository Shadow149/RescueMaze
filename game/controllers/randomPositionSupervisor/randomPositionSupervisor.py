"""Object Placing Supervisor Prototype v1
   Written by Robbie Goldman and Alfred Roberts

Features:
 - Places humans and obstacles randomly
 - Will not intersect walls or other objects
 - Will not be within 4 units of bases

Changelog:
 - 
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
    
    
def getAllBases() -> list:
    '''Returns a list of all the bases as a centre position'''
    #List to contain all the bases
    bases = []
    
    #Iterate for the bases
    for i in range(0, 3):
        #Get the minimum and maximum position vectors
        minBase = supervisor.getFromDef("base" + str(i) + "Min").getField("translation").getSFVec3f()
        maxBase = supervisor.getFromDef("base" + str(i) + "Max").getField("translation").getSFVec3f()
        #Create the base (midpoint of the min and max: min + (max-min/2))
        base = [((maxBase[0] - minBase[0]) / 2.0) + minBase[0], ((maxBase[2] - minBase[2]) / 2.0) + minBase[2]]
        #Add to list of bases
        bases.append(base)
    
    return bases
        

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
    #List to contain all humans
    obstacles = []
    #Iterate for each obstacle
    for i in range(len(obstaclesList)):
        #Get each obstacle from children field in the obstacle root node OBSTACLEGROUP
        obstacle = obstacleNodes.getMFNode(i)
        #Get obstacle translation
        obstaclePos = obstacle.getField("translation")
        #Get random valid position
        x, z = generatePosition(max(obstaclesList[i][0], obstaclesList[i][2]), walls, [], obstacles, bases)
        y = obstaclesList[i][1] / 2.0
        #Move humans to random positions in the building
        obstaclePos.setSFVec3f([x,y,z])
        obstacles.append([x, y, z, obstaclesList[i]])
    
    #Formatted as: [xPos, yPos, zPos, [xScale, yScale, zScale]]
    return obstacles


def setHumanPositions(numberHumans, humanNodes, walls, obstacles, bases: list) -> list:
    '''Place the humans in generated positions and return the placed humans'''
    #List to contain all humans
    humans = []
    #Iterate for each human
    for i in range(numberHumans):
        #Get each human from children field in the human root node HUMANGROUP
        human = humanNodes.getMFNode(i)
        #Get human translation
        humanPos = human.getField("translation")
        #Get random valid position
        x, z = generatePosition(humanRadius, walls, humans, obstacles, bases)
        #Move humans to random positions in the building
        humanPos.setSFVec3f([x,0.5,z])
        humans.append([x, z])
    
    #Returns the placed humans as: [xPosition, zPosition]
    return humans


#Get group node containing humans 
humanGroup = supervisor.getFromDef('HUMANGROUP')
humanNodes = humanGroup.getField("children")
#Get number of humans in map
numberOfHumans = humanNodes.getCount()

#Get group node containing obstacles 
obstacleGroup = supervisor.getFromDef('OBSTACLEGROUP')
obstacleNodes = obstacleGroup.getField("children")
#Get number of obstacles in map
numberOfObstacles = obstacleNodes.getCount()

#Get group node containing walls 
wallGroup = supervisor.getFromDef('WALLGROUP')
wallNodes = wallGroup.getField("children")
#Get number of walls in map
numberOfWalls = wallNodes.getCount() - 9

#Get all the walls
allWallBlocks = getAllWalls(numberOfWalls)
#Convert all the walls to boundaries
allWallBounds = convertWallsToBoundaries(allWallBlocks)
#Get all the obstacles
allObstacles = getAllObstacles(numberOfObstacles)
#Geta ll the base positions
allBases = getAllBases()

#Place all the obstacles
finalObstacles = setObstaclePositions(allObstacles, obstacleNodes, allWallBounds, allBases)
#Place all the humans
finalHumans = setHumanPositions(numberOfHumans, humanNodes, allWallBounds, finalObstacles, allBases)

#Send signal to say that items have been placed
outputField.setSFString("done")

