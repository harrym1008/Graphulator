from tkinter import *
from tkinter import messagebox
from tkinter.font import Font
from PIL import Image, ImageTk

from colours import *
from graphui import GraphUserInterface

import drawfunc
from evaluate import *
from numstr import *


numbersDropdown = [str(i+1) for i in range(10)]



class UserInterface:
    def __init__(self, graphUI, killMethodReference):
        self.root = Tk()
        self.root.title("Graphulator v4")
        self.root.protocol("WM_DELETE_WINDOW", killMethodReference)  
        self.root.iconbitmap("Images/icon.ico")
        # This makes it run the Kill method when the X button is pressed in the top right of the window

        self.CreateFonts()
        self.CreateImages()
        self.CreateWindow()

        self.helpOpen = False
        self.currentEquation = 0

        self.graphUI: GraphUserInterface = graphUI



    def CreateWindow(self):
        self.CreateNewLabel("Graphulator v4", 0).grid(row=0, column=0, columnspan=8)
        self.CreateNewLabel("A graphing calculator by Harrison McGrath", 1).grid(row=1, column=0, columnspan=8)
        self.CreateNewLabel("", 1).grid(row=2, column=0, columnspan=4)

        self.entries = [StringVar(self.root) for i in range(10)]
        self.labels = []
        self.errorImages = []

        for i in range(10):
            label = self.CreateNewLabel(f"  [{i+1}]  ", 4)
            label.grid(row=3+i, column=0)
            self.labels.append(label)

            entry = Entry(self.root, textvariable=self.entries[i])
            entry.config(font=self.fonts[3])
            entry.grid(row=3+i, column=1, columnspan=2)

            image = Label(self.root, image=self.tkImages[0])
            image.grid(row=3+i, column=3)
            self.errorImages.append(image)

        # Create help button
        button = Button(self.root, text="Help", command=self.HelpWindow)
        button.config(font=self.fonts[1])
        button.grid(row=16, column=0, columnspan=2)
        
        # Create Y-intercept button
        button = Button(self.root, text="Y-Intercept", command=self.DisplayYIntercept)
        button.config(font=self.fonts[1])
        button.grid(row=17, column=0, columnspan=2)
        
        # Create X-intercept button
        button = Button(self.root, text="X-Intercept (Root)", command=self.DisplayXIntercept)
        button.config(font=self.fonts[1])
        button.grid(row=18, column=0, columnspan=2)
        
        # Create Intersection button
        button = Button(self.root, text=" Find Intersection ", command=self.DisplayIntersection)
        button.config(font=self.fonts[1])
        button.grid(row=16, column=2, columnspan=2)
        
        self.CreateNewLabel("Equations for intsect:", 2).grid(row=17, column=2, columnspan=2)

        # Create the dropdowns that are used in the intersection parameters
        self.intsectStringVars = [StringVar(self.root, f"{i+1}") for i in range(2)]
        self.intsectDropdowns = [OptionMenu(self.root, self.intsectStringVars[i], *numbersDropdown) for i in range(2)]
        [dd.config(font=self.fonts[1]) for dd in self.intsectDropdowns]
        self.intsectDropdowns[0].grid(row=18, column=2)
        self.intsectDropdowns[1].grid(row=18, column=3)

        
        # Create Toggle Equals To button
        button = Button(self.root, text="> ⇄ ≥", command=self.ToggleOrEqualTo)
        button.config(font=self.fonts[1])
        button.grid(row=19, column=0, columnspan=2)


    # This method toggles the "or equal to" for > and < in the selected equation
    def ToggleOrEqualTo(self):
        array = list(self.entries[self.currentEquation].get())

        for i in range(len(array)):
            letter = array[i]

            if letter == ">":
                letter = "≥"
            elif letter == "≥":
                letter = ">"
            elif letter == "<":
                letter = "≤"
            elif letter == "≤":
                letter = "<"

            array[i] = letter

        string = ""
        string = string.join(array)

        self.entries[self.currentEquation].set(string)




    # This code finds the location(s) of the intersection, then creates a window displaying where
    def DisplayIntersection(self):
        x, y = sp.symbols("x y")
        equNums = int(self.intsectStringVars[0].get())-1, int(self.intsectStringVars[1].get())-1
        strEqus = self.entries[ equNums[0] ].get(), self.entries[ equNums[1] ].get() 

        header = f"{equNums[0]+1}: {strEqus[0]}\n{equNums[1]+1}: {strEqus[1]}"

        try:

            strEqus = UnreplaceEquation(strEqus[0]), UnreplaceEquation(strEqus[1])
            equ1 = drawfunc.PlottedEquation.ProduceSympyEquation(strEqus[0], getHandSides=False)
            equ2 = drawfunc.PlottedEquation.ProduceSympyEquation(strEqus[1], getHandSides=False)

            intersections = sp.solve([equ1, equ2], (x, y))
            intsectString = ""

            points = []

            for i in range(len(intersections[0])):
                x = float(sp.N(intersections[0][i]))
                y = float(sp.N(intersections[1][i]))
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
        x, y = 0, sp.Symbol("y")

        try:
            strEqu = UnreplaceEquation(self.entries[self.currentEquation].get())
            equ = drawfunc.PlottedEquation.ProduceSympyEquation(strEqu, getHandSides=False)
            print(equ)
            ySolutions = drawfunc.PlottedEquation.ProduceEquationSolutions(equ, "y")
            
            if len(ySolutions) == 0:
                messagebox.showwarning("X-Intercept", "This equation does not have an X-intercept.")
                return

            pointsString = "\n"
            for sol in ySolutions:
                pointsString += f"(0, {NStr(eval(sol))})\n"

            string = f"The Y-intercept is at point{'' if len(ySolutions) == 1 else 's'}:\n{pointsString}"
            messagebox.showinfo("Y-Intercept", string)

        except Exception as error:
            messagebox.showerror("Y-Intercept", f"""An error occured whilst calculating the Y-Intercept.\n
Error:   {type(error).__name__}
Message: {error.args[0]}""")
        
        
    def DisplayXIntercept(self):
        try:
            x, y = sp.Symbol("x"), 0
            strEqu = UnreplaceEquation(self.entries[self.currentEquation].get())
            equ = drawfunc.PlottedEquation.ProduceSympyEquation(strEqu, getHandSides=False)
            xSolutions = drawfunc.PlottedEquation.ProduceEquationSolutions(equ, "x")
            
            if len(xSolutions) == 0:
                messagebox.showwarning("X-Intercept", "This equation does not have an X-intercept.")
                return

            pointsString = "\n"
            for sol in xSolutions:
                pointsString += f"({NStr(eval(sol))}, 0)\n"

            string = f"The X-intercept is at point{'' if len(xSolutions) == 1 else 's'}:\n{pointsString}"
            messagebox.showinfo("X-Intercept", string)

        except Exception as error:
            messagebox.showerror("X-Intercept", f"""An error occured whilst calculating the X-Intercept.\n
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





    def HelpWindow(self):
        if self.helpOpen:
            return
        self.helpOpen = True

        top = Toplevel()
        top.title("Help Window")
        top.protocol("WM_DELETE_WINDOW", lambda: self.DeactivateHelpWindow(top))  

        # Draw the help window
        messagebox.showinfo("Hello", '''
The graphs:
    5x
    2x+1

intersect at the points:
    (0, 0)
    (10, 20)
''')
        self.helpOpen = False

        

    def DeactivateHelpWindow(self, top):
        top.destroy()
        self.helpOpen = False
    

        

    def CreateFonts(self):
        self.fonts = [
            Font(family="monofonto", size=20, weight="bold"),
            Font(family="monofonto", size=10),
            Font(family="monofonto", size=8),
            Font(family="monofonto", size=12),
            Font(family="monofonto", size=12, weight="bold", ),
        ]


    def CreateImages(self):
        self.files = [
            "Images/blank.png",
            "Images/no.png"
        ]

        self.tkImages = [ImageTk.PhotoImage(Image.open(f).resize((16, 16), Image.ANTIALIAS)) for f in self.files]




    def CreateNewLabel(self, text, font, colour="black"):
        lbl = Label(self.root, text=text)
        lbl.config(font=self.fonts[font], fg=colour)
        return lbl




    def AskToHighlightPoints(self, title, content, points):
        pointWord = "these points" if len(points) > 1 else "this point"
        content += f"\nWould you like to highlight {pointWord} in the graph window?"

        result = messagebox.askquestion(title, content, icon="info")

        if result:
            self.graphUI.highlightedPoints.extend(points)
