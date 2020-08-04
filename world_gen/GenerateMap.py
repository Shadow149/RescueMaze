"""Map Generation Main Script Type 2 v4
   Written by Robbie Goldman and Alfred Roberts

Changelog:
 Type 1
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
 Type 2
 V1:
 - Based on type 1 but modified to perform maze generation not BSP
 V2:
 - Changed so that the start is the exit too
 V3:
 - Added human generation
 V4:
 - Updated generation so start tile is within the main map section
"""

import random
from PIL import Image
import math
import WorldCreator
import os
import GUI
dirname = os.path.dirname(__file__)

#Object to contain information for a map tile
class Tile ():
    def __init__ (self) -> None:
        '''Initialize the tile with all four walls and no special parts'''
        #All walls
        self.upperWall = True
        self.lowerWall = True
        self.leftWall = True
        self.rightWall = True
        #No special parts
        self.checkpoint = False
        self.trap = False
        self.goal = False
        self.swamp = False
        #List of humans [up, right, down, left]
        self.humans = [0,0,0,0]
        self.hasHuman = False
        #No obstacles yet
        self.obstacle = False

    def addWalls (self, wallList: list) -> None:
        '''Add a list of walls'''
        if 0 in wallList:
            self.upperWall = True
        if 1 in wallList:
            self.rightWall = True
        if 2 in wallList:
            self.lowerWall = True
        if 3 in wallList:
            self.leftWall = True

    def removeWalls (self, wallList: list) -> None:
        '''Remove a list of walls'''
        if 0 in wallList:
            self.upperWall = False
        if 1 in wallList:
            self.rightWall = False
        if 2 in wallList:
            self.lowerWall = False
        if 3 in wallList:
            self.leftWall = False

    def addCheckpoint (self) -> None:
        '''Add a checkpoint - removes traps, goals and swamps'''
        self.checkpoint = True
        self.trap = False
        self.goal = False
        self.swamp = False

    def removeCheckpoint (self) -> None:
        '''Remove a checkpoint'''
        self.checkpoint = False

    def addTrap (self) -> None:
        '''Add a trap - removes checkpoints, goals and swamps'''
        self.trap = True
        self.checkpoint = False
        self.goal = False
        self.swamp = False

    def removeTrap (self) -> None:
        '''Remove a trap'''
        self.trap = False

    def addGoal (self) -> None:
        '''Add a goal - removes checkpoints, traps and swamps'''
        self.goal = True
        self.checkpoint = False
        self.trap = False
        self.swamp = False

    def removeGoal (self) -> None:
        '''Remove a goal'''
        self.goal = False
    
    def addSwamp (self) -> None:
        '''Add a swamp - removes checkpoints, traps and goals'''
        self.swamp = True
        self.checkpoint = False
        self.trap = False
        self.goal = False

    def removeSwamp (self) -> None:
        '''Remove a swamp'''
        self.swamp = False
    
    def getWalls (self) -> list:
        '''Returns a list of bools which represents if each of the four walls is present'''
        return [self.upperWall, self.rightWall, self.lowerWall, self.leftWall]

    def getCheckpoint (self) -> bool:
        '''Return if this tile has a checkpoint'''
        return self.checkpoint

    def getTrap (self) -> bool:
        '''Return if this tile has a trap'''
        return self.trap

    def getGoal (self) -> bool:
        '''Return if this tile has a goal'''
        return self.goal
    
    def getSwamp (self) -> bool:
        '''Return if this tile has a swamp'''
        return self.swamp
       
    def addHuman (self, type, wall) -> bool:
        '''Add a human to a given wall, returns true only if a wall was present in that direction and it didn't contain a human'''
        #Get the walls from this tile
        walls = self.getWalls()
        #If the wall position is valid
        if wall < len(walls) and wall < len(self.humans) and wall >= 0 and not self.hasHuman:
            #If there isn't already a human on that wall
            if walls[wall] and self.humans[wall] == 0:
                #Set the human value
                self.humans[wall] = type
                #This tile does contain a human
                self.hasHuman = True
                #Successfully added
                return True
        
        #Failed to add human
        return False
    
    def getHuman (self) -> bool:
        '''Returns true if there is a human on this tile'''
        #Iterate humans list
        for h in self.humans:
            #If it is a human
            if h != 0:
                return True
        #Otherwise
        return False
        
    def getHumanData (self) -> list:
        '''Returns the human type and the wall it is on'''
        #Iterate through the walls
        for i in range(0, len(self.humans)):
            #If there is a human
            if self.humans[i] != 0:
                #Return the human type and the wall
                return self.humans[i], i
        
        #Return no human
        return 0, 0
     
    def addObstacle(self) -> None:
        '''Toggle flag for an obstacle to true'''
        self.obstacle = True
    
    def getObstacle(self) -> bool:
        '''Returns true if an obstacle has been placed in this tile'''
    
    def generatePixels (self) -> list:
        '''Generate a grid of pixels for this tile'''
        #Array to hold pixel information
        pixels = []

        #The background pixel colour
        basicPixel = 0

        #Change background colour if this is a checkpoint / trap / goal / swamp
        if self.checkpoint:
            basicPixel = 2
        if self.trap:
            basicPixel = 3
        if self.goal:
            basicPixel = 4
        if self.swamp:
            basicPixel = 5

        #Fill array with background pixels
        for y in range(0, 20):
            row = []
            for x in range(0, 20):
                row.append(basicPixel)
            pixels.append(row)

        #Add upper wall
        if self.upperWall:
            for x in range(0, 20):
                pixels[0][x] = 1
                pixels[1][x] = 1
            #Add upper human
            if self.humans[0] > 0:
                hColour = 6
                if self.humans[0] == 4:
                    hColour = 7
                for x in range(5, 16):
                    pixels[2][x] = hColour
        #Add left wall
        if self.leftWall:
            for y in range(0, 20):
                pixels[y][0] = 1
                pixels[y][1] = 1
            #Add left human
            if self.humans[3] > 0:
                hColour = 6
                if self.humans[3] == 4:
                    hColour = 7
                for y in range(5, 16):
                    pixels[y][2] = hColour
        #Add lower wall
        if self.lowerWall:
            for x in range(0, 20):
                pixels[len(pixels) - 1][x] = 1
                pixels[len(pixels) - 2][x] = 1
            if self.humans[2] > 0:
                hColour = 6
                if self.humans[2] == 4:
                    hColour = 7
                for x in range(5, 16):
                    pixels[len(pixels) - 3][x] = hColour
        #Add right wall
        if self.rightWall:
            for y in range(0, 20):
                pixels[y][len(pixels[0]) - 1] = 1
                pixels[y][len(pixels[0]) - 2] = 1
            #Add right human
            if self.humans[1] > 0:
                hColour = 6
                if self.humans[1] == 4:
                    hColour = 7
                for y in range(5, 16):
                    pixels[y][len(pixels[0]) - 3] = hColour
        
        #Add obstacle marker
        if self.obstacle:
            for x in range(8, 13):
                for y in range(8, 13):
                    pixels[y][x] = 8
                    
        #Return array of pixels
        return pixels


def createEmptyWorld(x, y):
    '''Create a new array of x by y containing all walls on all tiles'''
    array = []

    #Iterate y axis
    for i in range(0, y):

        #Create this row
        row = []

        #Iterate x axis
        for j in range(0, x):
            #Add a new section of the maze
            row.append(Tile())
        #Add the row to the array
        array.append(row)
    
    #Return the generated array
    return array


def printWorld(array):
    '''Output the array as a map image file'''
    #Create a new image with the same dimensions as the array (in rgb mode with white background)
    img = Image.new("RGB", (len(array[0]) * 20, len(array) * 20), "#FFFFFF")

    xStart = 0
    yStart = 0
    
    #Iterate across x axis
    for i in range(len(array[0])):
        #Reset y start position each loop
        yStart = 0
        #Iterate across y axis
        for j in range(len(array)):
            #Get that tile
            tile = array[j][i]
            #If there is a tile there
            if tile != None:
                #Get the pixels for the tile
                pixels = tile.generatePixels()
                #Iterate across x of pixels
                for x in range(0, 20):
                    #Iterate across y of pixels
                    for y in range(0, 20):
                        #If there is a wall
                        if pixels[y][x] == 1:
                            #Add blue pixel
                            img.putpixel((xStart + x, yStart + y), (0, 0, 255))
                        #If there is a checkpoint
                        if pixels[y][x] == 2:
                            #Add grey pixel
                            img.putpixel((xStart + x, yStart + y), (175, 175, 175))
                        #If there is a trap
                        if pixels[y][x] == 3:
                            #Add black pixel
                            img.putpixel((xStart + x, yStart + y), (0, 0, 0))
                        #If there is a goal
                        if pixels[y][x] == 4:
                            #Add green pixel
                            img.putpixel((xStart + x, yStart + y), (0, 255, 0))
                        #If there is a swamp
                        if pixels[y][x] == 5:
                            #Add tan pixel
                            img.putpixel((xStart + x, yStart + y), (222, 184, 135))
                        #If there is a visual human
                        if pixels[y][x] == 6:
                            #Add magenta pixel
                            img.putpixel((xStart + x, yStart + y), (255, 0, 255))
                        #If there is a thermal human
                        if pixels[y][x] == 7:
                            #Add red pixel
                            img.putpixel((xStart + x, yStart + y), (255, 0, 0))
                        #If there is an obstacle
                        if pixels[y][x] == 8:
                            #Add orange pixel
                            img.putpixel((xStart + x, yStart + y), (255, 127, 0))
            #Increase y start each pass
            yStart = yStart + 20
        #Increase x start position each time
        xStart = xStart + 20
    
    #Save the completed image to file
    img.save(os.path.join(dirname, "map.png"), "PNG")


def openSurround(world, target, direction):
    '''Opens a the wall in the given direction. Both the target tile and the one adjacent to it.'''
    #Directions (in order) of the surrounding tiles
    around = [[0, -1], [1, 0], [0, 1], [-1, 0]]
    #For each direction this is the alternative in the opposite direction
    alternateDirections = [2, 3, 0, 1]

    #Get the target tile
    thisTile = world[target[1]][target[0]]

    #Get the position of the tile being opened to
    opened = [target[0] + around[direction][0], target[1] + around[direction][1]]

    #Get the other tile
    thatTile = world[opened[1]][opened[0]]

    #Open the walls in both tiles
    thatTile.removeWalls([alternateDirections[direction]])
    thisTile.removeWalls([direction])

    #Return the position that was opened to
    return opened


def getAllAround (world, pos):
    '''Return a list of the 4 surrounding tiles'''
    aroundPositions = []
    aroundDirs = []
    #Surrounding directions
    around = [[0, -1], [1, 0], [0, 1], [-1, 0]]

    #Initialize direction
    d = 0
    #Iterate for each surrounding tile
    for a in around:
        #Get the position
        otherPos = [pos[0] + a[0], pos[1] + a[1]]
        #If the position is in the grid
        if otherPos[0] >= 0 and otherPos[0] < len(world[0]) and otherPos[1] >= 0 and otherPos[1] < len(world):
            #Add position and direction to list
            aroundPositions.append(otherPos)
            aroundDirs.append(d)
        #Increment the direction
        d = d + 1

    #Return the tiles and directions
    return aroundPositions, aroundDirs


def depthFirstMaze (world, start):
    '''Generate a maze using depth first search'''
    #List of tiles that have been visited
    visited = [start]
    #The current stack - allowing for backtracking
    stack = [start]

    #Currently selected point on the stack
    pointer = 0

    #If the algorithm has finished
    done = False

    #While it is still generating
    while not done:
        usable = []
        #Get all the tiles around the current one
        posList, directions = getAllAround(world, stack[pointer])
        #Iterate through found tiles
        for i in range(len(posList)):
            #If it hasn't been visited yet
            if posList[i] not in visited:
                #Add to the list of usable tiles with it's direction
                usable.append([posList[i], directions[i]])

        #If there are tiles that can be reached
        if len(usable) > 0:
            #Pick a random tile
            r = random.randrange(0, len(usable))
            #Open the wall to that tile
            openSurround(world, stack[pointer], usable[r][1])
            #Add tile to visited
            visited.append(usable[r][0])
            #Add tile to stack
            stack.append(usable[r][0])
            #Increment pointer to point at new tile
            pointer = pointer + 1
        else:
            #If there are no unvisited tiles to go to
            #Decrement pointer (go back a tile)
            pointer = pointer - 1
            #Remove last item from stack
            del stack[len(stack) - 1]
            #If the pointer has retreated past the start
            if pointer < 0:
                #The algorithm is finished
                done = True


def checkConnect (world, start, check, avoid):
    '''Check if the start and check points can be connected without avoid'''
    #List of used tiles
    visited = [start, avoid]
    #Stack to hold the tile path
    stack = [start]

    #Pointer - current tile
    pointer = 0

    #Finished
    done = False

    #Until it has finished
    while not done:
        usable = []
        #Get surrounding tiles
        posList, directions = getAllAround(world, stack[pointer])
        #Get the walls of the current tile
        tileWalls = world[stack[pointer][1]][stack[pointer][0]].getWalls()
        #Iterate surrounding tiles
        for i in range(len(posList)):
            #If the tile hasn't already been visited and the wall is open to get to it
            if posList[i] not in visited and not tileWalls[directions[i]]:
                #Get the tile that corresponds to that movement
                otherTile = world[posList[i][1]][posList[i][0]]
                #If there is a tile there
                if otherTile != None:
                    #If that tile isn't a trap or swamp or obstacle
                    if not otherTile.getTrap() and not otherTile.getSwamp() and not otherTile.getObstacle():
                        #Add the tile to usable tiles
                        usable.append([posList[i], directions[i]])

        #Iterate through usable tiles
        for u in usable:
            #If it is the tile being searched for
            if u[0] == check:
                #The connection can be made
                return True

        #If there are tiles to go to
        if len(usable) > 0:
            #Move to the next one
            visited.append(usable[0][0])
            stack.append(usable[0][0])
            pointer = pointer + 1
        else:
            #Move back a tile
            pointer = pointer - 1
            del stack[len(stack) - 1]
            #If it has moved back past the start
            if pointer < 0:
                #It has finished
                done = True

    #Connection could not be made
    return False


def addCheckPoints(array, checkpoints, startTile, endTile, x, y):
    '''Add a number of checkpoints to the map'''
    #Cannot put a checkpoint at the start or end
    disallowedSpaces = [startTile, endTile]
    
    #Get data about tiles surrounding the start
    aroundStart, aroundStartDir = getAllAround(array, startTile)
    
    #Iterate through surrounding tiles
    for i in range(0, len(aroundStart)):
        #If there is not a wall to block
        if not array[startTile[1]][startTile[0]].getWalls()[aroundStartDir[i]]:
            #Cannot place check point here
            disallowedSpaces.append([aroundStart[i][0], aroundStart[i][1]])
    
    #Split the grid into quadrants
    quads = [[[0, 0], [int(x / 2) - 1, int(y / 2) - 1]],
             [[int(x / 2), 0], [x - 1, int(y / 2) - 1]],
             [[0, int(y / 2)], [int(x / 2) - 1, y - 1]],
             [[int(x / 2), int(y / 2)], [x - 1, y - 1]]]

    #For each of the checkpoints
    for i in range(0, checkpoints):
        #Not added yet
        added = False
        #Get a random quadrant
        rQ = random.randrange(0, len(quads))
        q = quads[rQ]
        #Remove the quadrant
        del quads[rQ]
        #Until it has added the checkpoint
        while not added:
            #Get a random position
            xPos = random.randint(q[0][0], q[1][0])
            yPos = random.randint(q[0][1], q[1][1])
            #If it is allowed to put the checkpoint there
            if [xPos, yPos] not in disallowedSpaces:
                #Get the tile
                tile = array[yPos][xPos]
                #If there isn't already a checkpoint or trap there
                if not tile.getCheckpoint() and not tile.getTrap() and not tile.getGoal():
                    #Add a checkpoint
                    tile.addCheckpoint()
                    #Add this tile and four surrounding to not allowed spaces
                    disallowedSpaces.append([xPos, yPos])
                    around = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                    for a in around:
                        disallowedSpaces.append([xPos + a[0], yPos + a[1]])
                    #The checkpoint has been added
                    added = True


def addTraps(array, traps, startTile, endTile, x, y):
    '''Add a number of traps to the map'''
    #Split the grid into quadrants
    quads = [[[0, 0], [int(x / 2) - 1, int(y / 2) - 1]],
             [[int(x / 2), 0], [x - 1, int(y / 2) - 1]],
             [[0, int(y / 2)], [int(x / 2) - 1, y - 1]],
             [[int(x / 2), int(y / 2)], [x - 1, y - 1]]]

    #Iterate for each trap
    for i in range(0, traps):
        #It hasn't added the trap yet
        added = False
        #Until the trap has been added
        while not added:
            #Pick a random quadrant
            rQ = random.randrange(0, len(quads))
            q = quads[rQ]
            #Generate a random position
            xPos = random.randint(q[0][0], q[1][0])
            yPos = random.randint(q[0][1], q[1][1])
            #Get the tile
            tile = array[yPos][xPos]
            #If it isn't the start or end and there is a tile there
            if [xPos, yPos] != startTile and [xPos, yPos] != endTile and tile != None:
                #If there isn't a checkpoint
                if not tile.getCheckpoint():
                    allowed = True
                    #Surrounding tile positions
                    around = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                    #Iterate for surrounding
                    for a in around:
                        #Get the tile
                        checkTile = None
                        if yPos + a[1] >= 0 and yPos + a[1] < len(array) and xPos + a[0] >= 0 and xPos + a[0] < len(array[0]):
                            checkTile = array[yPos + a[1]][xPos + a[0]]
                        #If there is a tile there
                        if checkTile != None:
                            #If there isn't a trap there
                            if not checkTile.getTrap() and not checkTile.getGoal():
                                #If a connection cannot be made to the start
                                if not checkConnect(array, startTile ,[xPos + a[0], yPos + a[1]], [xPos, yPos]):
                                    #The trap cannot be placed here
                                    allowed = False

                    #If the trap can be placed here
                    if allowed:
                        #Add the trap
                        added = True
                        tile.addTrap()
                        #Remove the quadrant from the options
                        del quads[rQ]


def addSwamps(array, swamps, startTile, endTile, x, y):
    '''Adds a number of swamps to the map'''
    #Cannot put a swamp at the start or end
    disallowedSpaces = [startTile, endTile]
    
    #Get data about tiles surrounding the start
    aroundStart, aroundStartDir = getAllAround(array, startTile)
    
    #Iterate through surrounding tiles
    for i in range(0, len(aroundStart)):
        #If there is not a wall to block
        if not array[startTile[1]][startTile[0]].getWalls()[aroundStartDir[i]]:
            #Cannot place check point here
            disallowedSpaces.append([aroundStart[i][0], aroundStart[i][1]])
    
    #Iterate for each swamp
    for i in range(0, swamps):
        #Not added yet
        added = False
        attempt = 0
        #Repeat until added or 100 tries reached
        while not added and attempt < 100:
            #Get a random tile
            xPos = random.randrange(0, x)
            yPos = random.randrange(0, y)
            tile = array[yPos][xPos]
            #If this isn't the start, end or not a tile
            if [xPos, yPos] not in disallowedSpaces:
                #If there is nothing there already
                if not tile.getGoal() and not tile.getCheckpoint() and not tile.getSwamp() and not tile.getTrap():
                    #Add the swamp
                    tile.addSwamp()
                    added = True
            #Increment counter
            attempt = attempt + 1


def generateHumanSpaces(array, x, y):
    '''Generate a list of wall groups with directions'''
    wallGroups = []
    
    #Two directional lists of walls
    currentGroup = []
    currentGroupOther = []
    
    #Iterate through each tile (left to right, top to bottom)
    for yPos in range(0, y):
        for xPos in range(0, x):
            #Get this tile
            cTile = array[yPos][xPos]
            #If this has an upper wall and no special tile states
            if cTile.getWalls()[0] and not cTile.getTrap() and not cTile.getCheckpoint() and not cTile.getSwamp() and not cTile.getGoal():
                #Add this tile to the list of tiles
                currentGroup.append(cTile)
            #Otherwise if there are tiles in the group
            elif len(currentGroup) != 0:
                #Add group to list with upper direction
                wallGroups.append([0, currentGroup])
                currentGroup = []
            #If there is a wall on the right
            if cTile.getWalls()[1] and len(currentGroup) != 0:
                #End the group and add to the list with direction
                wallGroups.append([0, currentGroup])
                currentGroup = []
            #If the end of the row has been reached
            if xPos == x + 1:
                #If there are tiles in the group
                if len(currentGroup) != 0:
                    #Add to list of groups with direction
                    wallGroups.append([0, currentGroup])
                #End group
                currentGroup = []
            
            #If this has a lower wall and no special tile states
            if cTile.getWalls()[2] and not cTile.getTrap() and not cTile.getCheckpoint() and not cTile.getSwamp() and not cTile.getGoal():
                #Add this tile to the list of tiles
                currentGroupOther.append(cTile)
            #Otherwise if there are tiles in the group
            elif len(currentGroupOther) != 0:
                #Add group to list with down direction
                wallGroups.append([2, currentGroupOther])
                currentGroupOther = []
            #If there is a wall on the right
            if cTile.getWalls()[1] and len(currentGroupOther) != 0:
                #End the group and add to the list with direction
                wallGroups.append([2, currentGroupOther])
                currentGroupOther = []
            #If the end of the row has been reached
            if xPos == x + 1:
                #If there are tiles in the group
                if len(currentGroupOther) != 0:
                    #Add to list of groups with direction
                    wallGroups.append([2, currentGroupOther])
                #End group
                currentGroupOther = []
    
    #Iterate through each tile (top to bottom, left to right)    
    for xPos in range(0, x):
        for yPos in range(0, y):
            #Get this tile
            cTile = array[yPos][xPos]
            #If this has a right wall and no special tile states
            if cTile.getWalls()[1] and not cTile.getTrap() and not cTile.getCheckpoint() and not cTile.getSwamp() and not cTile.getGoal():
                #Add this tile to the list of tiles
                currentGroup.append(cTile)
            #Otherwise if there are tiles in the group
            elif len(currentGroup) != 0:
                #Add group to list with right direction
                wallGroups.append([1, currentGroup])
                currentGroup = []
            #If there is a wall on the bottom
            if cTile.getWalls()[2] and len(currentGroup) != 0:
                #End the group and add to the list with direction
                wallGroups.append([1, currentGroup])
                currentGroup = []
            #If the end of the column has been reached
            if yPos == y + 1:
                #If there are tiles in the group
                if len(currentGroup) != 0:
                    #Add to list of groups with direction
                    wallGroups.append([1, currentGroup])
                #End group
                currentGroup = []
            
            cTile = array[yPos][xPos]
            #If this has a left wall and no special tile states
            if cTile.getWalls()[3] and not cTile.getTrap() and not cTile.getCheckpoint() and not cTile.getSwamp() and not cTile.getGoal():
                #Add this tile to the list of tiles
                currentGroupOther.append(cTile)
            #Otherwise if there are tiles in the group
            elif len(currentGroupOther) != 0:
                #Add group to list with left direction
                wallGroups.append([3, currentGroupOther])
                currentGroupOther = []
            #If there is a wall on the bottom
            if cTile.getWalls()[2] and len(currentGroupOther) != 0:
                #End the group and add to the list with direction
                wallGroups.append([3, currentGroupOther])
                currentGroupOther = []
            #If the end of the column has been reached
            if yPos == y + 1:
                #If there are tiles in the group
                if len(currentGroupOther) != 0:
                    #Add to list of groups with direction
                    wallGroups.append([3, currentGroupOther])
                #End group
                currentGroupOther = []
    
    #Return the list of wall groups
    return wallGroups


def addHumans (array, numberVisual, numberThermal, x, y):
    '''Add the specified number of humans to the array'''
    #List to hold all humans to add
    toAdd = []
    
    #For each of the visual humans
    for i in range(0, numberVisual):
        #Pick a random type (1 - harmed, 2 - unharmed, 3 - stable)
        toAdd.append(random.randrange(1, 4))
    
    #For each of the thermal humans
    for i in range(0, numberThermal):
        #Add a thermal
        toAdd.append(4)
        
    humansPlaced = [0, 0]
    
    #If there are humans to add
    if len(toAdd) > 0:
    
        #Scramble order (so that if some cannot be added it is not all thermal missing)
        for i in range(0, 200):
            #Random positions
            r1 = random.randrange(0, len(toAdd))
            r2 = random.randrange(0, len(toAdd))
            #Temporary store item 1
            temp = toAdd[r1]
            #Place item 2
            toAdd[r1] = toAdd[r2]
            #Place item 1
            toAdd[r2] = temp
        
        #Groups of walls to place humans on
        wallGroupData = generateHumanSpaces(array, x, y)
        used = []
        
        #Iterate for every human
        for h in toAdd:
            #Not added yet, give 200 attempts
            added = False
            attempts = 200
            
            #While still trying to add
            while not added and attempts > 0:
                #Decreate attempt amount
                attempts = attempts - 1
                #Random wall group
                r = random.randrange(0, len(wallGroupData))
                #If that group is unused
                if r not in used:
                    #Get the group data
                    group = wallGroupData[r][1]
                    #Randomly select a tile in that group
                    tile = group[random.randrange(0, len(group))]
                    #Attempt to add a human
                    success = tile.addHuman(h, wallGroupData[r][0])
                    #If added successfully
                    if success:
                        added = True
                        #Increment human counters
                        if h < 4:
                            #Visual
                            humansPlaced[0] = humansPlaced[0] + 1
                        else:
                            #Thermal
                            humansPlaced[1] = humansPlaced[1] + 1
                        
                        #Add position to used list
                        used.append(r)
                
                #If all the groups have been used
                if len(used) >= len(wallGroupData):
                    #Reset for second pass
                    used = []
    
    #Return the numbers of humans placed
    return humansPlaced


def generateWorld(x, y, checkpoints, traps, swamps, visual, thermal):
    '''Perform generation of a world array'''
    #Create the empty array
    array = createEmptyWorld(x, y)

    #Pick a starting edge
    startEdge = random.randrange(0, 4)
    xStart = 0
    yStart = 0

    startDir = 0

    #Top edge
    if startEdge == 0:
        #Pick start position
        yStart = 0
        xStart = random.randrange(0, len(array[0]))
        #Set start direction
        startDir = 2
    #Right edge
    if startEdge == 1:
        #Pick start position
        xStart = len(array[0]) - 1
        yStart = random.randrange(0, len(array))
        #Set start direction
        startDir = 3
    #Bottom edge
    if startEdge == 2:
        #Pick start position
        yStart = len(array) - 1
        xStart = random.randrange(0, len(array[0]))
        #Set start direction
        startDir = 0
    #Left edge
    if startEdge == 3:
        #Pick start position
        xStart = 0
        yStart = random.randrange(0, len(array))
        #Set start direction
        startDir = 1
    
    #Take a record of the position of the start tile in the maze
    startTile = [xStart, yStart]
    
    #Add starting tile to start position
    array[startTile[1]][startTile[0]].addGoal()
    
    #Calculate minimum orthogonal distance between start and end
    minDistance = min(10, int((x + y) / 2) + 1)
    possibleEnd = []

    #Iterate horizontal edges
    for xEnd in range(0, len(array[0])):
        for yEnd in [0, len(array) - 1]:
            #Test if distance is enough
            if abs(xStart - xEnd) + abs(yStart - yEnd) - 1 >= minDistance:
                #Add to possible end points
                possibleEnd.append([xEnd, yEnd])

    #Iterate vertical edges
    for yEnd in range(0, len(array)):
        for xEnd in [0, len(array[0]) - 1]:
            #Test if distance is enough
            if abs(xStart - xEnd) + abs(yStart - yEnd) - 1 >= minDistance:
                #Add to possible end points
                possibleEnd.append([xEnd, yEnd])

    endTile = [0, 0]

    #If there are some possible end points
    if len(possibleEnd) > 0:
        #Get an end position (chosen randomly)
        xEnd, yEnd = possibleEnd[random.randrange(0, len(possibleEnd))]
        endTile = [xEnd, yEnd]

    #Generate maze
    depthFirstMaze(array, startTile)

    #Open some random spaces
    for i in range(0, int((x + y) / 2) ** 2):
        #Random position
        randX = random.randrange(0, len(array[0]))
        randY = random.randrange(0, len(array))
        #Get the valid directions
        allowedDirs = getAllAround(array, [randX, randY])[1]
        #If there are some positions that can be opened
        if len(allowedDirs) > 0:
            #Get a direction to open
            d = allowedDirs[random.randrange(0, len(allowedDirs))]
            #Open that direction (if it is already open it will do nothing)
            openSurround(array, [randX, randY], d)

    #Add checkpoints
    addCheckPoints(array, checkpoints, startTile, endTile, x, y)

    #Add traps
    addTraps(array, traps, startTile, endTile, x, y)
    
    #Add swamps
    addSwamps(array, swamps, startTile, endTile, x, y)
    
    #Add humans
    humansAdded = addHumans(array, visual, thermal, x, y)

    #Return the array, start position and humans
    return array, [startTile, startDir], humansAdded[0], humansAdded[1]


def addObstacle(debris):
    '''Generate random dimensions for an obstacle'''
    #Default height for static obstacle
    height = 0.15
    #Adjust height for debris
    if debris:
        height = 0.01
    #Default size contstraints for static obstacle
    minSize = 5
    maxSize = 20
    #Adjust size constraints for debris
    if debris:
        minSize = 2
        maxSize = 5
    #Generate random size
    width = float(random.randrange(minSize, maxSize)) / 100.0
    depth = float(random.randrange(minSize, maxSize)) / 100.0
    #Create obstacle
    obstacle = [width, height, depth, debris]
    return obstacle
    
    
def getTileAroundBlocking(array, xPos, yPos):
    '''Returns a list of whether there is something blocking surrounding tiles [up, right, down, left]'''
    #Surrounding tile offsets
    around = [[0, -1], [1, 0], [0, 1], [-1, 0]]
    
    #Default values - nothing
    wallBlocks = [False, False, False, False]
    
    #Get the target tile
    tile = array[yPos][xPos]
    
    #If this isn't a tile
    if tile == None:
        #Return all blocked
        return [True, True, True, True]
    
    #Get the tile's walls
    walls = tile.getWalls()
    
    #Iterate for four directions
    for d in range(0, len(around)):
        #If there is a wall
        if walls[d]:
            #It is blocked
            wallBlocks[d] = True
        else:
            #If there isn't a wall
            #Get the tile that is adjacent in the current direction
            otherTile = array[yPos + around[d][1]][xPos + around[d][0]]
            #If there is not a tile there
            if otherTile == None:
                #That direction is blocked
                wallBlocks[d] = True
            else:
                #If there is a checkpoint, trap or swamp in that direction
                if otherTile.getCheckpoint() or otherTile.getTrap() or otherTile.getSwamp():
                    #It is blocked
                    wallBlocks[d] = True
    
    #return the blocked state of the directions
    return wallBlocks


def getStartTileFromBay(startPos):
    '''Convert from start bay position and direction to first tile in maze position'''
    #Facing up
    if startPos[1] == 0:
        return [startPos[0][0], startPos[0][1] - 1]
    #Facing right
    if startPos[1] == 1:
        return [startPos[0][0] + 1, startPos[0][1]]
    #Facing down
    if startPos[1] == 2:
        return [startPos[0][0], startPos[0][1] + 1]
    #Facing left
    if startPos[1] == 3:
        return [startPos[0][0] - 1, startPos[0][1]]
    
    #Return the same if invalid direction given
    return [startPos[0][0], startPos[0][1]]


def selectObstaclePositon(obstacle, array, x, y, obstacles, startPos):
    '''Select a valid position for the obstacle [x, y, z, rotation, radius]'''
    #Calculate radius of obstacle
    r = (((obstacle[0] / 2.0) ** 2) + ((obstacle[2] / 2.0) ** 2)) ** 0.50
    #Not selected a valid tile yet
    tSelected = None
    
    #Starting position for tiles
    startX = -((x + 1) * 0.3 / 2.0)
    startZ = -((y + 1) * 0.3 / 2.0)
    
    #The array position of the selected tile - none yet
    tPos = [0, 0]
    #100 attempts
    att = 100
    
    #Calculate the starting tile (so it is not obscured)
    startTile = getStartTileFromBay(startPos)
    
    #Repeat until a tile is found or all attempts exhausted
    while tSelected == None and att > 0:
        #Decrement attempts
        att -= 1
        #Get random tile position
        tPos = [random.randrange(0, x), random.randrange(0, y)]
        #Get the tile (offset for start of grid)
        tile = array[tPos[1]][tPos[0]]
        #If this is a tile and not the start point
        if tile != None and startTile != [tPos[0], tPos[1]]:
            #If it is not a special tile and does not contain an obstacle already
            if not tile.getCheckpoint() and not tile.getTrap() and not tile.getSwamp() and not tile.getObstacle() and not tile.getGoal():
                #Target tile found
                tSelected = tile
    
    #If no tile was selected
    if tSelected == None:
        #Return default position (not in maze)
        return [0, -1000, 0, 0, r]
    
    #Boundaries of tile to pick
    xBounds = [-0.15, 0.15]
    zBounds = [-0.15, 0.15]
    
    #Get the surrounding blocks
    walls = getTileAroundBlocking(array, tPos[0], tPos[1])
    
    #Get the centre position of the tile
    tPos = [(tPos[0] * 0.3) + startX, (tPos[1] * 0.3) + startZ]
    
    #Adjust away from present walls by the wall thickness and the radius
    if walls[0]:
        zBounds[0] = zBounds[0] + 0.015 + r
    if walls[2]:
        zBounds[1] = zBounds[1] - 0.015 - r
    if walls[1]:
        xBounds[1] = xBounds[1] - 0.015 - r
    if walls[3]:
        xBounds[0] = xBounds[0] + 0.015 + r
    
    #Selected position
    pos = [0, 0]
    #If it has been placed
    done = False
    att = 200
    
    #Repeat until a place has been found or no attempts are left
    while not done and att > 0:
        #Decrement attempts
        att -= 1
        #Get a random position
        pos = [round(random.uniform(xBounds[0], xBounds[1]), 5), round(random.uniform(zBounds[0], zBounds[1]), 5)]
        #Offset with tile position
        pos[0] = pos[0] + tPos[0]
        pos[1] = pos[1] + tPos[1]
        allowed = True
        #Iterate through placed obstacles
        for obs in obstacles:
            #If the obstacle is in the map
            if obs[0][1] > -1:
                #Get the x and z distances between the obstacles
                xDist = abs(pos[0] - obs[1][0])
                zDist = abs(pos[1] - obs[1][2])
                #If the total distance is less than their combined radius
                if (((xDist ** 2) + (zDist ** 2)) ** (0.5)) < r + obs[1][4]:
                    #They intersect and the obstacle cannot be placed here
                    allowed = False
        
        #If there is no reason to disallow this place
        if allowed:
            #It has been successfully placed
            done = True
    
    #If it has not been placed
    if not done:
        #Return default position (not in maze)
        return [0, -1000, 0, 0, r]
    
    #Random rotation for obstacle
    rot = round(random.uniform(0.00, 6.28), 3)
    
    #Add an obstacle to the selected tile
    tSelected.addObstacle()
    
    #Return the position data for the tile
    return [pos[0], 0, pos[1], rot, r]


def generateObstacles(bulky, debris, array, x, y, startPos):
    '''Generate a list of obstacles of length numObstacles'''
    #List to hold obstacle dimensions
    obstacles = []
    #How many obstacles have actually been placed
    placedBulky = 0
    placedDebris = 0
    
    #Iterate for each static obstacle
    for i in range(0, bulky):
        #Create an obstacle and add it to the list
        newObstacle = addObstacle(False)
        newObstaclePos = selectObstaclePositon(newObstacle, array, x, y, obstacles, startPos)
        if newObstaclePos[1] > -1:
            placedBulky = placedBulky + 1
        obstacles.append([newObstacle, newObstaclePos])

    #Iterate for each piece of debris
    for i in range(0, debris):
        #Create an obstacle and add it to the list
        newObstacle = addObstacle(True)
        obstacles.append([newObstacle, [0, -1000, 0, 0, 0]])

    #Return the list of dimensions
    return obstacles, placedBulky, placedDebris


def generatePlan (xSize, ySize, numCheckpoints, numTraps, bulkyObstacles, debris, numSwamps, numVisualHumans, numThermalHumans):
    '''Perform a map generation up to png - does not update map file'''
    #Generate the world and tree
    world, startPos, numVisual, numThermal = generateWorld(xSize, ySize, numCheckpoints, numTraps, numSwamps, numVisualHumans, numThermalHumans)
	
    #Create a list of obstacles
    obstacles, placedBulky, placedDebris = generateObstacles(bulkyObstacles, debris, world, xSize, ySize, startPos)

    #Output the world as a picture
    printWorld(world)

    print("Generation Successful")

    #Return generated parts
    return world, obstacles, startPos, numVisual, numThermal, placedBulky, placedDebris


def generateWorldFile (world, obstacles, startPos, window):
    #Array of wall tiles
    walls = []

    #Iterate vertically
    for y in range(0, len(world) + 1):
        #Create a row
        row = []
        #Iterate horizontally
        for x in range(0, len(world[0]) + 1):
            #Add each tile [present, [uWall,rWall,dWall,lWall], checkpoint, trap, goal, swamp, humanType, humanWall]
            row.append([False, [False, False, False, False], False, False, False, False, 0, 0])
        #Add row to array
        walls.append(row)

    #Iterate for each of the tiles
    for y in range(0, len(world)):
        for x in range(0, len(world[0])):
            #If there is a tile there
            if world[y][x] != None:
                #Get the human data
                humanInfo = world[y][x].getHumanData()
                #Add the wall data
                walls[y][x] = [True, world[y][x].getWalls(), world[y][x].getCheckpoint(), world[y][x].getTrap(), world[y][x].getGoal(), world[y][x].getSwamp(), humanInfo[0], humanInfo[1]]

    #Make a map from the walls and objects
    WorldCreator.makeFile(walls, obstacles, startPos, window)


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
printWorld(createEmptyWorld(1, 1))


#Create an instacnce of the user interface
window = GUI.GenerateWindow()

#The UI is currently in use
guiActive = True

#Set all generation parameters to Nones
world = None
obstacles = None
thermalHumans = None
visualHumans = None
startTilePos = None
placedBulky = None
placedDebris = None

#Loop while the UI is active
while guiActive:

    #If a generation is being called for
    if window.ready:
        #Cannot save now
        window.setSaveButton(False)
        #Get generation values as follows:
        #[[xSize ySize], [thermal, visual], [bulky, debris], [checkpoints, traps, swamps]]
        genValues = window.getValues()
        #A generation has started (resets flag so generation is not called again)
        window.generateStarted()
        #Unpack the human values
        thermalHumans, visualHumans = genValues[1][0], genValues[1][1]
        #Generate a plan with the values
        world, obstacles, startTilePos, visualHumans, thermalHumans, placedBulky, placedDebris = generatePlan(genValues[0][0], genValues[0][1], genValues[3][0], genValues[3][1], genValues[2][0], genValues[2][1], genValues[3][2], visualHumans, thermalHumans)
        #Unpack the used obstacle counts
        bulkyObstacles, debris = genValues[2][0], genValues[2][1]
        #Update the UI image of the map
        window.updateImage()

        #Update the output fields of the window
        window.setGeneratedInformation("Thermal: " + str(thermalHumans), "Visual: " + str(visualHumans), "Bulky: " + str(placedBulky) + "(" + str(bulkyObstacles) +")", "Debris: " + str(placedDebris) + "(" + str(debris) +")")

    #If a save file is being called for
    if window.saving:
        #Cannot save now
        window.setSaveButton(False)
        #Saving has begin (resets flag so save is not called twice)
        window.saveStarted()
        #If all values that are needed are not None
        if checkNoNones([world, obstacles, startTilePos, thermalHumans, visualHumans, placedBulky, placedDebris]):
            #Generate and save a world
            generateWorldFile(world, obstacles, startTilePos, window)

    #Attempt update loops           
    try:
        #Toggle the save button to the correct state
        window.setSaveButton(checkNoNones([world, obstacles, thermalHumans, visualHumans, startTilePos, placedBulky, placedDebris]))
        #Update loops for the UI - manually called to prevent blocking of this program
        window.update_idletasks()
        window.update()
    #If an error occurred in the update (window closed)
    except:
        #Terminate the UI loop
        guiActive = False
