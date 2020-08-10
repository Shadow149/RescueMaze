"""Generation Graphical User Interface Script Type 2 v1
   Written by Alfred Robers and Robbie Goldman
   Based on Type 1 GUI but modified for maze 

Changelog:
 V1:
  - Modified to have sliders for:
      - Room dimensions
      - Thermal and visual humans
      - Bulky obstacles and debris
      - Checkpoints and traps
  - Reduced output section to display only necessary info
"""

import tkinter as tk
from tkinter import font, filedialog
from PIL import Image, ImageTk
import os
dirname = os.path.dirname(__file__)

class GenerateWindow(tk.Tk):
    '''A generation interface window'''
    def __init__ (self, *args, **kwargs):
        '''Create new window setup'''
        #Create the basic tkinter window
        tk.Tk.__init__(self, *args, **kwargs)
        #Set a fixed geometry
        self.geometry("908x704")
        self.resizable(False, False)
        #Create a frame to hold the basic structure
        self.mainFrame = tk.Frame(self)
        self.mainFrame.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        #One row, two columns the right one larger than the left
        self.mainFrame.grid_rowconfigure(0, minsize = 700)
        self.mainFrame.grid_columnconfigure(0, minsize = 550)
        self.mainFrame.grid_columnconfigure(1, minsize = 350)
        #Frame to hold the output information (left side)
        self.outputFrame = tk.Frame(self.mainFrame, highlightbackground = "black", highlightthickness = 2)
        self.outputFrame.grid(row = 0, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))

        #Setup grid for holding output items
        self.outputFrame.grid_columnconfigure(0, minsize = 350)
        self.outputFrame.grid_rowconfigure(0, minsize = 30)
        self.outputFrame.grid_rowconfigure(1, minsize = 340)
        self.outputFrame.grid_rowconfigure(2, minsize = 216)
        self.outputFrame.grid_rowconfigure(3, minsize = 58)
        self.outputFrame.grid_rowconfigure(4, minsize = 58)

        #Label for the map
        self.mapLabel = tk.Label(self.outputFrame, text = "Generated Plan")
        self.mapLabel.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        #Image representing the map
        imageData = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "map.png")))
        self.mapImage = tk.Label(self.outputFrame, image = imageData, width = 250, height = 250)
        self.mapImage.image = imageData
        self.mapImage.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        #Frame to hold generation values
        self.generatedNumbers = tk.Frame(self.outputFrame)
        self.generatedNumbers.grid(row = 2, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        #All columns and rows for values
        self.generatedNumbers.grid_columnconfigure(0, minsize = 100)
        self.generatedNumbers.grid_columnconfigure(1, minsize = 250)
        self.generatedNumbers.grid_rowconfigure(0, minsize = 108)
        self.generatedNumbers.grid_rowconfigure(1, minsize = 108)

        #Lists to hold the output headers and bodies
        self.outputHeaders = []
        self.outputBodies = []
        #Current index
        position = 0
        #Iterate different output headers
        for header in ["Humans", "Obstacles"]:
            #Create header label and grid on the right
            label = tk.Label(self.generatedNumbers, text = header, relief = tk.SUNKEN)
            label.grid(row = position, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
            self.outputHeaders.append(label)
            #Create body label and grid on the left
            labelBody = tk.Label(self.generatedNumbers, text = "None", relief = tk.SUNKEN)
            labelBody.grid(row = position, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))
            self.outputBodies.append(labelBody)
            #Increment position
            position = position + 1

        #Add generate and save buttons
        self.generateButton = tk.Button(self.outputFrame, text = "Generate Map", bg = "lightblue", command = self.generatePressed)
        self.generateButton.grid(row = 3, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.saveButton = tk.Button(self.outputFrame, text = "Save World", bg = "lightblue", state = "disabled", command = self.savePressed)
        self.saveButton.grid(row = 4, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        #Setup frame for inputs
        self.inputFrame = tk.Frame(self.mainFrame)
        self.inputFrame.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        #Thin row for tabs
        self.inputFrame.grid_rowconfigure(0, minsize = 30)
        #Main row for inputs
        self.inputFrame.grid_rowconfigure(1, minsize = 670)
        self.inputFrame.grid_columnconfigure(0, minsize = 550)
        #Tabs frame
        self.inputTabs = tk.Frame(self.inputFrame)
        self.inputTabs.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        #Setup grid for tabs (up to 5)
        for i in range(0, 5):
            self.inputTabs.grid_columnconfigure(i, minsize = 110)
        self.inputTabs.grid_rowconfigure(0, minsize = 30)

        #Create tab for basic input
        self.basicTab = tk.Button(self.inputTabs, text = "Basic", relief = "ridge", command = self.basicTabPressed , borderwidth = 4, background = "lightblue")
        self.basicTab.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        #Create tab for advanced input
        self.advancedTab = tk.Button(self.inputTabs, text = "Advanced", relief = "ridge", command = self.advancedTabPressed , borderwidth = 4)
        self.advancedTab.grid(row = 0, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))

        #Get the default colour (so tabs can be restored to this colour when not selected)
        self.defaultColour = self.advancedTab.cget("background")

        #Create a frame for the inputs
        self.inputArea = tk.Frame(self.inputFrame,highlightbackground = "black", highlightthickness = 2)
        self.inputArea.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.inputArea.grid_rowconfigure(0, minsize = 670)
        self.inputArea.grid_columnconfigure(0, minsize = 550)

        #Create an advanced page
        self.advancedSection = tk.Frame(self.inputArea)
        self.advancedSection.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        #Create a basic page (created second so it starts on top)
        self.basicSection = tk.Frame(self.inputArea)
        self.basicSection.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        #Create larger font for input headers
        self.inputFont = font.Font(size = 16)

        #Setup grid of basic input page
        self.basicSection.grid_columnconfigure(0, minsize = 50)
        self.basicSection.grid_columnconfigure(1, minsize = 450)
        self.basicSection.grid_columnconfigure(2, minsize = 50)
        self.basicSection.grid_rowconfigure(0, minsize=670)

        #List of default difficulty values
        '''self.difficulties = [[[5, 5], [4, 7], [0, 0], [2, 1, 1]],
                             [[6, 5], [5, 8], [1, 0], [2, 1, 1]],
                             [[7, 7], [7, 10], [2, 0], [2, 2, 2]],
                             [[9, 7], [8, 12], [2, 0], [3, 2, 3]],
                             [[11, 9], [8, 17], [3, 0], [3, 3, 3]],
                             [[15, 15], [10, 20], [4, 0], [4, 3, 4]]]'''
        self.difficulties = [[[5, 5], [4, 7], [0, 0], [2, 1, 1]],
                             [[6, 5], [5, 8], [0, 0], [2, 1, 1]],
                             [[7, 7], [7, 10], [0, 0], [2, 2, 2]],
                             [[9, 7], [8, 12], [0, 0], [3, 2, 3]],
                             [[11, 9], [8, 17], [0, 0], [3, 3, 3]],
                             [[15, 15], [10, 20], [0, 0], [4, 3, 4]]]

        #Setup the grid for the advanced page
        self.advancedSection.grid_columnconfigure(0, minsize=275)
        self.advancedSection.grid_columnconfigure(1, minsize=275)
        self.advancedSection.grid_rowconfigure(0, minsize=336)
        self.advancedSection.grid_rowconfigure(1, minsize=336)

        #add the frame for the room controls
        self.advRoom = tk.Frame(self.advancedSection, highlightbackground = "black", highlightthickness = 2)
        self.advRoom.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        #add the frame for the human controls
        self.advHumans = tk.Frame(self.advancedSection, highlightbackground = "black", highlightthickness = 2)
        self.advHumans.grid(row = 0, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))
        #add the frame for the obstacle controls
        self.advObstacles = tk.Frame(self.advancedSection, highlightbackground = "black", highlightthickness = 2)
        self.advObstacles.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        #add the frame for the tile controls
        self.advTiles = tk.Frame(self.advancedSection, highlightbackground = "black", highlightthickness = 2)
        self.advTiles.grid(row = 1, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))

        self.troughColourDefault = None

        #List of different slider inputs [booleanVar (enabled), slider, extraSlider]
        self.inputsArray = []

        #Add input sliders for rooms, humans, obstacles and bases
        self.inputsArray.append(self.createSliderSection(self.advRoom, 5, 15, "Rooms", "Vertical:", 5, 15, "Horizontal:"))
        self.inputsArray.append(self.createSliderSection(self.advHumans, 0, 25, "Humans", "Visual:", 0, 25, "Thermal:"))
        self.inputsArray.append(self.createSliderSection(self.advObstacles, 0, 10, "Obstacles", "Debris:", 0, 20, "Bulky:"))
        self.inputsArray.append(self.createSliderSection(self.advTiles, 2, 4, "Tiles", "Traps:", 0, 4, "Checkpoints:", "Swamps:", 0, 6))
        
        #Add a slider to choose the difficulty
        self.basicSlider = tk.Scale(self.basicSection, label="Difficulty:", font=self.inputFont, showvalue=0, from_=0, to=5, orient=tk.HORIZONTAL, length=250, command = self.moveBasicSlider)
        self.basicSlider.grid(row = 0, column = 1)
        #Initialize difficulty slider
        self.moveBasicSlider(0)

        #Get the default trough colour (so it can be restored when a slider is enabled)
        self.troughColourDefault = self.basicSlider.cget("troughcolor")
        
        #Not ready for generation
        self.ready = False
        #Not currently saving
        self.saving = False
        #Difficulty is not currently changing
        self.changingDifficulty = False

        #Set the default difficulty
        self.moveBasicSlider(0)

        #Set correct state of enabled sliders
        self.updateValues()

    
    def updateImage (self) -> None:
        '''Update the map image once the new one has been generated'''
        #Get the image from the file
        imageData = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "map.png")))
        #Set the image of the mapImage
        self.mapImage.configure(image = imageData)
        self.mapImage.image = imageData

    
    def moveBasicSlider (self, value: int) -> None:
        '''Move the basic slider to a specific value'''
        #List of names of different difficulties
        diffs = ["Custom", "Very Easy", "Easy", "Normal", "Hard", "Very Hard", "Expert"]
        #Change the label of the slider
        self.basicSlider.configure(label = "Difficulty: " + diffs[int(value) + 1])
        #Change the position of the slider
        self.setDifficulty(int(value) + 1)

        
    def basicTabPressed (self) -> None:
        '''When the basic tab is pressed'''
        #Change the colour of the basic and advanced tabs
        self.basicTab.configure(background = "lightblue")
        self.advancedTab.configure(background = self.defaultColour)
        #Move the basic tab to the top
        self.basicSection.tkraise()


    def advancedTabPressed (self) -> None:
        '''When the advanced tab is pressed'''
        #Change the colour of the basic and advanced tabs
        self.basicTab.configure(background = self.defaultColour)
        self.advancedTab.configure(background = "lightblue")
        #Move the advanced tab to the top
        self.advancedSection.tkraise()


    def createSliderSection (self, parent, minVal: int, maxVal: int, title: str, extraTitle = None, extraMin = None, extraMax = None, firstTitle = "Number:", thirdTitle = None, thirdMin = None, thirdMax = None) -> list:
        '''Add a slider section to the given parent'''
        #Configure parent grid
        parent.grid_columnconfigure(0, weight = 1)
        parent.grid_rowconfigure(0, weight = 1)
        parent.grid_rowconfigure(1, weight = 6)
        #Create frame to hold the slider
        slideFrame = tk.Frame(parent)
        slideFrame.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        slideFrame.grid_columnconfigure(0, weight = 1)
        slideFrame.grid_rowconfigure(0, weight = 1)
        #If there is an extra slider
        if extraTitle != None and extraMin != None and extraMax != None:
            #Add another row
            slideFrame.grid_rowconfigure(1, weight = 1)
        #If there is a third slider
        if thirdTitle != None and thirdMin != None and thirdMax != None:
            #Add another row
            slideFrame.grid_rowconfigure(2, weight = 1)
        #Create boolean variable to hold the locked state of the slider
        enabled = tk.BooleanVar()
        #Create the slider
        mainSlider = self.createSlider(slideFrame, minVal, maxVal, firstTitle)
        extraSlider = None
        thirdSlider = None
        #If there is an extra slider
        if extraTitle != None and extraMin != None and extraMax != None:
            #Create the extra slider
            extraSlider = self.createSlider(slideFrame, extraMin, extraMax, extraTitle, 1)
        #If there is a third slider
        if thirdTitle != None and thirdMin != None and thirdMax != None:
            #Create the third slider
            thirdSlider = self.createSlider(slideFrame, thirdMin, thirdMax, thirdTitle, 2)
        #Create the header frame (to hold name and enabled box)
        headerFrame = tk.Frame(parent)
        headerFrame.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        headerFrame.grid_columnconfigure(0, weight = 3)
        headerFrame.grid_columnconfigure(1, weight = 1)
        headerFrame.grid_rowconfigure(0, weight = 1)
        #Create title label
        headerText = tk.Label(headerFrame, text=title, font = self.inputFont)
        headerText.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        #Create locked check box
        enabledBox = tk.Checkbutton(headerFrame, onvalue = True, offvalue = False, variable = enabled, command = self.inputChanged)
        enabledBox.grid(row = 0, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))
        
        #Boolean variable and both sliders
        toReturn = [enabled, mainSlider, extraSlider]
        #If there is a third
        if thirdTitle != None and thirdMin != None and thirdMax != None:
            #Add it to the data being returned
            toReturn.append(thirdSlider)
        
        #Return the boolean variable and all sliders
        return toReturn

        
    def createSlider (self, parent, minVal: int, maxVal: int, name: str, rowNum = 0) -> tk.Scale:
        '''Create a single slider'''
        #Configure parent's grid
        parent.grid_rowconfigure(0, weight = 1)
        #Create slider with correct values
        slider = tk.Scale(parent, label=name, from_=minVal, to=maxVal, orient=tk.HORIZONTAL, length=200, command = lambda x: self.inputChanged)

        #Start the slider at it's minimum value
        slider.set(minVal)

        #Place the slider into the grid
        slider.grid(row = rowNum, column = 0)
        
        return slider

    
    def setDifficulty (self, difficultyValue: int) -> None:
        '''Change the difficulty to a specific value'''
        difficultyValue = int(difficultyValue)

        custom = False
        #If it is a normal difficulty
        if difficultyValue > 0:
            #Subtract 1 to account for custom
            difficultyValue = difficultyValue - 1
        else:
            #It is a custom difficulty
            custom = True

        #If it is a specific difficulty being set
        if not custom:
            #Currently changing the difficulty (prevents repeated calls)
            self.changingDifficulty = True
            #Get the difficulty values
            diffValues = self.difficulties[difficultyValue]
            position = 0
            #Iterate across values
            while position < len(diffValues) and position < len(self.inputsArray):
                #Allow for the sliders to change
                self.inputsArray[position][0].set(True)
                self.updateValues()
                #Iterate through the values for that input type
                for dataPos in range(0, len(diffValues[position])):
                    #If there is an input value there
                    if len(self.inputsArray[position]) > dataPos + 1:
                        #Set the value of that option
                        self.inputsArray[position][dataPos + 1].set(diffValues[position][dataPos])
                #Lock changes by user
                self.inputsArray[position][0].set(False)
                #Next input type
                position = position + 1

            #Update the sliders - lock again
            self.updateValues()
            #No longer changing the difficulty (allowed to call again)
            self.changingDifficulty = False


    def inputChanged (self) -> None:
        '''When one of the user inputs is changed'''
        #If the difficulty isn't currently changing
        if not self.changingDifficulty:
            #Move the slider to custom
            self.moveBasicSlider(-1)
            #Update the locked states
            self.updateValues()

       
    def updateValues (self) -> None:
        '''Update the locked state of the sliders'''
        #Iterate through the inputs
        for field in self.inputsArray:
            #If there is at least 3 items (enabled, slider and extra) 
            if len(field) > 2:
                #If it is unlocked
                if field[0].get():
                    #Set slider to enabled
                    field[1].configure(state = "normal", troughcolor = self.troughColourDefault)
                    #If there is an extra slider (otherwise it will be None)
                    if field[2] != None:
                        #Set the extra slider to enabled
                        field[2].configure(state = "normal", troughcolor = self.troughColourDefault)
                    #If there is a third slider
                    if len(field) > 3:
                        if field[3] != None:
                            #Set the third slider to enabled
                            field[3].configure(state = "normal", troughcolor = self.troughColourDefault)
                else:
                    #Set slider to disabled
                    field[1].configure(state = "disabled", troughcolor = "#AA8888")
                    #If there is an extra slider (otherwise it will be None)
                    if field[2] != None:
                        #Set the extra slider to disabled
                        field[2].configure(state = "disabled", troughcolor = "#AA8888")
                    #If there is a third slider
                    if len(field) > 3:
                        if field[3] != None:
                            #Set the third slider to disabled
                            field[3].configure(state = "disabled", troughcolor = "#AA8888")


    def getValues (self) -> list:
        '''Get all the input values and return them'''
        #List to hold input values
        values = []
        #Iterate through input sections
        for inputType in self.inputsArray:
            #If they are a full input
            if len(inputType) > 2:
                #List to hold the fields inputs
                fieldValue = []
                #Iterate through parts to end of the input field
                for pos in range(1, len(inputType)):
                    #If the part is not none
                    if inputType[pos] != None:
                        #Add the value from the slider
                        fieldValue.append(inputType[pos].get())
                #Add all the fields values to the list of values
                values.append(fieldValue)
        
        return values


    def setSaveButton (self, allowed: bool) -> None:
        '''Set the save button to enabled/disabled'''
        if allowed:
            self.saveButton.configure(state = "normal")
        else:
            self.saveButton.configure(state = "disabled")


    def generatePressed (self) -> None:
        '''Set flag to indicate that a generation is needed'''
        self.ready = True


    def generateStarted (self) -> None:
        '''Reset flag so that a generation is not called more than once'''
        self.ready = False


    def savePressed (self) -> None:
        '''Set flag to indicate that a save is needed'''
        self.saving = True


    def saveStarted (self) -> None:
        '''Reset flag so that a save is not called more than once'''
        self.saving = False


    def getPathSelection (self) -> str:
        '''Get a path from the user as to where to save the file and return it'''
        path = filedialog.asksaveasfilename(title = "Save World As", filetypes = [("Webots World File", ".wbt")])
        return path


    def setGeneratedInformation (self, thermal: str, visual: str, obstacles: str, debris: str) -> None:
        '''Update the generated numbers from the values given by the generation'''
        #Combine items in a list (so it can be iteratively added)
        dataList = [[thermal, visual], [obstacles, debris]]
        position = 0
        #Iterate across all output types
        while position < len(dataList) and position < len(self.outputBodies):
            #Merge strings in same type with new line separators
            message = "\n".join(dataList[position])
            #Set the output text
            self.outputBodies[position].configure(text = message)
            #Increment counter
            position = position + 1
    
    
