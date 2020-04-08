"""Map Generation World File Creator Type 2 v1
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
"""


from decimal import Decimal
import os
dirname = os.path.dirname(__file__)

#List of activity colours (could be generated in future)
activityColours = [[1, 0, 1], [0, 1, 1], [1, 1, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]


def transformFromBounds(start, end):
    '''Convert from a start and end wall point into a position and scale'''
    #Convert start and end to decimals - aids precision
    start = [Decimal(start[0]), Decimal(start[1])]
    end = [Decimal(end[0]), Decimal(end[1])]
    #Position is half the difference between the start and the end added to the start
    pos = [start[0] + ((end[0] - start[0]) / Decimal(2)), start[1] + ((end[1] - start[1]) / Decimal(2))]
    #Scale is the end take the start add 1
    scale = [end[0] - start[0] + Decimal(1), end[1] - start[1] + Decimal(1)]

    #Convert scale to .wbt space (divide by 10)
    scale[0] = scale[0] / Decimal(10)
    scale[1] = scale[1] / Decimal(10)
    #Convert pos to .wbt space (divide by 10 then shift (centered on 0))
    pos[0] = (pos[0] / Decimal(10)) - Decimal(12.45)
    pos[1] = (pos[1] / Decimal(10)) - Decimal(9.95)

    #Convert back to floating point values
    scale[0] = float(scale[0])
    scale[1] = float(scale[1])
    pos[0] = float(pos[0])
    pos[1] = float(pos[1])

    #Returnt the position and scale of the box
    return pos, scale


def checkForCorners(pos, walls):
    '''Check if each of the corners is needed'''
    #Surrounding tile directions
    around = [[0, -1], [1, 0], [0, 1], [-1, 0]]
    #Needed corners
    corners = [False, False, False, False]

    surroundingTiles = []

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
    corners[0] = surroundingTiles[0][1][1] and surroundingTiles[1][1][0]
    #If bottom right is needed
    corners[1] = surroundingTiles[1][1][2] and surroundingTiles[2][1][1]
    #If bottom left is needed
    corners[2] = surroundingTiles[2][1][3] and surroundingTiles[3][1][2]
    #If top left is needed
    corners[3] = surroundingTiles[0][1][3] and surroundingTiles[3][1][0]

    return corners

def convertTileToTemplateIndex(pos, walls):
    '''Convert a world position to a tile name and rotation'''
    #Get the tile
    tile = walls[pos[1]][pos[0]]
    #Get the needed corners
    corners = checkForCorners(pos, walls)

    #No tile present
    if not tile[0]:
        return "", 0

    #All four walls
    if tile[1][0] and tile[1][1] and tile[1][2] and tile[1][3]:
        return "fourWalls", 0

    #All except top wall
    if not tile[1][0] and tile[1][1] and tile[1][2] and tile[1][3]:
        return "threeWalls", 0

    #All except right wall
    if tile[1][0] and not tile[1][1] and tile[1][2] and tile[1][3]:
        return "threeWalls", -1.5708

    #All except bottom wall
    if tile[1][0] and tile[1][1] and not tile[1][2] and tile[1][3]:
        return "threeWalls", 3.14159

    #All except right wall
    if tile[1][0] and tile[1][1] and tile[1][2] and not tile[1][3]:
        return "threeWalls", 1.5708

    #L shaped walls bottom and left
    if not tile[1][0] and not tile[1][1] and tile[1][2] and tile[1][3]:
        #If pillar needed
        if corners[0]:
            return "twoWallsOnePillar", 0
        else:
            return "twoWallsRightAngle", 0

    #L shaped walls top and left
    if tile[1][0] and not tile[1][1] and not tile[1][2] and tile[1][3]:
        #If pillar needed
        if corners[1]:
            return "twoWallsOnePillar", -1.5708
        else:
            return "twoWallsRightAngle", -1.5708

    #L shaped walls top and right
    if tile[1][0] and tile[1][1] and not tile[1][2] and not tile[1][3]:
        #If pillar needed
        if corners[2]:
            return "twoWallsOnePillar", 3.14159
        else:
            return "twoWallsRightAngle", 3.14159

    #L shaped walls bottom and right
    if not tile[1][0] and tile[1][1] and tile[1][2] and not tile[1][3]:
        #If pillar needed
        if corners[3]:
            return "twoWallsOnePillar", 1.5708
        else:
            return "twoWallsRightAngle", 1.5708

    #Tunnel shaped walls top and bottom
    if tile[1][0] and not tile[1][1] and tile[1][2] and not tile[1][3]:
        return "twoWallsTunnel", 0

    #Tunnel shaped walls left and right
    if not tile[1][0] and tile[1][1] and not tile[1][2] and tile[1][3]:
        return "twoWallsTunnel", 1.5708

    #Top wall only 
    if tile[1][0] and not tile[1][1] and not tile[1][2] and not tile[1][3]:
        #No corners
        if not corners[1] and not corners[2]:
            return "oneWall", 0
        else:
            #Right corner
            if corners[1] and not corners[2]:
                return "oneWallOnePillarRight", 0
            #Left corner
            elif not corners[1] and corners[2]:
                return "oneWallOnePillarLeft", 0
            #Both corners
            else:
                return "oneWallTwoPillars", 0

    #Right wall only 
    if not tile[1][0] and tile[1][1] and not tile[1][2] and not tile[1][3]:
        #No corners
        if not corners[2] and not corners[3]:
            return "oneWall", -1.5708
        else:
            #Right corner
            if corners[2] and not corners[3]:
                return "oneWallOnePillarRight", -1.5708
            #Left corner
            elif not corners[2] and corners[3]:
                return "oneWallOnePillarLeft", -1.5708
            #Both corners
            else:
                return "oneWallTwoPillars", -1.5708

    #Bottom wall only 
    if not tile[1][0] and not tile[1][1] and tile[1][2] and not tile[1][3]:
        #No corners
        if not corners[3] and not corners[0]:
            return "oneWall", 3.14159
        else:
            #Right corner
            if corners[3] and not corners[0]:
                return "oneWallOnePillarRight", 3.14159
            #Left corner
            elif not corners[3] and corners[0]:
                return "oneWallOnePillarLeft", 3.14159
            #Both corners
            else:
                return "oneWallTwoPillars", 3.14159

    #Left wall only 
    if not tile[1][0] and not tile[1][1] and not tile[1][2] and tile[1][3]:
        #No corners
        if not corners[0] and not corners[1]:
            return "oneWall", 1.5708
        else:
            #Right corner
            if corners[0] and not corners[1]:
                return "oneWallOnePillarRight", 1.5708
            #Left corner
            elif not corners[0] and corners[1]:
                return "oneWallOnePillarLeft", 1.5708
            #Both corners
            else:
                return "oneWallTwoPillars", 1.5708

    #All four corners
    if corners[0] and corners[1] and corners[2] and corners[3]:
        return "fourPillars", 0

    #Three corners no bottom right
    if corners[0] and not corners[1] and corners[2] and corners[3]:
        return "threePillars", 0

    #Three corners no bottom left
    if corners[0] and corners[1] and not corners[2] and corners[3]:
        return "threePillars", -1.5708

    #Three corners no top left
    if corners[0] and corners[1] and corners[2] and not corners[3]:
        return "threePillars", 3.14159

    #Three corners no top right
    if not corners[0] and corners[1] and corners[2] and corners[3]:
        return "threePillars", 1.5708

    #Two corners adjacent both top
    if corners[0] and not corners[1] and not corners[2] and corners[3]:
        return "twoPillarsHorizontal", 0

    #Two corners adjacent both right
    if corners[0] and corners[1] and not corners[2] and not corners[3]:
        return "twoPillarsHorizontal", -1.5708

    #Two corners adjacent both bottom
    if not corners[0] and corners[1] and corners[2] and not corners[3]:
        return "twoPillarsHorizontal", 3.14159

    #Two corners adjacent both left
    if not corners[0] and not corners[1] and corners[2] and corners[3]:
        return "twoPillarsHorizontal", 1.5708

    #Two corners diagonal top left and bottom right
    if not corners[0] and corners[1] and not corners[2] and corners[3]:
        return "twoPillarsDiagonal", 0

    #Two corners diagonal top right and bottom left
    if corners[0] and not corners[1] and corners[2] and not corners[3]:
        return "twoPillarsDiagonal", 1.5708

    #One corner top left
    if not corners[0] and not corners[1] and not corners[2] and corners[3]:
        return "onePillar", 0

    #One corner top right
    if corners[0] and not corners[1] and not corners[2] and not corners[3]:
        return "onePillar", -1.5708

    #One corner bottom right
    if not corners[0] and corners[1] and not corners[2] and not corners[3]:
        return "onePillar", 3.14159

    #One corner bottom left
    if not corners[0] and not corners[1] and corners[2] and not corners[3]:
        return "onePillar", 1.5708

    return "zeroWalls", 0


def convertTileToExternalWallIndex (pos, walls):
    '''Convert tile position to external wall name and rotation'''
    #Get the tile at the position
    thisWall = walls[pos[1]][pos[0]]

    #If there is no tile here there is no need for an external wall
    if not thisWall[0]:
        return "", 0

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

    #Top wall only
    if not otherTiles[0] and otherTiles[1] and otherTiles[2] and otherTiles[3]:
        return "externalWallSingle", 0

    #Right wall only
    if otherTiles[0] and not otherTiles[1] and otherTiles[2] and otherTiles[3]:
        return "externalWallSingle", -1.5708

    #Bottom wall only
    if otherTiles[0] and otherTiles[1] and not otherTiles[2] and otherTiles[3]:
        return "externalWallSingle", 3.14159

    #Left wall only
    if otherTiles[0] and otherTiles[1] and otherTiles[2] and not otherTiles[3]:
        return "externalWallSingle", 1.5708

    #Top and Left walls only
    if not otherTiles[0] and otherTiles[1] and otherTiles[2] and not otherTiles[3]:
        return "externalWallCorner", 0

    #Top and Right walls only
    if not otherTiles[0] and not otherTiles[1] and otherTiles[2] and otherTiles[3]:
        return "externalWallCorner", -1.5708

    #Bottom and Right walls only
    if otherTiles[0] and not otherTiles[1] and not otherTiles[2] and otherTiles[3]:
        return "externalWallCorner", 3.14159

    #Bottom and Left walls only
    if otherTiles[0] and otherTiles[1] and not otherTiles[2] and not otherTiles[3]:
        return "externalWallCorner", 1.5708

    #Three walls Bottom missing
    if not otherTiles[0] and not otherTiles[1] and otherTiles[2] and not otherTiles[3]:
        return "externalWallHoop", 0

    #Three walls Left missing
    if not otherTiles[0] and not otherTiles[1] and not otherTiles[2] and otherTiles[3]:
        return "externalWallHoop", -1.5708

    #Three walls Top missing
    if otherTiles[0] and not otherTiles[1] and not otherTiles[2] and not otherTiles[3]:
        return "externalWallHoop", 3.14159

    #Three walls Right missing
    if not otherTiles[0] and otherTiles[1] and not otherTiles[2] and not otherTiles[3]:
        return "externalWallHoop", 1.5708
    
    return "", 0


def createFileData (walls, obstacles, numThermal, numVisual, startPos):
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

    #All the map tiles templates
    tileTypes = ["fourWalls", "threeWalls", "twoWallsRightAngle", "twoWallsTunnel", "oneWall", "zeroWalls", "twoWallsOnePillar", "oneWallOnePillarLeft", "oneWallOnePillarRight", "oneWallTwoPillars", "fourPillars", "threePillars", "twoPillarsHorizontal", "twoPillarsDiagonal", "onePillar"]
    tileTemplates = []
    #Iterate through the tiles
    for name in tileTypes:
        #Construct the path
        path = os.path.join(dirname, "blockTemplates")
        path = os.path.join(path, "{0}.txt".format(name))
        #Open the file
        tileTemp = open(path, "r")
        #Add the template to the list
        tileTemplates.append(tileTemp.read())
        #Close the file
        tileTemp.close()

    #All the exterior wall templates
    externalTileTypes = ["externalWallSingle", "externalWallCorner", "externalWallHoop"]
    externalTileTemplates = []
    #Iterate through the tiles
    for name in externalTileTypes:
        #Construct the path
        path = os.path.join(dirname, "blockTemplates")
        path = os.path.join(path, "{0}.txt".format(name))
        #Open the file
        tileTemp = open(path, "r")
        #Add the template to the list
        externalTileTemplates.append(tileTemp.read())
        #Close the file
        tileTemp.close()

    #All extra tile parts
    extraTileTypes = ["checkpoint", "trap", "goal"]
    extraTileTemplates = []
    #Iterate through the parts
    for name in extraTileTypes:
        #Construct the path
        path = os.path.join(dirname, "blockTemplates")
        path = os.path.join(path, "{0}.txt".format(name))
        #Open the file
        tileTemp = open(path, "r")
        #Add the template to the list
        extraTileTemplates.append(tileTemp.read())
        #Close the file
        tileTemp.close()

    #Open the file containing the template for a group
    boundsTemplate = open(os.path.join(os.path.join(dirname, "blockTemplates"), "bounds.txt"), "r")
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


    #Create file data - initialy just the header
    fileData = fileHeader

    #Strings to hold the tile parts
    allTiles = ""
    allExternals = ""
    allExtras = ""
    #Strings to hold the boundaries for special tiles
    allCheckpointBounds = ""
    allTrapBounds = ""
    allGoalBounds = ""

    #Upper left corner to start placing tiles from
    startX = -(len(walls[0]) * 0.3 / 2.0)
    startZ = -(len(walls) * 0.3 / 2.0)

    #Id numbers used to give a unique but interable name to tile pieces
    tileId = 0
    checkId = 0
    trapId = 0
    goalId = 0

    #Iterate through all the tiles
    for x in range(0, len(walls[0])):
        for z in range(0, len(walls)):
            #Get the tile name and rotation for that position
            tileName, rotation = convertTileToTemplateIndex([x, z], walls)
            #If there is a tile needed to be placed
            if tileName in tileTypes:
                #Get the template index
                templateIndex = tileTypes.index(tileName)
                #Add the tile data to the string of tile data
                allTiles = allTiles + tileTemplates[templateIndex].format(x * 0.3 + startX, z * 0.3 + startZ, rotation, tileId)

                #Get the external name and rotation
                externalTileName, externalRotation = convertTileToExternalWallIndex([x, z], walls)
                #If there is a wall needed
                if externalTileName in externalTileTypes:
                    #Get the template index
                    templateIndex = externalTileTypes.index(externalTileName)
                    #Add the external wall data to the string of external data
                    allExternals = allExternals + externalTileTemplates[templateIndex].format(x * 0.3 + startX, z * 0.3 + startZ, externalRotation, tileId)

                #checkpoint
                if walls[z][x][2]:
                    #Add the checkpoint to the extra data
                    allExtras = allExtras + extraTileTemplates[0].format(x * 0.3 + startX, z * 0.3 + startZ, 0, tileId)
                    #Add bounds to the checkpoint boundaries
                    allCheckpointBounds = allCheckpointBounds + boundsPart.format("checkpoint", checkId, (x * 0.3 + startX) - 0.15, (z * 0.3 + startZ) - 0.15, (x * 0.3 + startX) + 0.15, (z * 0.3 + startZ) + 0.15)
                    #Increment id counter
                    checkId = checkId + 1
                    
                #trap
                if walls[z][x][3]:
                    #Add the trap to the extra data
                    allExtras = allExtras + extraTileTemplates[1].format(x * 0.3 + startX, z * 0.3 + startZ, 0, tileId)
                    #Add bounds to the trap boundaries
                    allTrapBounds = allTrapBounds + boundsPart.format("trap", trapId, (x * 0.3 + startX) - 0.15, (z * 0.3 + startZ) - 0.15, (x * 0.3 + startX) + 0.15, (z * 0.3 + startZ) + 0.15)
                    #Increment id counter
                    trapId = trapId + 1
                    
                #goal
                if walls[z][x][4]:
                    #Add the goal to the extra data
                    allExtras = allExtras + extraTileTemplates[2].format(x * 0.3 + startX, z * 0.3 + startZ, 0, tileId)
                    #Add bounds to the goal boundaries
                    allGoalBounds = allGoalBounds + boundsPart.format("goal", goalId, (x * 0.3 + startX) - 0.15, (z * 0.3 + startZ) - 0.15, (x * 0.3 + startX) + 0.15, (z * 0.3 + startZ) + 0.15)
                    #Increment id counter
                    goalId = goalId + 1

            #Increment id counter
            tileId = tileId + 1

    #Add the data pieces to the file data
    fileData = fileData + groupPart.format(allExternals, "EXTERNALWALLS")
    fileData = fileData + groupPart.format(allTiles, "WALLTILES")
    fileData = fileData + groupPart.format(allExtras, "SPECIALTILES")
    fileData = fileData + groupPart.format(allCheckpointBounds, "CHECKPOINTBOUNDS")
    fileData = fileData + groupPart.format(allTrapBounds, "TRAPBOUNDS")
    fileData = fileData + groupPart.format(allGoalBounds, "GOALBOUNDS")

    #String to hold all the data for the obstacles
    allObstacles = ""
    allDebris = ""

    #Id to give a unique name to the obstacles
    obstacleId = 0
    debrisId = 0

    #Iterate obstalces
    for obstacle in obstacles:
        #If this is debris
        if obstacle[3]:
            #Add the debris object
            allDebris = allDebris + debrisPart.format(debrisId, obstacle[0], obstacle[1], obstacle[2])
            #Increment id counter
            debrisId = debrisId + 1
        else:
            #Add the obstacle
            allObstacles = allObstacles + obstaclePart.format(obstacleId, obstacle[0], obstacle[1], obstacle[2])
            #Increment id counter
            obstacleId = obstacleId + 1

    #Add obstacles and debris to the file
    fileData = fileData + groupPart.format(allObstacles, "OBSTACLES")
    fileData = fileData + groupPart.format(allDebris, "DEBRIS")
    
    #String to hold all the data for the robots
    robotData = ""
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
        robotData = robotData + robotPart.format(1, startPos[0][0] * 0.3 + startX, (startPos[0][1] * 0.3 + startZ) - 0.075, 1.5708)
                                            
    #Add the robot data to the file
    fileData = fileData + robotData

    #Add supervisors
    fileData = fileData + supervisorPart
    
    #Return the file data as a string
    return fileData


def makeFile(boxData, obstacles, thermal, visual, startPos, uiWindow = None):
    '''Create and save the file for the information'''
    #Generate the file string for the map
    data = createFileData(boxData, obstacles, thermal, visual, startPos)
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

    #Open the file to store the world in (cleared when opened)
    worldFile = open(filePath, "w")
    #Write all the information to the file
    worldFile.write(data)
    #Close the file
    worldFile.close()
