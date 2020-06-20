from controller import Supervisor

#Create the instance of the supervisor class
supervisor = Supervisor()

class Queue:
    def __init__(self):
        self.queue = []
    def enqueue(self,data):
        return self.queue.append(data)
    def dequeue(self):
        return self.queue.pop(0)
    def peek(self):
        return self.queue[0]
    def is_empty(self):
        return len(self.queue) == 0

class RobotHistory(Queue):
    def __init__(self):
        super().__init__()
    def enqueue(self,data):
        if len(self.queue) > 8:
            self.dequeue()
        return self.queue.append(data)
    
class Robot:
    '''Robot object to hold values whether its in a base or holding a human'''
    def __init__(self, node):
        '''Initialises the in a base, has a human loaded and score values'''

        self.wb_node = node

        self.wb_translationField = self.wb_node.getField('translation')

        self.inBase = True
        self._humanLoaded = False
        self._activityLoaded = False
        
        self.history = RobotHistory()

        self.loadedHuman = None
        self.loadedActivity = None

        self._score = 0
    
        self._timeStopped = 0
        self._stopped = False
        self._stoppedTime = None

        self.messages = Queue()

        self.lastVisitedCheckPointPosition = []

        self.visitedCheckpoints = []
    
    @property
    def position(self) -> list:
        return self.wb_translationField.getSFVec3f()
    
    @position.setter
    def position(self, pos: list) -> None:
        self.wb_translationField.setSFVec3f(pos)

    def _isStopped(self) -> bool:
        vel: list = self.wb_node.getVelocity()
        robotStopped = abs(vel[0]) < 0.01 and abs(vel[1]) < 0.01 and abs(vel[2]) < 0.01
        return robotStopped
        
    def timeStopped(self) -> float:
        self._stopped = self._isStopped()
        
        #if it isn't stopped yet
        if self._stoppedTime == None:
            if self._stopped:
                #get time the robot stopped
                self._stoppedTime = supervisor.getTime()
        else:
            #if its stopped
            if self._stopped:
                #get current time
                currentTime = supervisor.getTime()
                #calculate the time the robot stopped
                self._timeStopped = currentTime - self._stoppedTime
            else:
                #if it's no longer stopped, reset variables
                self._stoppedTime = None
                self._timeStopped = 0
        
        return self._timeStopped
            
    
    def hasHumanLoaded(self) -> bool:
        return self._humanLoaded

    def hasActivityLoaded(self) -> bool:
        return self._activityLoaded

    def loadActivity(self, activityClass) -> None:
        self._activityLoaded = True
        self.loadedActivity = activityClass

    def unLoadActivity(self) -> None:
        self._activityLoaded = False
        self.loadedActivity = None

    def loadHuman(self, humanClass) -> None:
        self._humanLoaded = True
        self.loadedHuman = humanClass
        
    def unLoadHuman(self) -> None:
        self._humanLoaded = False
        self.loadedHuman = None
        
    def increaseScore(self, score: int) -> None:
        self._score += score
    
    def getScore(self) -> None:
        return self._score

class Checkpoint:
    '''Checkpoint object holding the boundaries'''
    def __init__(self, min: list, max: list, center: list):
        '''Initialize the maximum and minimum corners for the checkpoint'''
        self.min = min
        self.max = max
        self.center = center
    
    def checkPosition(self, pos: list) -> bool:
        '''Check if a position is in this checkpoint'''
        #If the x position is within the bounds
        if pos[0] >= self.min[0] and pos[0] <= self.max[0]:
            #if the z position is within the bounds
            if pos[2] >= self.min[1] and pos[2] <= self.max[1]:
                #It is in this checkpoint
                return True
        
        #It is not in this checkpoint
        return False