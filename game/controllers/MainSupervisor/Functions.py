import os
from controller import Supervisor

#Create the instance of the supervisor class
supervisor = Supervisor()

def getPath(number: int) -> str:
    '''Get the path to the correct controller'''
    #The current path to this python file
    filePath = os.path.dirname(os.path.abspath(__file__))
    
    filePath = filePath.replace('\\','/')

    #Split into parts on \
    pathParts = filePath.split("/")
    
    filePath = ""
    #Add all parts back together
    for part in pathParts:
        #Except the last one
        if part != pathParts[-1]:
            #Concatenate with / not \ (prevents issues with escape characters)
            filePath = filePath + part + "/"
    
    #Controller number part added
    if number == 0:
        filePath = filePath + "robot0Controller/robot0Controller.py"
    elif number == 1:
        filePath = filePath + "robot1Controller/robot1Controller.py"
    else:
        #Returns none if id was not valid
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
    
    #If there is a name in the file
    if "RobotName:" in fileData:
        #Find the name
        name = fileData[fileData.index("RobotName:") + 10:]
        name = name.split("\n")[0]
        #Return data with a name
        return name, number
    #Return data without a name
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
    supervisor.wwiSendText("historyUpdate"+","+",".join(robot0Obj.history.queue)+":"+",".join(robot1Obj.history.queue))

def getHumans():
    print('yeet')
    #Iterate for each human
    for i in range(numberOfHumans):
        #Get each human from children field in the human root node HUMANGROUP
        human = humanNodes.getMFNode(i)

        victimDescription = supervisor.getFromDef('human'+str(i)+'solid').getField('description').getSFString()
        textureType = victimDescription.split(',')[0]
        scoreWorth = int(victimDescription.split(',')[1])
        print(textureType)

        #Create Human Object from human position
        humanObj = Human(human ,i, textureType,scoreWorth)
        humans.append(humanObj)

def resetVictimsTextures():
    #Iterate for each victim
    for i in range(numberOfHumans):
        print(i)
        victimDescription = supervisor.getFromDef('human'+str(i)+'solid').getField('description').getSFString()
        textureType = victimDescription.split(',')[0]
        print(textureType)
        supervisor.getFromDef('human'+str(i)+'texture').getField('url').setMFString(0,'./textures/'+textureType+'_not_found.png')

def relocate(num):
    if int(num) == 0:
        relocatePosition = robot0Obj.lastVisitedCheckPointPosition
        print(relocatePosition)

        if relocatePosition == []:
            print('No checkpoint visited')
        else:
            robot0Obj.position = [relocatePosition[0],-0.0751,relocatePosition[2]]
    elif int(num) == 1:
        relocatePosition = robot1Obj.lastVisitedCheckPointPosition

        if relocatePosition == []:
            print('No checkpoint visited')
        else:
            robot1Obj.position = [relocatePosition[0],-0.0751,relocatePosition[2]]