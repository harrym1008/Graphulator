from tkinter import *
from tkinter import messagebox
from tkinter.font import Font
from multiprocessing import cpu_count

from colours import *
from uimath import UIMath
from evaluate import *
from numstr import *


numbersDropdown = [str(i+1) for i in range(10)]

scrsz = "438x700" if cpu_count() > 2 else "350x600"



class UserInterface:
    def __init__(self, graph, graphUI, killMethodReference):
        self.root = Tk()                  # Define the root window
        self.root.title("Graphulator")
        self.root.geometry(scrsz)     # Default resolution of 350x600

        self.root.protocol("WM_DELETE_WINDOW", killMethodReference)  
                                    # Run the kill method when the X is pressed

        self.graph = graph
        self.graphUI = graphUI

        self.currentEquation = 0
        self.dropdownOptions = [str(i+1) for i in range(10)]

        # Define constants
        self.a = 0
        self.b = 0
        self.c = 0
        self.t = (-10, 10)

        self.CreateFonts()      # Create fonts array
        self.CreateWindow()     # Place all tkinter widgets onto the window
        self.ResetConstants()





    def CreateWindow(self):
        self.CreateLabel("Graphulator", 0, (0.02, 0.01, 0.81, 0.07) )

        # Create reset button
        self.CreateButton("Reset", 3, self.Reset, (0.83, 0.005, 0.17, 0.07))

        # Define all of the label frames
        self.equLF = self.CreateLabelFrame("Equation Input", 1, (0.04, 0.08, 0.92, 0.49))
        self.calcLF = self.CreateLabelFrame("Calculations", 1, (0.04, 0.57, 0.92, 0.25))
        self.constLF = self.CreateLabelFrame("Constants", 1, (0.04, 0.82, 0.92, 0.17))
        
        self.intsectLF = self.CreateLabelFrame("Intersection", 3, (0.5, -0.05, 0.45, 0.5), self.calcLF)
        self.evalLF = self.CreateLabelFrame("Evaluate", 3, (0.5, 0.475, 0.45, 0.5), self.calcLF)

        # Create the equation entry widgets
        self.entries = []
        for i in range(10):
            self.entries.append(StringVar(self.equLF))
            self.CreateLabel(f"[{i+1}]", 2, (0, 0.1*i, 0.15, 0.09), self.equLF) 

            entry = Entry(self.equLF, textvariable=self.entries[i])
            entry.config(font=self.fonts[6])
            entry.place(relx=0.2, rely=0.1*i, relheight=0.09, relwidth=0.8) 


        # Create buttons inside the calculations frame
        self.CreateButton("Y-Intercept", 3, self.DisplayYIntercept, (0.05, 0, 0.4, 0.23), self.calcLF)
        self.CreateButton("X-Intercept", 3, self.DisplayXIntercept, (0.05, 0.25, 0.4, 0.23), self.calcLF)
        self.CreateButton("Intersection", 3, self.DisplayIntersection, (0.05, 0.5, 0.4, 0.23), self.calcLF)

        self.CreateButton("Eval X", 3, self.DisplayXEvaluation, (0.05, 0.75, 0.2, 0.23), self.calcLF)
        self.CreateButton("Eval Y", 3, self.DisplayYEvaluation, (0.25, 0.75, 0.2, 0.23), self.calcLF)

        # Create the dropdowns in the intersection frame
        self.intsectStringVars = [StringVar(self.intsectLF) for i in range(2)]
        for i, x in enumerate([0, 0.5]):
            self.intsectStringVars[i].set(f"{i+1}")
            dropdown = OptionMenu(self.intsectLF, self.intsectStringVars[i], *self.dropdownOptions)
            dropdown.config(font=self.fonts[2])
            dropdown.place(relx=x, rely=0, relwidth=0.5, relheight=1)

        # Create the entries in the evaluate frame
        self.CreateLabel("X =", 4, (0, -0.06, 0.3, 0.5), self.evalLF)
        self.CreateLabel("Y =", 4, (0, 0.44, 0.3, 0.5), self.evalLF)

        self.evalStringVars = [StringVar(self.evalLF) for i in range(2)]
        self.CreateEntry(self.evalStringVars[0], 4, (0.25, -0.06, 0.7, 0.5), self.evalLF)
        self.CreateEntry(self.evalStringVars[1], 4, (0.25, 0.44, 0.7, 0.5), self.evalLF)
        [sVar.set("0") for sVar in self.evalStringVars]

        # Create the sliders for the constants
        self.constantSliderValues = []
        self.constantEntryPairs = []
        self.constantValues = []

        for letter, y in [("a", -0.03), ("b", 0.22), ("c", 0.47), ("t", 0.72)]:
            variable = DoubleVar(self.constLF)
            self.constantSliderValues.append(variable)

            slider = Scale(self.constLF, from_=0, to=1, orient="horizontal", \
                 variable=variable, resolution=0.001, showvalue=False)
            slider['state'] = "disabled" if letter == "t" else "normal"
            slider.place(relx=0.06, rely=y, relwidth=0.4, relheight=0.25)
            
            stringVars = [StringVar(self.constLF), StringVar(self.constLF)]
            self.constantEntryPairs.append(stringVars)
            self.CreateEntry(stringVars[0], 5, (0.59, y, 0.135, 0.25), self.constLF)
            self.CreateEntry(stringVars[1], 5, (0.835, y, 0.135, 0.25), self.constLF)
            
            self.CreateLabel(letter, 4, (0, y, 0.06, 0.25), self.constLF)          
            self.CreateLabel(f"≤ {letter} ≤", 5, (0.73, y, 0.10, 0.25), self.constLF)
            
            stringVar = StringVar(self.constLF)
            self.constantValues.append(stringVar)            
            lbl = Label(self.constLF, textvariable=stringVar)
            lbl.config(font=self.fonts[5])
            lbl.place(relx=0.44, rely=y, relwidth=0.14, relheight=0.25) 

        for i in range(4):
            normalisedValue = 0.5
            self.constantSliderValues[i].set(normalisedValue)
            self.constantEntryPairs[i][0].set("-10")
            self.constantEntryPairs[i][1].set("10")
            self.constantValues[i].set(NStr(UIMath.Lerp(-10, 10, normalisedValue), short=True))
        


    def ResetConstants(self):
        aLower = UIMath.TryConvertToFloat(self.constantEntryPairs[0][0].get())
        aUpper = UIMath.TryConvertToFloat(self.constantEntryPairs[0][1].get())
        self.a = UIMath.Lerp(aLower, aUpper, self.constantSliderValues[0].get())
        
        bLower = UIMath.TryConvertToFloat(self.constantEntryPairs[1][0].get())
        bUpper = UIMath.TryConvertToFloat(self.constantEntryPairs[1][1].get())
        self.b = UIMath.Lerp(bLower, bUpper, self.constantSliderValues[1].get())
        
        cLower = UIMath.TryConvertToFloat(self.constantEntryPairs[2][0].get())
        cUpper = UIMath.TryConvertToFloat(self.constantEntryPairs[2][1].get())
        self.c = UIMath.Lerp(cLower, cUpper, self.constantSliderValues[2].get())

        tTimer = (time.perf_counter() % 10) / 10
        tLower = UIMath.TryConvertToFloat(self.constantEntryPairs[3][0].get())
        tUpper = UIMath.TryConvertToFloat(self.constantEntryPairs[3][1].get())
        tValue = UIMath.Lerp(tLower, tUpper, tTimer) 
        self.t = (tLower, tUpper)

        self.constantValues[0].set(NStr(self.a))
        self.constantValues[1].set(NStr(self.b))
        self.constantValues[2].set(NStr(self.c))
        self.constantValues[3].set(NStr(tValue, short=True))
        self.constantSliderValues[3].set(tTimer)


    def GetConstants(self):
        return (self.a, self.b, self.c, self.t[0], self.t[1])



    def Reset(self):        
        self.graph.zoom = 50
        self.graph.offset = [0, 0]
        self.graphUI.highlightedPoints.clear()




    # This code finds rusn the evaluate function for finding the X value, then creates a window displaying the points
    def DisplayXEvaluation(self):
        strEqu = self.entries[self.currentEquation].get()

        try:
            yValue = float(self.evalStringVars[1].get())
            points = UIMath.EvaluateX(strEqu, yValue)
            pointsString = ""

            for point in points:
                pointsString += f"({NStr(point[0])}, {NStr(point[1])})\n"
                print(point)

            self.AskToHighlightPoints("X-Evaluation", f"""{strEqu}
                
At Y = {NStr(yValue)}, the following point{'' if len(points[0]) == 1 else 's'} at on the graph:

{pointsString}""", points)


        except Exception as error:
            messagebox.showerror("X-Evaluation", f"""{strEqu}\n\nAn error occured whilst calculating the X evaluation.\n
Error:   {type(error).__name__}
Message: {error.args[0]}""")



    # This code finds rusn the evaluate function for finding the Y value, then creates a window displaying the points
    def DisplayYEvaluation(self):
        strEqu = self.entries[self.currentEquation].get()

        try:
            xValue = float(self.evalStringVars[0].get())
            points = UIMath.EvaluateX(strEqu, xValue)
            pointsString = ""

            for point in points:
                pointsString += f"({NStr(point[0])}, {NStr(point[1])})\n"
                print(point)

            self.AskToHighlightPoints("X-Evaluation", f"""{strEqu}
                
At X = {NStr(xValue)}, the following point{'' if len(points[0]) == 1 else 's'} at on the graph:

{pointsString}""", points)


        except Exception as error:
            messagebox.showerror("X-Evaluation", f"""{strEqu}\n\nAn error occured whilst calculating the X evaluation.\n
Error:   {type(error).__name__}
Message: {error.args[0]}""")






    # This code finds the location(s) of the intersection, then creates a window displaying the points
    def DisplayIntersection(self):
        equNums = int(self.intsectStringVars[0].get())-1, int(self.intsectStringVars[1].get())-1
        strEqus = self.entries[ equNums[0] ].get(), self.entries[ equNums[1] ].get() 

        header = f"{equNums[0]+1}: {strEqus[0]}\n{equNums[1]+1}: {strEqus[1]}"

        try:
            intersections = UIMath.FindIntersections(strEqus[0], strEqus[1])
            intsectString = ""

            points = [] 

            if len(intersections) == 0:
                raise NotFoundException("No intersections could be found")

            for intsect in intersections:
                x = float(intsect[0])
                y = float(intsect[1])
                points.append((x, y))

                intsectString += f"({NStr(x)}, {NStr(y)})\n"

            self.AskToHighlightPoints("Intersection", f"""{header}
                
The two graphs intersect at the point{'' if len(intersections[0]) == 1 else 's'}:

{intsectString}""", points)

        except Exception as error:
            messagebox.showerror("Intersection", f"""{header}\n\nAn error occured whilst calculating the intersection.\n
Error:   {type(error).__name__}
Message: {error.args[0]}""")
      
                







    def DisplayYIntercept(self):
        try:
            strEqu = self.entries[self.currentEquation].get()
            ySolutions = UIMath.FindYIntercept(strEqu)
            
            if len(ySolutions) == 0:
                raise NotFoundException("This equation does not a solution at X=0, and so it doesn't have a Y-intercept")

            pointsString = ""
            points = []

            x = 0
            for sol in ySolutions:
                y = float(eval(sol))
                points.append((x, y))
                pointsString += f"(0, {NStr(y)})\n"
                

            self.AskToHighlightPoints("Y-Intercept", f"""{strEqu}
            
The Y-intercept is at point{'' if len(ySolutions) == 1 else 's'}:

{pointsString}""", points)

        except Exception as error:
            messagebox.showerror("Y-Intercept", f"""An error occured whilst calculating the Y-intercept.\n
Error:   {type(error).__name__}
Message: {error.args[0]}""")
        
        
    def DisplayXIntercept(self):
        try:
            strEqu = self.entries[self.currentEquation].get()
            xSolutions = UIMath.FindXIntercept(strEqu)
            
            if len(xSolutions) == 0:
                raise NotFoundException("This equation does not a solution at Y=0, and so it doesn't have a X-intercept")

            pointsString = "\n"
            points = []

            y = 0
            for sol in xSolutions:
                x = float(eval(sol))
                points.append((x, y))
                pointsString += f"({NStr(x)}, 0)\n"
                

            self.AskToHighlightPoints("X-Intercept", f"""{strEqu}
            
The X-intercept is at point{'' if len(xSolutions) == 1 else 's'}:

{pointsString}""", points)

        except Exception as error:
            messagebox.showerror("X-Intercept", f"""An error occured whilst calculating the X-intercept.\n
Error:   {type(error).__name__}
Message: {error.args[0]}""")




    def GetListOfEquations(self):
        array = [i.get() for i in self.entries]
        self.ReplaceConstantWords(array)
        return array


    def ReplaceConstantWords(self, array):
        for i, string in enumerate(array):
            string = string.replace("golden", "ϕ")
            string = string.replace("pi", "π")
            string = string.replace("euler", "e")
            string = string.replace(">=", "≥")
            string = string.replace("<=", "≤")
            self.entries[i].set(string)


    def UpdateEquationNumberLabels(self, equationsList, selected, i):
        self.currentEquation = selected
        self.labels[i].forget()

        if equationsList[i] != "":
            colour = colours[graphColours[i % len(graphColours)]].hex
        else:
            colour = colours["black"].hex

        fontNum = 4 if i == selected else 3
        label = self.CreateNewLabel(f"  [{i+1}]  ", fontNum, colour)
        label.grid(row=3+i, column=0)
        self.labels[i] = label

        

    def CreateFonts(self):
        self.fonts = [
            Font(family="monofonto", size=20, weight="bold"),
            Font(family="monofonto", size=13),
            Font(family="monofonto", size=11, weight="bold"),
            Font(family="monofonto", size=11),
            Font(family="monofonto", size=9),
            Font(family="monofonto", size=8),
            Font(family="monofonto", size=12)
        ]



    def CreateLabel(self, text, fontNum, placement, root=None):
        if root is None:
            root = self.root

        lbl = Label(root, text=text)
        lbl.config(font=self.fonts[fontNum])
        lbl.place(relx=placement[0], rely=placement[1], relwidth=placement[2], relheight=placement[3])
        return lbl


    def CreateLabelFrame(self, text, fontNum, placement, root=None):
        if root is None:
            root = self.root

        lf = LabelFrame(root, text=text)
        lf.config(font=self.fonts[fontNum])
        lf.place(relx=placement[0], rely=placement[1], relwidth=placement[2], relheight=placement[3])
        return lf
        

    def CreateButton(self, text, fontNum, methodReference, placement, root=None):
        if root is None:
            root = self.root

        btn = Button(root, text=text, command=methodReference)
        btn.config(font=self.fonts[fontNum])
        btn.place(relx=placement[0], rely=placement[1], relwidth=placement[2], relheight=placement[3])
        return btn
        

    def CreateEntry(self, strVar, fontNum, placement, root=None):
        if root is None:
            root = self.root

        entry = Entry(root, textvariable=strVar)
        entry.config(font=self.fonts[fontNum])
        entry.place(relx=placement[0], rely=placement[1], relwidth=placement[2], relheight=placement[3])
        return entry





    def AskToHighlightPoints(self, title, content, points):
        pointWord = "these points" if len(points) > 1 else "this point"
        content += f"\nWould you like to highlight {pointWord} in the graph window?"

        result = messagebox.askquestion(title, content, icon="info")

        if result == "yes":
            self.graphUI.highlightedPoints.extend(points)



class NotFoundException(Exception):
    pass