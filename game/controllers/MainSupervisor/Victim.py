from controller import Supervisor

#Create the instance of the supervisor class
supervisor = Supervisor()

class Human():
    '''Human object holding the boundaries'''
    def __init__(self, node, ap: int, vtype: str, score: int):
        '''Initialises the radius and position of the human'''
    
        self.wb_node = node

        self.wb_translationField = self.wb_node.getField('translation')

        self.arrayPosition = ap
        self.scoreWorth = score
        self.radius = 0.15
        self.victim_type = vtype

        self.simple_victim_type = self.get_simple_victim_type()

        self.identified = False

    @property
    def position(self) -> list:
        return self.wb_translationField.getSFVec3f()
    
    @position.setter
    def position(self, pos: list) -> None:
        self.wb_translationField.setSFVec3f(pos)

    def identify(self):
        supervisor.getFromDef('human'+str(self.arrayPosition)+'texture').getField('url').setMFString(0,'./textures/'+self.victim_type+'_found.png')
        self.identified = True

    def get_simple_victim_type(self):
        if self.victim_type == 'victim_harmed':
            return 'H'
        elif self.victim_type == 'victim_unharmed':
            return 'U'
        elif self.victim_type == 'victim_stable':
            return 'S'

    def getType(self) -> int:
        '''Set type of human (adult or child) through object size'''
        #Get human size
        humanSize = self.wb_node.getField("scale").getSFVec3f()

        if humanSize[1] == 0.5:
            return 2  
        else:
            return 1  

    def checkPosition(self, pos: list, min_dist: float) -> bool:
        '''Check if a position is near an object, based on the min_dist value'''
        #Get distance from the object to the passed position using manhattan distance for speed
        #TODO Check if we want to use euclidian or manhattan distance -- currently manhattan
        distance = abs(self.position[0] - pos[0]) + abs(self.position[2] - pos[2])
        return distance < min_dist