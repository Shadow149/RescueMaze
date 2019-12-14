from decimal import Decimal
import os
dirname = os.path.dirname(__file__)

#The string to add to the end of the file to finish it
fileFooter = "  ]\n}\n"


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


def createFileData (boxData, bases, robots):
    '''Create a file data string from the positions and scales'''
    #Open the file containing the standard header
    headerFile = open(os.path.join(dirname, "fileHeader.txt"), "r")
    #Read header
    fileHeader = headerFile.read()
    #Close header file
    headerFile.close()

    #Open the file containing the template for a block
    boxTemplate = open(os.path.join(dirname, "boxTemplate.txt"), "r")
    #Read template
    boxPart = boxTemplate.read()
    #Close template file
    boxTemplate.close()

    #Open the file containing the template for a base
    baseTemplate = open(os.path.join(dirname, "baseTemplate.txt"), "r")
    #Read template
    basePart = baseTemplate.read()
    #Close template file
    baseTemplate.close()

    #Open the file containing the template for a set of base boundaries
    baseBoundTemplate = open(os.path.join(dirname, "baseBoundsTemplate.txt"), "r")
    #Read template
    baseBoundPart = baseBoundTemplate.read()
    #Close template file
    baseBoundTemplate.close()

    #Open the file containing the template for a robot
    robotTemplate = open(os.path.join(dirname, "robotTemplate.txt"), "r")
    #Read template
    robotPart = robotTemplate.read()
    #Close template file
    robotTemplate.close()

    #Open the file containing the template for a group
    groupTemplate = open(os.path.join(dirname, "groupTemplate.txt"), "r")
    #Read template
    groupPart = groupTemplate.read()
    #Close template file
    groupTemplate.close()

    #Open the file containing the template for a human group
    humanGroupTemplate = open(os.path.join(dirname, "humanGroupTemplate.txt"), "r")
    #Read template
    humanGroupPart = humanGroupTemplate.read()
    #Close template file
    humanGroupTemplate.close()

    #Open the file containing the template for a human
    humanTemplate = open(os.path.join(dirname, "humanTemplate.txt"), "r")
    #Read template
    humanPart = humanTemplate.read()
    #Close template file
    humanTemplate.close()

    #Open the file containing the template for the supervisor
    supervisorTemplate = open(os.path.join(dirname, "supervisorTemplate.txt"), "r")
    #Read template
    supervisorPart = supervisorTemplate.read()
    #Close template file
    supervisorTemplate.close()


    #Create file data - initialy just the header
    fileData = fileHeader

    #Number used to give a unique name to the solid
    i = 0
    #Iterate for each of the blocks
    for box in boxData:
        #Add a copy of the template to the end of the file with the position, scale data and name inserted
        fileData = fileData + boxPart.format(box[0][0], box[0][1], box[1][0], box[1][1], "internalWall" + str(i))
        #Increment solid name counter
        i = i + 1

    baseBoundsAll = ""
    #Number used to give a unique name to the solid
    i = 0
    #Iterate for each of the bases
    for base in bases:
        #Add a copy of the templace for the base to the file, with position, scale data and a name inserted
        fileData = fileData + basePart.format(base[0][0], base[0][1], base[1][0], base[1][1], "base" + str(i))
        #Add a copy of the base bounds to the bounds list
        baseBoundsAll = baseBoundsAll + baseBoundPart.format(base[0][0] - (base[1][0] / 2), base[0][1] - (base[1][1] / 2), base[0][0] + (base[1][0] / 2), base[0][1] + (base[1][1] / 2), str(i))
        #Increment solid name counter
        i = i + 1

    fileData = fileData + groupPart.format(baseBoundsAll)

    #Add the footer onto the file data
    fileData = fileData + fileFooter

    #Number used to give a unique name to the solid
    i = 0

    for robot in robots:

        fileData = fileData + robotPart.format(robot[0], robot[1], str(i))

        i = i + 1

    #String to contain all human objects
    humansAll = ""

    #Number used to give a unique name to each human's solid
    i = 0

    #Iterate 20 times
    for humanNum in range(0, 20):
        #Add another human
        humansAll = humansAll + humanPart.format(humanNum)
        #Increment name counter
        i = i + 1
    
    #Insert humans into group and add to file
    fileData = fileData + humanGroupPart.format(humansAll)

    #Add a supervisor robot
    fileData = fileData + supervisorPart

    #Return the file data as a string
    return fileData


def makeFile(boxData, bases, robots):
    '''Create and save the file for the information'''
    #Generate the file string for the map
    data = createFileData(boxData, bases, robots)

    #Open the file to store the world in (cleared when opened)
    worldFile = open(os.path.join(dirname, "generatedWorld.wbt"), "w")
    #Write all the information to the file
    worldFile.write(data)
    #Close the file
    worldFile.close()