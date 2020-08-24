"""Map Generation World File Creator Type 2 v4
   Written by Robbie Goldman and Alfred Roberts

Changelog:
 Type 1
 V2:
 - Added Group node for walls
 - Incorporated obstacles into file
 V3:
 - Allows user to select where they want the file to be saved
 - Added children (human special type)
 V4:
 - Bases now generate into their own separate group
 V5:
 - Added boundary nodes for rooms
 V6:
 - Added position nodes for doors
 Type 2
 V1:
 - Overhauled to change from a floor and external walls into modular pieces
 V2:
 - Changed to use proto nodes for tiles
 v3:
 - Removed robots from generation (commended out if needed)
 v4:
 - Updated to scale tiles
"""


from decimal import Decimal
import os
import random
dirname = os.path.dirname(__file__)

#General scale for tiles - adjusts position and size of pieces and obstacles
tileScale = [0.4, 0.4, 0.4]
#The vertical position of the floor
floorPos = -0.075 * tileScale[1]

def checkForCorners(pos, walls):
    '''Check if each of the corners is needed'''
    #Surrounding tile directions
    around = [[0, -1], [1, 0], [0, 1], [-1, 0]]
    #Needed corners
    corners = [False, False, False, False]

    surroundingTiles = []

    thisWall = walls[pos[1]][pos[0]]

    if not thisWall[0]:
        return corners

    #For each surrounding card
    for a in around:
        #Get the position
        xPos = pos[0] + a[0]
        yPos = pos[1] + a[1]
        #If it is a valid position
        if xPos > -1 and xPos < len(walls[0]) and yPos > -1 and yPos < len(walls):
            #Add the tile to the surrounding list
            surroundingTiles.append(walls[yPos][xPos])
        else:
            #Otherwise add a null value
            surroundingTiles.append([False, [False, False, False, False], False, False, False])

    #If top right is needed
    corners[0] = surroundingTiles[0][1][1] and surroundingTiles[1][1][0] and not thisWall[1][0] and not thisWall[1][1]
    #If bottom right is needed
    corners[1] = surroundingTiles[1][1][2] and surroundingTiles[2][1][1] and not thisWall[1][1] and not thisWall[1][2]
    #If bottom left is needed
    corners[2] = surroundingTiles[2][1][3] and surroundingTiles[3][1][2] and not thisWall[1][2] and not thisWall[1][3]
    #If top left is needed
    corners[3] = surroundingTiles[0][1][3] and surroundingTiles[3][1][0] and not thisWall[1][3] and not thisWall[1][0]

    return corners


def checkForExternalWalls (pos, walls):
    '''Convert tile position to a list of bools for needed external walls'''
    #Get the tile at the position
    thisWall = walls[pos[1]][pos[0]]

    #If there is no tile here there is no need for an external wall
    if not thisWall[0]:
        return [False, False, False, False]

    #Surrounding tiles
    around = [[0, -1], [1, 0], [0, 1], [-1, 0]]
    otherTiles = [False, False, False, False]

    d = 0

    for a in around:
        #Get the tiles position
        xPos = pos[0] + a[0]
        yPos = pos[1] + a[1]
        #If it is a valid positon
        if xPos > -1 and xPos < len(walls[0]) and yPos > -1 and yPos < len(walls):
            #Add the tiles present data
            otherTiles[d] = walls[yPos][xPos][0]
        else:
            #No tile present
            otherTiles[d] = False
        #Add one to direction counter
        d = d + 1

    #Convert to needed walls
    externalsNeeded = [not otherTiles[0], not otherTiles[1], not otherTiles[2], not otherTiles[3]]
    return externalsNeeded


def checkForNotch (pos, walls):
    '''Determine if a notch is needed on either side'''
    #Variables to store if each notch is needed
    needLeft = False
    needRight = False

    #No notches needed if there is not a floor
    if not walls[pos[1]][pos[0]][0]:
        return False, False, 0

    rotations = [3.14159, 1.57079, 0, -1.57079]

    #Surrounding tiles
    around = [[0, -1], [1, 0], [0, 1], [-1, 0]]
    #Tiles to check if notches are needed
    notchAround = [[ [1, -1], [-1, -1] ],
                   [ [1, 1], [1, -1] ],
                   [ [-1, 1], [1, 1] ],
                   [ [-1, -1], [-1, 1] ]]

    #Current direction
    d = 0
    #Number of surrounding tiles
    surround = 0

    #Direction of present tile
    dire = -1

    #Iterate for surrounding tiles
    for a in around:
        #If x axis is within array
        if pos[0] + a[0] < len(walls[0]) and pos[0] + a[0] > -1:
            #If y axis is within array
            if pos[1] + a[1] < len(walls) and pos[1] + a[1] > -1:
                #If there is a tile there
                if walls[pos[1] + a[1]][pos[0] + a[0]][0]:
                    #Add to number of surrounding tiles
                    surround = surround + 1
                    #Store direction
                    dire = d
        #Increment direction
        d = d + 1

    rotation = 0

    #If there was only one connected tile and there is a valid stored direction
    if surround == 1 and dire > -1 and dire < len(notchAround):
        #Get the left and right tile positions to check
        targetLeft = [pos[0] + notchAround[dire][0][0], pos[1] + notchAround[dire][0][1]]
        targetRight = [pos[0] + notchAround[dire][1][0], pos[1] + notchAround[dire][1][1]]

        #If the left tile is a valid target position
        if targetLeft[0] < len(walls[0]) and targetLeft[0] > -1 and targetLeft[1] < len(walls) and targetLeft[1] > -1:
            #If there is no tile there
            if not walls[targetLeft[1]][targetLeft[0]][0]:
                #A left notch is needed
                needLeft = True

        #If the right tile is a valid target position
        if targetRight[0] < len(walls[0]) and targetRight[0] > -1 and targetRight[1] < len(walls) and targetRight[1] > -1:
            #If there is no tile there
            if not walls[targetRight[1]][targetRight[0]][0]:
                #A right notch is needed
                needRight = True

        rotation = rotations[dire]

    #Return information about needed notches
    return needLeft, needRight, rotation


def createFileData (walls, obstacles, startPos):
    '''Create a file data string from the positions and scales'''
    #Open the file containing the standard header
    headerFile = open(os.path.join(dirname, "fileHeader.txt"), "r")
    #Read header
    fileHeader = headerFile.read()
    #Close header file
    headerFile.close()

    #Open the file containing the template for a group
    groupTemplate = open(os.path.join(dirname, "groupTemplate.txt"), "r")
    #Read template
    groupPart = groupTemplate.read()
    #Close template file
    groupTemplate.close()

    #Open the file containing the template for a robot
    robotTemplate = open(os.path.join(dirname, "robotTemplate.txt"), "r")
    #Read template
    robotPart = robotTemplate.read()
    #Close template file
    robotTemplate.close()

    #Open the file containing the template for a proto tile
    protoTileTemplate = open(os.path.join(dirname, "protoTileTemplate.txt"), "r")
    #Read template
    protoTilePart = protoTileTemplate.read()
    #Close template file
    protoTileTemplate.close()

    #Open the file containing the template for a boundary
    boundsTemplate = open(os.path.join(dirname, "boundsTemplate.txt"), "r")
    #Read template
    boundsPart = boundsTemplate.read()
    #Close template file
    boundsTemplate.close()

    #Open the file containing the template for the obstacles
    obstacleTemplate = open(os.path.join(dirname, "obstacleTemplate.txt"), "r")
    #Read template
    obstaclePart = obstacleTemplate.read()
    #Close template file
    obstacleTemplate.close()

    #Open the file containing the template for the debris
    debrisTemplate = open(os.path.join(dirname, "debrisTemplate.txt"), "r")
    #Read template
    debrisPart = debrisTemplate.read()
    #Close template file
    debrisTemplate.close()

    #Open the file containing the template for the supervisor
    supervisorTemplate = open(os.path.join(dirname, "supervisorTemplate.txt"), "r")
    #Read template
    supervisorPart = supervisorTemplate.read()
    #Close template file
    supervisorTemplate.close()

    #Open the file containing the template for the visual humans
    visualHumanTemplate = open(os.path.join(dirname, "visualHumanTemplate.txt"), "r")
    #Read template
    visualHumanPart = visualHumanTemplate.read()
    #Close template file
    visualHumanTemplate.close()

    #Open the file containing the template for the thermal humans
    thermalHumanTemplate = open(os.path.join(dirname, "thermalHumanTemplate.txt"), "r")
    #Read template
    thermalHumanPart = thermalHumanTemplate.read()
    #Close template file
    thermalHumanTemplate.close()


    #Create file data - initialy just the header
    fileData = fileHeader

    #Strings to hold the tile parts
    allTiles = ""
    #Strings to hold the boundaries for special tiles
    allCheckpointBounds = ""
    allTrapBounds = ""
    allGoalBounds = ""
    allSwampBounds = ""

    #String to hold all the humans
    allHumans = ""

    #Upper left corner to start placing tiles from
    width = len(walls[0])
    height = len(walls)
    startX = -(len(walls[0]) * (0.3 * tileScale[0]) / 2.0)
    startZ = -(len(walls) * (0.3 * tileScale[2]) / 2.0)

    #Rotations of humans for each wall
    humanRotation = [3.14, 1.57, 0, -1.57]
    #Offsets for visual and thermal humans
    humanOffset = [[0, -0.1375 * tileScale[2]], [0.1375 * tileScale[0], 0], [0, 0.1375 * tileScale[2]], [-0.1375 * tileScale[0], 0]]
    humanOffsetThermal = [[0, -0.136 * tileScale[2]], [0.136 * tileScale[0], 0], [0, 0.136 * tileScale[2]], [-0.136 * tileScale[0], 0]]
    #Names of types of visual human
    humanTypesVisual = ["harmed", "unharmed", "stable"]

    #Id numbers used to give a unique but interable name to tile pieces
    tileId = 0
    checkId = 0
    trapId = 0
    goalId = 0
    swampId = 0
    humanId = 0

    #Iterate through all the tiles
    for x in range(0, len(walls[0])):
        for z in range(0, len(walls)):
            #Check which corners and external walls and notches are needed
            corners = checkForCorners([x, z], walls)
            externals = checkForExternalWalls([x, z], walls)
            notchData = checkForNotch([x, z], walls)
            notch = ""
            #Name to be given to the tile
            tileName = "TILE"
            if walls[z][x][4]:
                tileName = "START_TILE"
            #Set notch string to correct value
            if notchData[0]:
                notch = "left"
            if notchData[1]:
                notch = "right"
            #Create a new tile with all the data
            tile = protoTilePart.format(tileName, x, z, walls[z][x][0] and not walls[z][x][3], walls[z][x][1][0], walls[z][x][1][1], walls[z][x][1][2], walls[z][x][1][3], corners[0], corners[1], corners[2], corners[3], externals[0], externals[1], externals[2], externals[3], notch, notchData[2], walls[z][x][4], walls[z][x][3], walls[z][x][2], walls[z][x][5], width, height, tileId, tileScale[0], tileScale[1], tileScale[2])
            tile = tile.replace("True", "TRUE")
            tile = tile.replace("False", "FALSE")
            allTiles = allTiles + tile
            #checkpoint
            if walls[z][x][2]:
                #Add bounds to the checkpoint boundaries
                allCheckpointBounds = allCheckpointBounds + boundsPart.format("checkpoint", checkId, (x * 0.3 * tileScale[0] + startX) - (0.15 * tileScale[0]), (z * 0.3 * tileScale[2] + startZ) - (0.15 * tileScale[2]), (x * 0.3 * tileScale[0] + startX) + (0.15 * tileScale[0]), (z * 0.3 * tileScale[2] + startZ) + (0.15 * tileScale[2]), floorPos)
                #Increment id counter
                checkId = checkId + 1

            #trap
            if walls[z][x][3]:
                #Add bounds to the trap boundaries
                allTrapBounds = allTrapBounds + boundsPart.format("trap", trapId, (x * 0.3 * tileScale[0] + startX) - (0.15 * tileScale[0]), (z * 0.3 * tileScale[2] + startZ) - (0.15 * tileScale[2]), (x * 0.3 * tileScale[0] + startX) + (0.15 * tileScale[0]), (z * 0.3 * tileScale[2] + startZ) + (0.15 * tileScale[2]), floorPos)
                #Increment id counter
                trapId = trapId + 1

            #goal
            if walls[z][x][4]:
                #Add bounds to the goal boundaries
                allGoalBounds = allGoalBounds + boundsPart.format("start", goalId, (x * 0.3 * tileScale[0] + startX) - (0.15 * tileScale[0]), (z * 0.3 * tileScale[2] + startZ) - (0.15 * tileScale[2]), (x * 0.3 * tileScale[0] + startX) + (0.15 * tileScale[0]), (z * 0.3 * tileScale[2] + startZ) + (0.15 * tileScale[2]), floorPos)
                #Increment id counter
                goalId = goalId + 1
            #swamp
            if walls[z][x][5]:
                #Add bounds to the swamp boundaries
                allSwampBounds = allSwampBounds + boundsPart.format("swamp", swampId, (x * 0.3 * tileScale[0] + startX) - (0.15 * tileScale[0]), (z * 0.3 * tileScale[2] + startZ) - (0.15 * tileScale[2]), (x * 0.3 * tileScale[0] + startX) + (0.15 * tileScale[0]), (z * 0.3 * tileScale[2] + startZ) + (0.15 * tileScale[2]), floorPos)
                #Increment id counter
                swampId = swampId + 1
            #Increment id counter
            tileId = tileId + 1

            #Human
            if walls[z][x][6] != 0:
                #Position of tile
                humanPos = [(x * 0.3 * tileScale[0]) + startX , (z * 0.3 * tileScale[2]) + startZ]
                humanRot = humanRotation[walls[z][x][7]]
                #Randomly move human left and right on wall
                randomOffset = [0, 0]
                if walls[z][x][7] in [0, 2]:
                    #X offset for top and bottom
                    randomOffset = [round(random.uniform(-0.08 * tileScale[0], 0.08 * tileScale[0]), 3), 0]
                else:
                    #Z offset for left and right
                    randomOffset = [0, round(random.uniform(-0.08 * tileScale[2], 0.08 * tileScale[2]), 3)]
                #Thermal
                if walls[z][x][6] == 4:
                    humanPos[0] = humanPos[0] + humanOffsetThermal[walls[z][x][7]][0] + randomOffset[0]
                    humanPos[1] = humanPos[1] + humanOffsetThermal[walls[z][x][7]][1] + randomOffset[1]
                    score = 30
                    if walls[z][x][8]:
                        score = 10
                    allHumans = allHumans + thermalHumanPart.format(humanPos[0], humanPos[1], humanRot, humanId, score)
                else:
                    humanPos[0] = humanPos[0] + humanOffset[walls[z][x][7]][0] + randomOffset[0]
                    humanPos[1] = humanPos[1] + humanOffset[walls[z][x][7]][1] + randomOffset[1]
                    score = 30
                    if walls[z][x][8]:
                        score = 10
                    allHumans = allHumans + visualHumanPart.format(humanPos[0], humanPos[1], humanRot, humanId, humanTypesVisual[walls[z][x][6] - 1], score)

                humanId = humanId + 1





    #Add the data pieces to the file data
    fileData = fileData + groupPart.format(allTiles, "WALLTILES")
    fileData = fileData + groupPart.format(allCheckpointBounds, "CHECKPOINTBOUNDS")
    fileData = fileData + groupPart.format(allTrapBounds, "TRAPBOUNDS")
    fileData = fileData + groupPart.format(allGoalBounds, "STARTBOUNDS")
    fileData = fileData + groupPart.format(allSwampBounds, "SWAMPBOUNDS")

    #String to hold all the data for the obstacles
    allObstacles = ""
    allDebris = ""

    #Id to give a unique name to the obstacles
    obstacleId = 0
    debrisId = 0

    #Iterate obstalces
    for obstacle in obstacles:
        #If this is debris
        if obstacle[0][3]:
            #Add the debris object (scaled to world size)
            allDebris = allDebris + debrisPart.format(debrisId, obstacle[0][0] * tileScale[0], obstacle[0][1] * tileScale[1], obstacle[0][2] * tileScale[2])
            #Increment id counter
            debrisId = debrisId + 1
        else:
            #Add the obstacle (scaled and positioned based on world scale)
            allObstacles = allObstacles + obstaclePart.format(obstacleId, obstacle[0][0] * tileScale[0], obstacle[0][1] * tileScale[1], obstacle[0][2] * tileScale[2], obstacle[1][0] * tileScale[0], obstacle[1][1] * tileScale[1], obstacle[1][2] * tileScale[2], obstacle[1][3])
            #Increment id counter
            obstacleId = obstacleId + 1

    #Add obstacles and debris to the file
    fileData = fileData + groupPart.format(allObstacles, "OBSTACLES")
    fileData = fileData + groupPart.format(allDebris, "DEBRIS")

    #String to hold all the data for the robots (removed - now performed by supervisor)
    '''robotData = ""
    #If starting facing up
    if startPos[1] == 0:
        #Add robots (spaced -X, +X) and rotated
        robotData = robotData + robotPart.format(0, (startPos[0][0] * 0.3 + startX) - 0.075, startPos[0][1] * 0.3 + startZ, 0)
        robotData = robotData + robotPart.format(1, (startPos[0][0] * 0.3 + startX) + 0.075, startPos[0][1] * 0.3 + startZ, 0)
    #If starting facing right
    if startPos[1] == 1:
        #Add robots (spaced -Z, +Z) and rotated
        robotData = robotData + robotPart.format(0, startPos[0][0] * 0.3 + startX, (startPos[0][1] * 0.3 + startZ) - 0.075, -1.5708)
        robotData = robotData + robotPart.format(1, startPos[0][0] * 0.3 + startX, (startPos[0][1] * 0.3 + startZ) + 0.075, -1.5708)
    #If starting facing down
    if startPos[1] == 2:
        #Add robots (spaced +X, -X) and rotated
        robotData = robotData + robotPart.format(0, (startPos[0][0] * 0.3 + startX) + 0.075, startPos[0][1] * 0.3 + startZ, 3.14159)
        robotData = robotData + robotPart.format(1, (startPos[0][0] * 0.3 + startX) - 0.075, startPos[0][1] * 0.3 + startZ, 3.14159)
    #If starting facing left
    if startPos[1] == 3:
        #Add robots (spaced +Z, -Z) and rotated
        robotData = robotData + robotPart.format(0, startPos[0][0] * 0.3 + startX, (startPos[0][1] * 0.3 + startZ) + 0.075, 1.5708)
        robotData = robotData + robotPart.format(1, startPos[0][0] * 0.3 + startX, (startPos[0][1] * 0.3 + startZ) - 0.075, 1.5708)'''

    fileData = fileData + groupPart.format(allHumans, "HUMANGROUP")

    #Add the robot data to the file
    fileData = fileData + robotPart.format(0)

    #Add supervisors
    fileData = fileData + supervisorPart

    #Return the file data as a string
    return fileData


def makeFile(boxData, obstacles, startPos, uiWindow = None):
    '''Create and save the file for the information'''
    #Generate the file string for the map
    data = createFileData(boxData, obstacles, startPos)
    #The default file path
    filePath = os.path.join(dirname, "generatedWorld.wbt")

    #If there is a GUI window to use
    if uiWindow != None:
        #Get the path from the user
        path = uiWindow.getPathSelection()
        #Strip leading or trailing whitespace
        path = path.strip()
        #If there is a path
        if path != "":
            #If there isn't a .wbt extension on the file
            if not path.endswith(".wbt"):
                #Add the extension
                path = path + ".wbt"
            #Change the path to the one the user gave
            filePath = path
        else:
            return

    #Open the file to store the world in (cleared when opened)
    worldFile = open(filePath, "w")
    #Write all the information to the file
    worldFile.write(data)
    #Close the file
    worldFile.close()
