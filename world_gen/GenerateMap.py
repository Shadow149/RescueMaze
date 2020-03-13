"""Map Generation Main Script v6
   Written by Robbie Goldman and Alfred Roberts

Changelog:
 V2:
 - Added randomly sized cubes as obstacles
 V3:
 - Added GUI integraction
 - Added child generation
 V4:
 - Added activity generation
 - Resized bases
 V5:
 - Added boundaries for rooms
 V6:
 - Added door calculations (position and connected rooms)
"""

import random
from PIL import Image
import math
import WorldCreator
import os
import GUI
dirname = os.path.dirname(__file__)


class node ():
    '''Node object to hold information on each part of the tree'''
    def __init__(self, parent, xMin, xMax, yMin, yMax, array):
        '''Initialize node with a parent and outer corner positions'''
        self.parent = parent
        #No children yet
        self.left = None
        self.right = None
        self.shape = [[xMin, yMin], [xMax, yMax]]
        #Currently no wall
        self.wall = None
        self.unusableWall = []
        self.wallParts = []
        #There is no base here yet
        self.basePresent = False
        self.basePossible = False
        #If the node is large enough a base may be added
        if (xMax - xMin)  - 2 > 20 and (yMax - yMin) - 2 > 20:
            self.basePossible = True
        self.outside = False
        #If one of its bounds are on the outside of the array
        if self.shape[0][0] == 0 or self.shape[0][1] == 0 or self.shape[1][0] == len(array[0]) - 1 or self.shape[1][1] == len(array):
            #This node is on the outside
            self.outside = True
    
    def setLeft(self, child):
        '''Set the left child'''
        self.left = child
    
    def setRight(self, child):
        '''Set the right child'''
        self.right = child
    
    def setWall(self, wall):
        '''Set the current wall'''
        self.wall = wall
        #If there is a wall (not empty)
        if len(wall) > 0:
            #If there is a parent
            if self.parent != None:
                #adjust the parent node to remove the end points
                self.parent.adjustWall(wall[0], wall[len(wall) - 1])
    
    def setWallParts(self, parts):
        '''Set the list of wall parts'''
        self.wallParts = parts

    def adjustWall(self, start, end):
        '''Add start and end to unusable walls'''
        self.unusableWall.append(start)
        self.unusableWall.append(end)
        #If there is a parent
        if self.parent != None:
            #Make the points unusable there too
            self.parent.adjustWall(start, end)
    
    def setBase (self):
        self.basePresent = True

    def getChildren(self):
        '''Return both children (may be None)'''
        return self.left, self.right
    
    def getParent(self):
        '''Return the parent node'''
        return self.parent
    
    def getWall(self):
        '''Return the list of wall positions'''
        return self.wall
    
    def getUnusableWall(self):
        '''Return the list of unusable wall positions'''
        return self.unusableWall

    def getBounds(self):
        '''Return the boundary points of the node'''
        return self.shape[0][0], self.shape[0][1], self.shape[1][0], self.shape[1][1]

    def getWallParts(self):
        '''Returnt the list of lists of wall sections'''
        return self.wallParts
    
    def getBase(self):
        return self.basePresent, self.basePossible
    
    def getOutside(self):
        return self.outside


def createEmptyWorld():
    '''Create a new array of 250 by 200 containing spaces and a wall of w around the outside'''
    array = []

    #Iterate y axis
    for i in range(0, 200):

        #Create this row
        row = []

        #Iterate x axis
        for j in range(0, 250):
            #If this is the top or bottom row or outsides
            if i == 0 or i == 199 or j == 0 or j == 249:
                #Add wall
                row.append("w")
            else:
                #Add empty space
                row.append(" ")
        #Add the row to the array
        array.append(row)
    
    #Return the generated array
    return array


def printWorld(array):
    '''Output the array as a map image file'''
    #Create a new image with the same dimensions as the array (in rgb mode with white background)
    img = Image.new("RGB", (len(array[0]), len(array)), "#FFFFFF")

    #Iterate across x axis
    for i in range(len(array[0])):
        #Iterate across y axis
        for j in range(len(array)):
            #If there is a wall there
            if array[j][i] == "w":
                #Add a blue pixel
                img.putpixel((i, j), (0, 0, 255))
            #If there is a base there
            if array[j][i] == "b":
                #add a grey pixel
                img.putpixel((i, j), (150, 150, 150))
    
    #Save the completed image to file
    img.save(os.path.join(dirname, "map.png"), "PNG")


def splitNode(n, array):
    '''Split a node into two parts randomly'''

    #Retrieve the boundary points of the node
    xMin, yMin, xMax, yMax = n.getBounds()

    #Calculate the size of the node
    size = [xMax - xMin, yMax - yMin]
    bounds = [[0,0],[0,0]]
    #Modifier for how much of the ends of the room not to include
    modifier = 0.35
    #Calculate bounds of possible split positions
    bounds[0][0] = int(size[1] * modifier) + yMin
    bounds[0][1] = yMax - int(size[1] * modifier)
    bounds[1][0] = int(size[0] * modifier) + xMin
    bounds[1][1] = xMax - int(size[0] * modifier)

    #Pick a random direction
    direction = random.randint(0, 1)

    #If the room is much wider than it is tall
    if size[0] > 1.5 * size[1]:
        #Split the room vertically
        direction = 1

    #If the room is much taller than it is wide
    if size[1] > 1.5 * size[0]:
        #Split the room horizontally
        direction = 0

    #Pick a position to split it on based on the direction
    r = random.randint(bounds[direction][0], bounds[direction][1])

    left = None
    right = None

    wall = []

    #Horizontal
    if direction == 0:
        #Generate left and right nodes from the boundary points
        left = node(n, xMin, xMax, yMin, r, array)
        right = node(n, xMin, xMax, r, yMax, array)
        #Iterate across at the generated y position
        for xPos in range(xMin, xMax + 1):
            #Set as walls
            array[r][xPos] = "w"
            #Add to the list of walls
            wall.append([xPos, r])
    else:
        #Vertical
        #Generate left and right nodes from bounary points
        left = node(n, xMin, r, yMin, yMax, array)
        right = node(n, r, xMax, yMin, yMax, array)
        #Iterate down at the generated x position
        for yPos in range(yMin, yMax + 1):
            #Set as walls
            array[yPos][r] = "w"
            #Add to the list of walls
            wall.append([r, yPos])

    #Set the nodes children and wall
    n.setLeft(left)
    n.setRight(right)
    n.setWall(wall)

    #Return the updated array
    return array


def splitDepth(rootNode, array):
    '''Split the given node if not already otherwise split both children'''
    #Get the children
    children = rootNode.getChildren()
    #If it doesn't have children - split it
    if children[0] == None or children[1] == None:
        array = splitNode(rootNode, array)
    else:
        #Otherwise split the children (recursively)
        array = splitDepth(children[0], array)
        array = splitDepth(children[1], array)
    
    #Return the updated array
    return array


def getAllMaxMin(rootNode):
    '''Get the min and max value for all the rooms'''
    #List containing nodes to be checked
    currentNodes = [rootNode]
    #List of leaf nodes
    finalNodes = []
    #List to contain boundaries
    nodeBounds = []

    #As long as there are still nodes to check
    while len(currentNodes) > 0:
        #Get the next node
        nextNode = currentNodes[0]
        #If it has no children
        if nextNode.left == None and nextNode.right == None:
            #Add this node to the final list - it is a leaf
            finalNodes.append(nextNode)
        else:
            #Add this nodes child nodes to be checked
            currentNodes.append(nextNode.left)
            currentNodes.append(nextNode.right)
        #delete this node from the list to be checked
        del currentNodes[0]
    
    #iterate through the final nodes
    for node in finalNodes:
        #Get the boundary shape
        nodeBounds.append(node.shape)

    #return the list of boundaries
    return nodeBounds


def openDoor (wall, array):
    '''Add a door randomly to a wall'''
    #Door information (centre position and direction 0 is up/down 1 is left/right)
    doorCentre = [None, None]
    doorDir = 0
    #If the wall is long enough to hold a full door
    if len(wall) > 16:
        #Generate random position
        r = random.randint(1, len(wall) - 16)
        #Add door middle to information
        doorCentre = [wall[r + 7][0], wall[r + 7][1]]
        #Iterate down door
        for i in range(0, 15):
            #Check the position is valid
            if i + r < len(wall):
                #Remove the wall at that position
                array[wall[i + r][1]][wall[i + r][0]] = " "
    else:
        #If the wall is too short for a full addDoors
        #Add door middle to information
        doorCentre = [wall[1 + (len(wall) // 2)][0], wall[1 + (len(wall) // 2)][1]]
        #Iterate across all central wall pieces
        for i in range(1, len(wall) - 1):
            #Remove the wall
            array[wall[i][1]][wall[i][0]] = " "

    #Calculate the door's orientation (bases on the two end points
    #If the y positions are different
    if wall[0][1] != wall[len(wall) - 1][1]:
        #It is a left/right door
        doorDir = 1
    
    #Return the updated array
    return array, [doorCentre, doorDir]


def addDoorToWall(wall, unusable, array):
    '''Add the doors to a given wall'''
    #List of all wall parts
    wallParts = []
    #List to contain added doors
    doorsList = []
    #The part of the wall currently being processed
    currentPart = []
    #Iterate through the wall
    for i in range(0, len(wall)):
        #If that wall can be used (not a joining position)
        if wall[i] not in unusable:
            #Add wall to the current parts
            currentPart.append(wall[i])
        else:
            #That position cannot be used - break in parts of the wall
            #If there is something in the current part
            if currentPart != []:
                #Add current part to the list of wall parts
                wallParts.append(currentPart)
                #Reset the current part
                currentPart = []
    
    #If there is still a part left
    if currentPart != []:
        #Add remaining part
        wallParts.append(currentPart)
    
    #List of parts of the wall longer than 15
    largeParts = []

    #Iterate wall parts
    for i in range(0, len(wallParts)):
        #If it is long enough
        if len(wallParts[i]) >= 15:
            #Add to large parts list
            largeParts.append(wallParts[i])

    #If there is at least 1 large part
    if len(largeParts) > 0:

        #Pick a random part
        w1 = random.randint(0, len(largeParts) - 1)
        #Open a door in that wall part
        array, newDoor = openDoor(largeParts[w1], array)
        doorsList.append(newDoor)

        #Iterate for large wall parts
        for i in range(len(largeParts)):
            #33% chance to add a door to a part (not the intial one again)
            if random.randint(0, 2) == 0 and i != w1:
                #Open a door in that wall part
                array, newDoor = openDoor(largeParts[i], array)
                doorsList.append(newDoor)
    else:
        #No large parts
        #No wall has been selected yet
        longest = -1
        selected = -1
        #Iterate throught the wall parts
        for i in range(0, len(wallParts)):
            #If the current part is longer than the selected part
            if len(wallParts[i]) > longest:
                #Select the wall part
                longest = len(wallParts)
                selected = i
        
        #If a part was selected
        if selected != -1:
            #Open a door in that wall part
            array, newDoor = openDoor(wallParts[selected], array)
            doorsList.append(newDoor)
    
    #Return the updated array and all the doors
    return array, doorsList


def addDoors(rootNode, array):
    '''Add doors to the root node and all its children (recursively)'''
    #Get the children of the node
    children = rootNode.getChildren()

    #List to contain all added doors
    allDoors = []

    #If there is a left child
    if children[0] != None:
        #Add doors to left child and all its children
        array, newDoors = addDoors(children[0], array)
        allDoors = allDoors + newDoors
    #If there is a right child
    if children[1] != None:
        #Add doors to right child and all its children
        array, newDoors = addDoors(children[1], array)
        allDoors = allDoors + newDoors

    #Get the wall for this node
    wall = rootNode.getWall()
    #Get the unusable wall parts for this node
    unusable = rootNode.getUnusableWall()

    #If there is a wall (not leaf node)
    if wall != None:
        #Add doors to the wall of that node
        array, addedDoors = addDoorToWall(wall, unusable, array)
        allDoors = allDoors + addedDoors

    #Return the updated array
    return array, allDoors


def convertBoundsToWorld(originalBounds):
    '''Takes the list of bounds in array space and converts to world space'''
    #List to contain final boundary positions
    finalBounds = []

    #Iterate list of positions
    for bound in originalBounds:
        #Calculate minimum and maximum
        minPos = WorldCreator.transformFromBounds(bound[0], bound[0])[0]
        #Adjust for wall thickness
        minPos[0] = minPos[0] + 0.075
        minPos[1] = minPos[1] + 0.075
        maxPos = WorldCreator.transformFromBounds(bound[1], bound[1])[0]
        #Adjust for wall thickness
        maxPos[0] = maxPos[0] - 0.075
        maxPos[1] = maxPos[1] - 0.075
        #Append data to final array
        finalBounds.append([minPos, maxPos])

    #Return world space bounds
    return finalBounds


def determineRoomIndex(position, bounds):
    '''Checks all the boundaries to determine which room a position is in'''
    #Id of current room
    boundId = 0
    #Iterate room boundaries
    for bound in bounds:
        #If it is between the xMin and xMax
        if bound[0][0] <= position[0] and bound[1][0] >= position[0]:
            #If it is between the yMin and yMax
            if bound[0][1] <= position[1] and bound[1][1] >= position[1]:
                #It is within this room
                return boundId

        #Increment room id counter
        boundId = boundId + 1

    #Not found in any of the rooms
    return -1

def convertDoorsToWorld(doors, bounds):
    '''Convert door positions and directions from array space to world space and determine room connections'''
    #List to contain final door data
    finalDoors = []

    #Adjustments to enter rooms [[vert+, vert-] , [horiz+, horiz-]]
    additions = [[[0, 0.085], [0, -0.085]], [[0.085, 0], [-0.085, 0]]]

    #Iterate through the doors
    for door in doors:
        #If the door exists
        if door[0][0] != None and door[0][1] != None:
            #Get the position of the centre of the door
            doorPos = WorldCreator.transformFromBounds(door[0], door[0])[0]
            #Get the positions to check for the rooms
            room1Pos = [doorPos[0] + additions[door[1]][0][0], doorPos[1] + additions[door[1]][0][1]]
            room2Pos = [doorPos[0] + additions[door[1]][1][0], doorPos[1] + additions[door[1]][1][1]]
            #Determine which room each position is in
            room1Id = determineRoomIndex(room1Pos, bounds)
            room2Id = determineRoomIndex(room2Pos, bounds)
            #Add the door to the list [[x, y], [room1, room2]]
            finalDoors.append([doorPos, [room1Id, room2Id]])

    #Return the completed list of doors
    return finalDoors

def generateWorld(splits):
    '''Perform generation of a world array'''
    #Create the empty array
    array = createEmptyWorld()
    #Create the root node with the boundaries of the array
    root = node(None, 0, len(array[0]) - 1, 0, len(array) - 1, array)

    #Perform binary split a number of times
    for i in range(splits):
        #Split the lowest level of the array
        array = splitDepth(root, array)

    #Get all the room boundary positions
    bounds = getAllMaxMin(root)
    
    #Add all the doors to the array
    array, allDoors = addDoors(root, array)
    
    #Return the array, root node, room boundaries and doors
    return array, root, bounds, allDoors


def generateWallParts(rootNode, array):
    '''Traverse the tree and generate all the wall parts for the nodes'''
    #Get the children of the current node
    children = rootNode.getChildren()

    #If there is a left child
    if children[0] != None:
        #Generate the wall parts for the left child
        generateWallParts(children[0], array)
    #If there is a right child
    if children[1] != None:
        #Generate the wall parts for the right child
        generateWallParts(children[1], array)
    
    #Get the wall for this node
    wall = rootNode.getWall()

    #If there is a wall (not a leaf)
    if wall != None:
        #List to contain all wall parts
        wallParts = []
        #The current part
        part = []

        #Iterate for each position in the wall
        for piece in wall:
            #If this piece is a wall
            if array[piece[1]][piece[0]] == "w":
                #Add it to the end of the part
                part.append(piece)
            else:
                #If there is something in this part
                if part != []:
                    #Add the part to the list
                    wallParts.append(part)
                    #Reset the part
                    part = []

        #If there is a part left over
        if part != []:
            #Add it to the end of the list
            wallParts.append(part)

        #Set the parts in the node object
        rootNode.setWallParts(wallParts)

def createAllWallBlocks(rootNode, usedPos):
    '''Create a list of all the wall objects needed (position and scale) (Recursive)'''
    #Empty list to contain all the wall blocks
    wallData = []
    
    #Get the wall parts for this node
    wallParts = rootNode.getWallParts()

    #If there were some parts in this node
    if len(wallParts) > 0:
        #Iterate parts
        for part in wallParts:
            
            #Remove and parts of the wall that have already been placed
            for bit in part:
                if bit in usedPos:
                    part.remove(bit)

            if len(part) > 0:
                #Convert the wall to position and scale then append to the data list
                wallData.append(WorldCreator.transformFromBounds(part[0], part[-1]))

            #Add all the parts used to the list of used parts
            for bit in part:
                usedPos.append(bit)
            
    
    #Get the Children of this node
    children = rootNode.getChildren()

    #If there is a left child
    if children[0] != None:
        #Add to the data the data generated from the left child
        wallDataPart, usedPos = createAllWallBlocks(children[0], usedPos)
        wallData = wallData + wallDataPart
    #If there is a right child
    if children[1] != None:
        #Add to the data the data generated from the right child
        wallDataPart, usedPos = createAllWallBlocks(children[1], usedPos)
        wallData = wallData + wallDataPart
    
    #Return the wall data
    return wallData, usedPos


def addBase(root, array, quadrants):
    '''Add a base to the tree'''
    added = False
    base = []
    usedQuad = None

    #Repeat until the base has been added
    while not added:
        #Set the current node to the root
        currentNode = root
        #Get the children
        children = root.getChildren()
        
        #Pick a random quadrant (picks one of four pairs of binary choices)
        rQuad = random.randint(0, len(quadrants) - 1)

        #If there are children
        if children[0] != None and children[1] != None:
            #Move the current node based on the quadrant selected
            currentNode = children[quadrants[rQuad][0]]
            #Get the children
            children = currentNode.getChildren()
            #If there are children
            if children[0] != None and children[1] != None:
                #Move the current node based on the quadrant selected
                currentNode = children[quadrants[rQuad][1]]
                #Get the children
                children = currentNode.getChildren()

        #Until the bottom of the tree has been reached
        while children[0] != None and children[1] != None:
            #Randomly pick one of the binary leaves
            r = random.randint(0, 1)
            #Move current node
            currentNode = children[r]
            #Get the current nodes children
            children = currentNode.getChildren()
        
        #Get if there is a base in the current node and if it is big enough too
        already, possible = currentNode.getBase()
        #Get if the node is on the outside
        outside = currentNode.getOutside()

        #If there is no base there, it is big enough and it is on the outside
        if not already and possible and outside:
            #Place a base there
            currentNode.setBase()
            #Get the boundaries of the leaf
            xMin, yMin, xMax, yMax = currentNode.getBounds()
            #Move to possible base starting positions
            xMin = xMin + 1
            yMin = yMin + 1
            xMax = xMax - 21
            yMax = yMax - 21

            #Calculate a third of the dimensions
            xThird = math.floor((xMax - xMin) / 3)
            yThird = math.floor((yMax - yMin) / 3)

            #Generate a random position in the central third
            xPos = random.randint(xMin + xThird, xMax - xThird)
            yPos = random.randint(yMin + yThird, yMax - yThird)

            #Create the base array
            base = [[xPos, yPos], [xPos + 15, yPos + 15]]

            #Set which quadrant was used
            usedQuad = quadrants[rQuad]

            #A base has been added
            added = True
    
    #If a base was created
    if base != []:
        #Iterate across x axis
        for x in range(base[0][0], base[1][0] + 1):
            #Iterate down y axis
            for y in range(base[0][1], base[1][1] + 1):
                #If the position is valid in the world array
                if x > 0 and x < len(array[0]) - 1 and y > 0 and y < len(array):
                    #Set that position to a base
                    array[y][x] = "b"
    
    #Return the new base, updated array and the used quadrant
    return base, array, usedQuad


def createBases(array, numberBases, rootNode):
    '''Add a set of bases to the world'''
    bases = []
    #All four quadrants (two binary choices)
    quads = [[0, 0], [0, 1], [1, 0], [1, 1]]

    #Iterate for each base (max 4)
    for i in range(0, numberBases):
        #Add a base
        base, array, used = addBase(rootNode, array, quads)
        #If a valid quad was used
        if used in quads:
            #Remove the used quad from the list (so it can't be used again)
            quads.remove(used)
        #Add the base to the list of bases
        bases.append(base)
    
    #Return the updated array and the list of base positions
    return array, bases


def addRobots(bases):
    '''Add robots to the bases'''
    robots = []

    #For each of the robots (2 robots)
    for i in range(0, 2):
        #If there is a base free to add it to
        if i < len(bases):
            #Calculate the position of the centre of the base
            xPos = math.floor((bases[i][1][0] - bases[i][0][0]) / 2) + bases[i][0][0]
            yPos = math.floor((bases[i][1][1] - bases[i][0][1]) / 2) + bases[i][0][1]
            #Add position to the list of robots
            robots.append([xPos, yPos])
    
    #Return the list of robots
    return robots


def createBaseBlocks(bases):
    '''Create the world space base blocks from the base positions'''
    newBases = []

    #Iterate for the bases
    for base in bases:
        #Convert the base positions to world space
        b = WorldCreator.transformFromBounds(base[0], base[1])
        #Add to list of created bases
        newBases.append(b)
    
    #Return the list of world space bases
    return newBases


def convertRobotsToWorld(robots):
    '''Create the world space positions list for the robots'''
    newRobots = []

    #Iterate for the robots
    for robot in robots:
        #Convert the robot position to world space ([0] is because position only is needed, not scale)
        r = WorldCreator.transformFromBounds(robot, robot)[0]
        #Add to list of robot world positions
        newRobots.append(r)

    #Return the list of robot world positions    
    return newRobots


def generateEdges(array):
    '''Generate a list of all the outside positions of the given array'''
    positions = []

    #Iterate down on y axis
    for i in range(0, len(array)):
        #Left and right
        for j in [0, len(array[0]) - 1]:
            #Add to list of positions
            positions.append([j, i])

    #Iterate across x axis
    for i in range(0, len(array[0])):
        #Top and bottom
        for j in [0, len(array) - 1]:
            #If not already in the list
            if [i, j] not in positions:
                #Add to the list of positions
                positions.append([i, j])
    
    #Return the generated list
    return positions

def addObstacle(dynamic):
    '''Generate random dimensions for an obstacle'''
    height = float(random.randrange(50, 130)) / 100.0
    width = float(random.randrange(30, 220)) / 100.0
    depth = float(random.randrange(30, 220)) / 100.0
    obstacle = [width, height, depth, dynamic]
    return obstacle
	

def generateObstacles(numObstaclesStatic, numObstaclesDynamic):
    '''Generate a list of obstacles of length numObstacles'''
    #List to hold obstacle dimensions
    obstacles = []
    #Iterate for each static obstacle
    for i in range(0, numObstaclesStatic):
        #Create an obstacle and add it to the list
        newObstacle = addObstacle(False)
        obstacles.append(newObstacle)

    #Iterate for each static obstacle
    for i in range(0, numObstaclesDynamic):
        #Create an obstacle and add it to the list
        newObstacle = addObstacle(True)
        obstacles.append(newObstacle)

    #Return the list of dimensions
    return obstacles


def generatePlan (numSplits, numObstaclesStatic, numObstaclesDynamic, numBases):
    '''Perform a map generation up to png - does not update map file'''
    #Generate the world and tree
    world, root, bounds, doors = generateWorld(numSplits)
    #Create the bases from the world and the tree
    world, bases = createBases(world, numBases, root)

    #Create the robots from the bases
    robots = addRobots(bases)
    #Convert the bases to world space
    baseBlocks = createBaseBlocks(bases)
    #Convert the robot positions to world space
    robotPositions = convertRobotsToWorld(robots)
	
    #Create a list of obstacles
    obstacles = generateObstacles(numObstaclesStatic, numObstaclesDynamic)

    #Output the world as a picture
    printWorld(world)

    print("Generation Successful")

    #Return generated parts
    return world, root, robotPositions, obstacles, baseBlocks, bounds, doors


def generateWorldFile (world, root, baseBlocks, obstacles, robotPositons, numHumans, numChildren, activities, bounds, doors, window):
    #Generate the wall parts for the tree
    generateWallParts(root, world)
    #Generate the edges of the map to mark as used
    used = generateEdges(world)
    #Calculate all the wall blocks for the tree (exclude used pixels)
    walls, used = createAllWallBlocks(root, used)

    #Convert the bounds positions to world space
    bounds = convertBoundsToWorld(bounds)

    doors = convertDoorsToWorld(doors, bounds)

    #Make a map from the walls and objects
    WorldCreator.makeFile(walls, baseBlocks, obstacles, robotPositions, numHumans, numChildren, activities, bounds, doors, window)


def checkNoNones (dataValues):
    '''Check there are no None values in a list'''
    #Iterate all items
    for value in dataValues:
        #If there is a none
        if value == None:
            return False
    #Otherwise
    return True

#Generate an empty map (to be loaded to begin)
printWorld(createEmptyWorld())

#Create an instacnce of the user interface
window = GUI.GenerateWindow()

#The UI is currently in use
guiActive = True

#Set all generation parameters to Nones
world = None
root = None
robotPositions = None
obstacles = None
baseBlocks = None
humanNum = None
childNum = None
activities = None
bounds = None
doors = None

activityNumbers = []

#Loop while the UI is active
while guiActive:

    #If a generation is being called for
    if window.ready:
        #Cannot save now
        window.setSaveButton(False)
        #Get generation values as follows:
        #[[room splits], [humans, children], [obstaclesStatic, obstaclesDynamic], [bases] [activityTypes]]
        genValues = window.getValues()
        #A generation has started (resets flag so generation is not called again)
        window.generateStarted()
        #Generate a plan with the values
        world, root, robotPositions, obstacles, baseBlocks, bounds, doors = generatePlan(genValues[0][0], genValues[2][0], genValues[2][1], genValues[3][0])
        #Unpack the unused human values
        humanNum, childNum = genValues[1][0], genValues[1][1]
        #Unpack the used obstacle counts
        obsStaticNum, obsDynamicNum = genValues[2][0], genValues[2][1]
        #Unpack the activity list
        activities = genValues[4]
        #Update the UI image of the map
        window.updateImage()

        #List of activities to be added to the world
        activityNumbers = []
        #Message to indicate which activities will be added
        activityList = "None"

        #If there are activities
        if len(activities) > 0:
            #Reset message
            activityList = ""
            #Iterate through the activities
            for activity in activities:
                #Add number to list and name to message
                activityNumbers.append(activity[0])
                activityList = activityList + "\n" + activity[1]

        #Update the output fields of the window
        window.setGeneratedInformation("Adults: " + str(humanNum), "Children: " + str(childNum), str(len(baseBlocks)), "Static: " + str(obsStaticNum), "Dynamic: " + str(obsDynamicNum), activityList)

    #If a save file is being called for
    if window.saving:
        #Cannot save now
        window.setSaveButton(False)
        #Saving has begin (resets flag so save is not called twice)
        window.saveStarted()
        #If all values that are needed are not None
        if checkNoNones([world, root, robotPositions, obstacles, baseBlocks, humanNum, childNum, activities, bounds, doors]):
            #Generate and save a world
            generateWorldFile(world, root, baseBlocks, obstacles, robotPositions, humanNum, childNum, activityNumbers, bounds, doors, window)

    #Attempt update loops           
    try:
        #Toggle the save button to the correct state
        window.setSaveButton(checkNoNones([world, root, robotPositions, obstacles, baseBlocks, humanNum, childNum, bounds]))
        #Update loops for the UI - manually called to prevent blocking of this program
        window.update_idletasks()
        window.update()
    #If an error occurred in the update (window closed)
    except:
        #Terminate the UI loop
        guiActive = False

