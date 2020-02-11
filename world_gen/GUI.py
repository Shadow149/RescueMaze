import tkinter as tk
from tkinter import font, filedialog
from PIL import Image, ImageTk

class GenerateWindow(tk.Tk):
    def __init__ (self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("908x704")
        self.resizable(False, False)
        self.mainFrame = tk.Frame(self)
        self.mainFrame.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.mainFrame.grid_rowconfigure(0, minsize = 700)
        self.mainFrame.grid_columnconfigure(0, minsize = 550)
        self.mainFrame.grid_columnconfigure(1, minsize = 350)
        self.outputFrame = tk.Frame(self.mainFrame, highlightbackground = "black", highlightthickness = 2)
        self.outputFrame.grid(row = 0, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))

        self.outputFrame.grid_columnconfigure(0, minsize = 350)
        self.outputFrame.grid_rowconfigure(0, minsize = 30)
        self.outputFrame.grid_rowconfigure(1, minsize = 120)
        self.outputFrame.grid_rowconfigure(2, minsize = 350)
        self.outputFrame.grid_rowconfigure(3, minsize = 58)
        self.outputFrame.grid_rowconfigure(4, minsize = 58)

        self.mapLabel = tk.Label(self.outputFrame, text = "Generated Plan")
        self.mapLabel.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        
        imageData = ImageTk.PhotoImage(Image.open("map.png"))
        self.mapImage = tk.Label(self.outputFrame, image = imageData)
        self.mapImage.image = imageData
        self.mapImage.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        self.generatedNumbers = tk.Frame(self.outputFrame)
        self.generatedNumbers.grid(row = 2, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        self.generatedNumbers.grid_columnconfigure(0, minsize = 100)
        self.generatedNumbers.grid_columnconfigure(1, minsize = 250)
        self.generatedNumbers.grid_rowconfigure(0, minsize = 70)
        self.generatedNumbers.grid_rowconfigure(1, minsize = 70)
        self.generatedNumbers.grid_rowconfigure(2, minsize = 70)
        self.generatedNumbers.grid_rowconfigure(3, minsize = 70)
        self.generatedNumbers.grid_rowconfigure(4, minsize = 70)

        self.outputHeaders = []
        self.outputBodies = []
        position = 0
        for header in ["Humans", "Bases", "Obstacles", "Activities", ""]:
            label = tk.Label(self.generatedNumbers, text = header, relief = tk.SUNKEN)
            label.grid(row = position, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
            self.outputHeaders.append(label)
            labelBody = tk.Label(self.generatedNumbers, text = "None", relief = tk.SUNKEN)
            labelBody.grid(row = position, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))
            self.outputBodies.append(labelBody)
            position = position + 1

        self.generateButton = tk.Button(self.outputFrame, text = "Generate Map", bg = "lightblue", command = self.generatePressed)
        self.generateButton.grid(row = 3, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.saveButton = tk.Button(self.outputFrame, text = "Save World", bg = "lightblue", state = "disabled", command = self.savePressed)
        self.saveButton.grid(row = 4, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        
        self.inputFrame = tk.Frame(self.mainFrame)
        self.inputFrame.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.inputFrame.grid_rowconfigure(0, minsize = 30)
        self.inputFrame.grid_rowconfigure(1, minsize = 670)
        self.inputFrame.grid_columnconfigure(0, minsize = 550)
        self.inputTabs = tk.Frame(self.inputFrame)
        self.inputTabs.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        for i in range(0, 5):
            self.inputTabs.grid_columnconfigure(i, minsize = 110)
        self.inputTabs.grid_rowconfigure(0, minsize = 30)

        self.basicTab = tk.Button(self.inputTabs, text = "Basic", relief = "ridge", command = self.basicTabPressed , borderwidth = 4, background = "lightblue")
        self.basicTab.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        self.advancedTab = tk.Button(self.inputTabs, text = "Advanced", relief = "ridge", command = self.advancedTabPressed , borderwidth = 4)
        self.advancedTab.grid(row = 0, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))

        self.defaultColour = self.advancedTab.cget("background")
        
        self.inputArea = tk.Frame(self.inputFrame,highlightbackground = "black", highlightthickness = 2)
        self.inputArea.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.inputArea.grid_rowconfigure(0, minsize = 670)
        self.inputArea.grid_columnconfigure(0, minsize = 550)
        
        self.advancedSection = tk.Frame(self.inputArea, background = "red")
        self.advancedSection.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.basicSection = tk.Frame(self.inputArea)
        self.basicSection.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        self.inputFont = font.Font(size = 16)
        
        self.basicSection.grid_columnconfigure(0, minsize = 50)
        self.basicSection.grid_columnconfigure(1, minsize = 450)
        self.basicSection.grid_columnconfigure(2, minsize = 50)
        self.basicSection.grid_rowconfigure(0, minsize=670)
        
        self.basicSlider = tk.Scale(self.basicSection, label="Difficulty:", font=self.inputFont, showvalue=0, from_=0, to=5, orient=tk.HORIZONTAL, length=250, command = self.moveBasicSlider)
        self.basicSlider.grid(row = 0, column = 1)

        self.moveBasicSlider(0)

        self.advancedSection.grid_columnconfigure(0, minsize=275)
        self.advancedSection.grid_columnconfigure(1, minsize=275)
        self.advancedSection.grid_rowconfigure(0, minsize=223)
        self.advancedSection.grid_rowconfigure(1, minsize=223)
        self.advancedSection.grid_rowconfigure(2, minsize=223)

        self.advRoom = tk.Frame(self.advancedSection, highlightbackground = "black", highlightthickness = 2)
        self.advRoom.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.advHumans = tk.Frame(self.advancedSection, highlightbackground = "black", highlightthickness = 2)
        self.advHumans.grid(row = 0, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.advObstacles = tk.Frame(self.advancedSection, highlightbackground = "black", highlightthickness = 2)
        self.advObstacles.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.advActivities = tk.Frame(self.advancedSection, highlightbackground = "black", highlightthickness = 2)
        self.advActivities.grid(row = 1, column = 1, rowspan = 2, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.advBases = tk.Frame(self.advancedSection, highlightbackground = "black", highlightthickness = 2)
        self.advBases.grid(row = 2, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))

        self.troughColourDefault = self.basicSlider.cget("troughcolor")
        
        self.inputsArray = []
        
        self.inputsArray.append(self.createSliderSection(self.advRoom, 2, 5, "Rooms", None, None, None, "Splits:"))
        self.inputsArray.append(self.createSliderSection(self.advHumans, 0, 50, "Humans", "Children:", 0, 50, "Adults:"))
        self.inputsArray.append(self.createSliderSection(self.advObstacles, 0, 10, "Obstacles"))
        self.inputsArray.append(self.createSliderSection(self.advBases, 2, 4, "Bases"))

        self.difficulties = [[[2], [25, 15], [0], [2]], [[3], [20, 10], [2], [3]], [[4], [16, 4], [4], [3]], [[4], [13, 5], [6], [3]], [[5], [10, 3], [8], [2]]]

        self.ready = False
        self.saving = False
        self.changingDifficulty = False

        self.updateValues()

    
    def updateImage (self):
        imageData = ImageTk.PhotoImage(Image.open("map.png"))
        self.mapImage.configure(image = imageData)
        self.mapImage.image = imageData

    
    def moveBasicSlider (self, value):
        diffs = ["Custom", "Very Easy", "Easy", "Normal", "Hard", "Very Hard", "Expert"]
        self.basicSlider.configure(label = "Difficulty: " + diffs[int(value) + 1])
        self.setDifficulty(value)

        
    def basicTabPressed (self):
        self.basicTab.configure(background = "lightblue")
        self.advancedTab.configure(background = self.defaultColour)
        self.basicSection.tkraise()


    def advancedTabPressed (self):
        self.basicTab.configure(background = self.defaultColour)
        self.advancedTab.configure(background = "lightblue")
        self.advancedSection.tkraise()


    def createSliderSection (self, parent, minVal, maxVal, title, extraTitle = None, extraMin = None, extraMax = None, firstTitle = "Number:"):
        parent.grid_columnconfigure(0, weight = 1)
        parent.grid_rowconfigure(0, weight = 1)
        parent.grid_rowconfigure(1, weight = 6)
        slideFrame = tk.Frame(parent)
        slideFrame.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        slideFrame.grid_columnconfigure(0, weight = 1)
        slideFrame.grid_rowconfigure(0, weight = 1)
        if extraTitle != None and extraMin != None and extraMax != None:
            slideFrame.grid_rowconfigure(1, weight = 1)
        enabled = tk.BooleanVar()
        mainSlider = self.createSlider(slideFrame, minVal, maxVal, firstTitle)
        extraSlider = None
        if extraTitle != None and extraMin != None and extraMax != None:
            extraSlider = self.createSlider(slideFrame, extraMin, extraMax, extraTitle, 1)
        headerFrame = tk.Frame(parent)
        headerFrame.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        headerFrame.grid_columnconfigure(0, weight = 3)
        headerFrame.grid_columnconfigure(1, weight = 1)
        headerFrame.grid_rowconfigure(0, weight = 1)
        headerText = tk.Label(headerFrame, text=title, font = self.inputFont)
        headerText.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W))
        enabledBox = tk.Checkbutton(headerFrame, onvalue = True, offvalue = False, variable = enabled, command = self.inputChanged)
        enabledBox.grid(row = 0, column = 1, sticky = (tk.N, tk.E, tk.S, tk.W))
        
        return [enabled, mainSlider, extraSlider]

        
    def createSlider (self, parent, minVal, maxVal, name, rowNum = 0):
        parent.grid_rowconfigure(0, weight = 1)
        slider = tk.Scale(parent, label=name, from_=minVal, to=maxVal, orient=tk.HORIZONTAL, length=200, command = lambda x: self.inputChanged)

        slider.set(minVal)
        
        slider.grid(row = rowNum, column = 0)
        return slider


    def setDifficulty (self, difficultyValue):
        
        difficultyValue = int(difficultyValue)

        custom = False
        
        if difficultyValue > 0:
            difficultyValue = difficultyValue - 1
        else:
            custom = True

        if not custom:
            self.changingDifficulty = True
            diffValues = self.difficulties[difficultyValue]
            position = 0
            while position < len(diffValues) and position < len(self.inputsArray):
                self.inputsArray[position][0].set(True)
                self.updateValues()
                for dataPos in range(0, len(diffValues[position])):
                    if len(self.inputsArray[position]) > dataPos + 1:
                        self.inputsArray[position][dataPos + 1].set(diffValues[position][dataPos])
                self.inputsArray[position][0].set(False)
                position = position + 1

            self.updateValues()
            self.changingDifficulty = False


    def inputChanged (self):
        if not self.changingDifficulty:
            diff = self.checkCurrentDifficulty()
            if diff > -1:
                self.basicSlider.set(diff)
            else:
                self.moveBasicSlider(diff)
            self.updateValues()

       
    def updateValues (self):
        for field in self.inputsArray:
            if len(field) > 2:
                if field[0].get():
                    field[1].configure(state = "normal", troughcolor = self.troughColourDefault)
                    if (field[2] != None):
                        field[2].configure(state = "normal", troughcolor = self.troughColourDefault)
                else:
                    field[1].configure(state = "disabled", troughcolor = "#AA8888")
                    if (field[2] != None):
                        field[2].configure(state = "disabled", troughcolor = "#AA8888")


    def getValues (self):
        values = []
        for inputType in self.inputsArray:
            if len(inputType) > 2:
                fieldValue = []
                for pos in range(1, len(inputType)):
                    if inputType[pos] != None:
                        fieldValue.append(inputType[pos].get())
                values.append(fieldValue)

        return values


    def setSaveButton (self, allowed):
        if allowed:
            self.saveButton.configure(state = "normal")
        else:
            self.saveButton.configure(state = "disabled")


    def generatePressed (self):
        self.ready = True


    def generateStarted (self):
        self.ready = False


    def savePressed (self):
        self.saving = True


    def saveStarted (self):
        self.saving = False


    def getPathSelection (self):
        path = fledialog.asksaveasfilename(title = "Save World As", filetypes = [("Webots World File", ".wbt")])
        return path


    def setGeneratedInformation (self, adults, children, bases, obstacles, activities):
        dataList = [[adults, children], [bases], [obstacles], [activities]]
        position = 0
        while position < len(dataList) and position < len(self.outputBodies):
            message = "\n".join(dataList[position])
            self.outputBodies[position].configure(text = message)
            position = position + 1
    
    
    def checkCurrentDifficulty (self):
        values = self.getValues()
        for v in range(0, len(values)):
            if type(values[v]) != type([]):
                values[v] = [values[v]]

        for pos in range(0, len(self.difficulties)):
            match = True
            for field in range(0, max(len(values), len(self.difficulties[pos]))):
                for item in range(0, max(len(values[field]), len(self.difficulties[pos][field]))):
                    if values[field][item] != self.difficulties[pos][field][item]:
                        match = False

            if match:
                return pos

        return -1
