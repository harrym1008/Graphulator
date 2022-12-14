from tkinter import *
from tkinter import messagebox
from tkinter.font import Font
from multiprocessing import cpu_count

from colours import *
from graphui import GraphUserInterface

import drawfunc
from uimath import UIMath
from evaluate import *
from numstr import *


numbersDropdown = [str(i+1) for i in range(10)]



class UserInterface:
    def __init__(self, graphUI, killMethodReference):
        self.root = Tk()
        self.root.title("Graphulator")
        self.root.geometry("350x600")

        if cpu_count() > 2:
            self.root.geometry("438x750")

        self.root.protocol("WM_DELETE_WINDOW", killMethodReference)
        # This makes it run the Kill method when the X button is pressed in the top right of the window

        self.CreateFonts()
        self.CreateWindow()

        self.currentEquation = 0

        self.graphUI: GraphUserInterface = graphUI



    def CreateWindow(self):
        self.CreateLabel("Graphulator", 0, (0.02, 0.01, 0.85, 0.07) )

        self.equLF = self.CreateLabelFrame("Equation Input", 1, (0.04, 0.08, 0.92, 0.49))
        self.calcLF = self.CreateLabelFrame("Calculations", 1, (0.04, 0.57, 0.92, 0.25))
        self.dataLF = self.CreateLabelFrame("Program Data", 1, (0.04, 0.84, 0.92, 0.15))

        self.entries = []
        for i in range(10):
            self.entries.append(StringVar(self.equLF))
            self.CreateLabel(f"[{i+1}]", 2, (0, 0.1*i, 0.15, 0.09), self.equLF) 

            entry = Entry(self.equLF, textvariable=self.entries[i])
            entry.config(font=self.fonts[6])
            entry.place(relx=0.2, rely=0.1*i, relheight=0.09, relwidth=0.8) 





    # This code finds the location(s) of the intersection, then creates a window displaying where
    def DisplayIntersection(self):
        x, y = sp.symbols("x y")
        equNums = int(self.intsectStringVars[0].get())-1, int(self.intsectStringVars[1].get())-1
        strEqus = self.entries[ equNums[0] ].get(), self.entries[ equNums[1] ].get() 

        header = f"{equNums[0]+1}: {strEqus[0]}\n{equNums[1]+1}: {strEqus[1]}"

        try:
            intersections = UIMath.FindIntersections(strEqus[0], strEqus[1])
            intsectString = ""

            points = []

            for intsect in intersections:
                x = float(intsect[0])
                y = float(intsect[1])
                points.append((x, y))

                intsectString += f"({NStr(x)}, {NStr(y)})\n"

            print(points)
            self.AskToHighlightPoints("Intersection", f"""{header}
                
The two graphs intersect at the point{'' if len(intersections[0]) == 1 else 's'}:

{intsectString}""", points)

        except Exception as error:
            raise error
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





    def AskToHighlightPoints(self, title, content, points):
        pointWord = "these points" if len(points) > 1 else "this point"
        content += f"\nWould you like to highlight {pointWord} in the graph window?"

        result = messagebox.askquestion(title, content, icon="info")

        if result:
            self.graphUI.highlightedPoints.extend(points)
