from controller import Robot

#TODO comment code

MOVE_FORWARD = "MOVE_FORWARD"
TURN_LEFT = "TURN_LEFT"
TURN_RIGHT = "TURN_RIGHT"
STOP = "STOP"

class Player (Robot):


    def boundSpeed(self, speed):
        return max(-self.maxSpeed, min(self.maxSpeed, speed))

    def __init__(self):
        super(Player, self).__init__()
        
        self.timeStep = 32
        self.maxSpeed = 10.0
        
        self.mode = MOVE_FORWARD
        self.wheels = []
        self.distanceSensors = []
        self.leftSensors = []
        self.rightSensors = []
        self.frontSensor = None
        
        self.humanLoaded = False
        self.collecting = False
        
        #config camera
        self.camera = self.getCamera('camera')
        self.camera.enable(4 * self.timeStep)
        self.camera.recognitionEnable(4 * self.timeStep)
        
        #config wheels
        self.wheels.append(self.getMotor("left wheel"))
        self.wheels.append(self.getMotor("right wheel"))
        
        #move forever
        self.wheels[0].setPosition(float("inf"))
        self.wheels[1].setPosition(float("inf"))
        
        #config sensors
        
        self.frontSensor = self.getDistanceSensor('so4')
        self.frontSensor.enable(self.timeStep)

        for i in range(3):
            sensor = self.getDistanceSensor('so'+str(i))
            self.leftSensors.append(sensor)
            self.leftSensors[i].enable(self.timeStep)


        for i in range(3):
            sensor = self.getDistanceSensor('so'+str(5+i))
            self.rightSensors.append(sensor)
            self.rightSensors[i].enable(self.timeStep)
        
        #idk
        self.wheels[0].setVelocity(0.0)
        self.wheels[1].setVelocity(0.0)
    
    def getDetectedObjects(self):
        objects = self.camera.getRecognitionObjects()
        return objects
    
    def getBaseObjects(self):
        objects = self.getDetectedObjects()
        
        bases = []
        
        for item in objects:
            if item.get_colors() == [0.3,0,1]:
                deposit_pos = item.get_position()
                deposit_image_pos = item.get_position_on_image()
                bases.append([deposit_pos,deposit_image_pos])
        
        return bases
    
    def getHumanObjects(self):
        objects = self.getDetectedObjects()
        
        humans = []
        
        for item in objects:
            if item.get_colors() == [0,0,0]:
                human_pos = item.get_position()
                human_image_pos = item.get_position_on_image()
                humans.append([human_pos,human_image_pos])
        
        return humans
    
    def nearObject(self,objPos: list) -> bool:
        return abs(objPos[0]) < 0.5 and abs(objPos[2]) < 0.5
    
    def update(self):
        self.mode = MOVE_FORWARD
        
        #for all sensors
        for i in range(3):
            if self.leftSensors[i].getValue() > 900:
                self.mode = TURN_RIGHT
            elif self.rightSensors[2-i].getValue() > 900:
                self.mode = TURN_LEFT
        if self.frontSensor.getValue() > 900:
            self.mode = TURN_RIGHT
        
        bases = self.getBaseObjects()
        humans = self.getHumanObjects()
        
        print(self.humanLoaded)
        
        for base in bases:
            if self.nearObject(base[0]) and self.humanLoaded:
                self.mode = STOP
                break
            
        for human in humans:
            if self.nearObject(human[0]) and not self.humanLoaded or self.collecting:
                self.collecting = True
                self.mode = STOP
                self.humanLoaded = True
                break
        
      
    def run(self):
        while True:

            speeds = [0.0, 0.0]
            
            self.update()
            #print(self.mode)

            # Send actuators commands according to the mode
            if self.mode == MOVE_FORWARD:
                speeds[0] = self.maxSpeed
                speeds[1] = self.maxSpeed
            elif self.mode == TURN_RIGHT:
                #set left wheel speed
                speeds[0] = 0.5 * self.maxSpeed
                #set right wheel speed
                speeds[1] = 0
            elif self.mode == TURN_LEFT:
                #set left wheel speed
                speeds[0] = 0
                #set right wheel speed
                speeds[1] = 0.5 * self.maxSpeed
            elif self.mode == STOP:
                #set left wheel speed
                speeds[0] = 0
                #set right wheel speed
                speeds[1] = 0
                
                
            self.wheels[0].setVelocity(speeds[0])
            self.wheels[1].setVelocity(speeds[1])

            # Perform a simulation step, quit the loop when
            # Webots is about to quit.
            if self.step(self.timeStep) == -1:
                break


controller = Player()
controller.run()
