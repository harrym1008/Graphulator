from tkinter import *
from tkinter.font import Font


root = Tk()

fonts = [
    Font(family="monofonto", size=20, weight="bold"),
    Font(family="monofonto", size=13),
    Font(family="monofonto", size=11, weight="bold"),
    Font(family="monofonto", size=11),
    Font(family="monofonto", size=9),
    Font(family="monofonto", size=8),
    Font(family="monofonto", size=12)
]


root.geometry("350x600")

lbl = Label(root, text="Graphulator")
lbl.config(font=fonts[0])
lbl.place(relx=0.02, rely=0.01, relheight=0.07, relwidth=0.85)

btn = Button(root, text="Reset")
btn.config(font=fonts[3])
btn.place(relx=0.85, rely=0.02, relheight=0.05, relwidth=0.14)

equationInputLabelFrame = LabelFrame(root, text="Equation Input")
equationInputLabelFrame.config(font=fonts[1])
equationInputLabelFrame.place(relx=0.04, rely=0.08, relheight=0.49, relwidth=0.92)

calculationsLabelFrame = LabelFrame(root, text="Calculations")
calculationsLabelFrame.config(font=fonts[1])
calculationsLabelFrame.place(relx=0.04, rely=0.57, relheight=0.25, relwidth=0.92)

dataLabelFrame = LabelFrame(root, text="Program Data")
dataLabelFrame.config(font=fonts[1])
dataLabelFrame.place(relx=0.04, rely=0.84, relheight=0.15, relwidth=0.92)

# Data label frame
dataTextBox = Text(dataLabelFrame)
dataTextBox.insert(INSERT, \
'''Offset:    X = 2134.3214,  Y = 532.123286
Zoom:      52442.204%
Selected:  [4] y = sin(x)''')
dataTextBox.config(font=fonts[4], state="disabled")
dataTextBox.place(relx=0.02, rely=0, relheight=0.98, relwidth=0.96)


# Equation Input Frame
entries = [StringVar() for i in range(10)]

for i in range(10):
    equLbl = Label(equationInputLabelFrame, text=f"[{i+1}]")
    equLbl.config(font=fonts[2])
    equLbl.place(relx=0, rely=0.1*i, relheight=0.09, relwidth=0.15)    

    entry = Entry(equationInputLabelFrame, textvariable=entries[i])
    entry.config(font=fonts[6])
    entry.place(relx=0.2, rely=0.1*i, relheight=0.09, relwidth=0.8) 


# Calculations Frame
btns = [Button(calculationsLabelFrame, text="Y-Intercept"),
        Button(calculationsLabelFrame, text="X-Intercept"),
        Button(calculationsLabelFrame, text="Intersection")
]

for i, btn in enumerate(btns):
    btn.config(font=fonts[3])
    btn.place(relx=0.05, rely=i*0.25, relheight=0.23, relwidth=0.4)

btn = Button(calculationsLabelFrame, text="Eval X")
btn.config(font=fonts[3])
btn.place(relx=0.05, rely=0.75, relheight=0.23, relwidth=0.2)

btn = Button(calculationsLabelFrame, text="Eval Y")
btn.config(font=fonts[3])
btn.place(relx=0.25, rely=0.75, relheight=0.23, relwidth=0.2)


# Frames

intersectionLabelFrame = LabelFrame(calculationsLabelFrame, text="Intersection")
intersectionLabelFrame.config(font=fonts[3])
intersectionLabelFrame.place(relx=0.5, rely=-0.05, relheight=0.5, relwidth=0.45)

evaluateLabelFrame = LabelFrame(calculationsLabelFrame, text="Evaluate")
evaluateLabelFrame.config(font=fonts[3])
evaluateLabelFrame.place(relx=0.5, rely=0.475, relheight=0.5, relwidth=0.45)

# Intersections
dropdownOptions = [f"{i+1}" for i in range(10)]
intsectStringVars = [StringVar(intersectionLabelFrame, f"{i+1}") for i in range(2)]
dropdowns = [OptionMenu(intersectionLabelFrame, intsectStringVars[i], *dropdownOptions) for i in range(2)]
[dd.config(font=fonts[2]) for dd in dropdowns]

dropdowns[0].place(relx=0, rely=0, relheight=1, relwidth=0.5)
dropdowns[1].place(relx=0.5, rely=0, relheight=1, relwidth=0.5)

# Evaluate functionality
evaluateStringVars = [StringVar(evaluateLabelFrame, "") for i in range(2)]
lbl = Label(evaluateLabelFrame, text=f"X =")
lbl.config(font=fonts[4])
lbl.place(relx=0, rely=-0.06, relheight=0.5, relwidth=0.3)
lbl = Label(evaluateLabelFrame, text=f"Y =")
lbl.config(font=fonts[4])
lbl.place(relx=0, rely=0.44, relheight=0.5, relwidth=0.3)

evalEntries = [Entry(evaluateLabelFrame, textvariable=evaluateStringVars[i]) for i in range(2)]
[entry.config(font=fonts[4]) for entry in evalEntries]
evalEntries[0].place(relx=0.25, rely=-0.06, relheight=0.5, relwidth=0.7)
evalEntries[1].place(relx=0.25, rely=0.44, relheight=0.5, relwidth=0.7)


root.mainloop()