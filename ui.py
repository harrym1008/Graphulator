from tkinter import *
from tkinter import messagebox
from tkinter.font import Font
from PIL import Image, ImageTk

from colours import *



class UserInterface:
    def __init__(self, killMethodReference):
        self.root = Tk()
        self.root.title("Graphulator v4")
        self.root.protocol("WM_DELETE_WINDOW", killMethodReference)  
        self.root.iconbitmap("Images/icon.ico")
        # This makes it run the Kill method when the X button is pressed in the top right of the window

        self.CreateFonts()
        self.CreateImages()
        self.CreateWindow()

        self.helpOpen = False



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
            entry.grid(row=3+i, column=1)

            image = Label(self.root, image=self.tkImages[0])
            image.grid(row=3+i, column=2)
            self.errorImages.append(image)

        button = Button(self.root, text="Help", command=self.HelpWindow)
        button.config(font=self.fonts[1])
        button.grid(row=16, column=0)


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
        self.labels[i].forget()

        if equationsList[i] != "":
            colour = colours[graphColours[i % len(graphColours)]].hex
        else:
            colour = colours["black"].hex

        fontNum = 4 if i == selected else 2
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

        

    def DeactivateHelpWindow(self, top):
        top.destroy()
        self.helpOpen = False
    

        

    def CreateFonts(self):
        self.fonts = [
            Font(family="monofonto", size=20, weight="bold"),
            Font(family="monofonto", size=10),
            Font(family="monofonto", size=10),
            Font(family="monofonto", size=11),
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

