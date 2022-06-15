import tkinter as tk
import tkinter.font as font
import turtle, math, random
import maths

GRAPH_WIDTH = 1000
GRAPH_HEIGHT = 750
INFINITY_POS = GRAPH_WIDTH * 2
GRAPH_INCREASE = 0.5
EQUATIONS_AMOUNT = 16


BOUNDS = {"x": [-GRAPH_WIDTH // 2, GRAPH_WIDTH // 2 - 1],
          "y": [-GRAPH_HEIGHT // 2, GRAPH_HEIGHT // 2 - 1]}

REPLACE = {
    "^": "**",
    "asin(": "maths.InverseTrig('s', ",
    "acos(": "maths.InverseTrig('c', ",
    "atan(": "maths.InverseTrig('t', ",
    "sin(": "math.sin(",
    "cos(": "math.cos(",
    "tan(": "math.tan(",
    "floor(": "math.floor(",
    "ceiling(": "math.ceil(",
    "log(": "maths.Logarithm(10, ",
    "log2(": "maths.Logarithm(2, ",
    "factorial(": "maths.StartFactorial(",

    "skip": "skip"}

equation = ""
zoom = 30
processing = False

ERROR_MSG = ["Success",  # 0
             "Improper equation notation",  # 1
             "Empty equation input",  # 2
             "Out of domain"  # 3
             ]

COLOURS = ["red",
           "blue",
           "lime green",
           "magenta",
           "gold",
           "blue violet",
           "dark orange",
           "deep sky blue"]



    


def FloatRange(start, stop, step, centre=None):
    if centre is not None:
        array = [centre]

        x = centre
        while x > start:
            x -= step
            array.append(x)
        x = centre
        while x < stop:
            x += step
            array.append(x)

        array.sort()
        return array

    n = []
    while start < stop:
        n.append(start)
        start += step
    return n


def DrawAxis():
    t.pencolor("black")
    screen.tracer(0)
    for i in FloatRange(BOUNDS["x"][0], BOUNDS["x"][1], zoom, 0):
        if i == BOUNDS["x"][0]:
            continue

        t.pensize(4 if i == 0 else 1)

        t.penup()
        t.goto(i, BOUNDS["y"][0])
        t.pendown()
        t.goto(i, BOUNDS["y"][1])
        t.penup()
        t.goto(BOUNDS["x"][0], i)
        t.pendown()
        t.goto(BOUNDS["x"][1], i)

    screen.update()


def DrawFunction(colour, iValue):
    screen.tracer(math.floor(3 * GRAPH_INCREASE) if instant.get() == 0 else 0)

    t.penup()
    t.pensize(5)
    t.pencolor(colour)

    i = iValue
    pi = math.pi

    first = True

    lastValue = 0
    extremeVal = [BOUNDS["y"][0] * 1.25, BOUNDS["y"][1] * 1.25]

    extremeVal[0] /= zoom
    extremeVal[1] /= zoom

    #print(f"Extreme value is {extremeVal}")
    #print(BOUNDS)

    for x in FloatRange(BOUNDS["x"][0] / zoom, BOUNDS["x"][1] / zoom, 1 / zoom / GRAPH_INCREASE, 0):
        try:
            n = x
            y = eval(equation)

            if ((lastValue > extremeVal[0] and y < -extremeVal[1]) or
                (lastValue < -extremeVal[1] and y < -extremeVal[0])) and not first:
                t.penup()

            first = False
            t.goto(x * zoom, y * zoom)
            t.pendown()
            lastValue = y

        except:
            continue

    screen.tracer(0)
    screen.update()


def DrawBorder(width=5):
    t.penup()
    t.pencolor("black")
    t.pensize(width)
    t.goto(BOUNDS["x"][0], BOUNDS["y"][0])
    t.pendown()
    t.goto(BOUNDS["x"][1], BOUNDS["y"][0])
    t.goto(BOUNDS["x"][1], BOUNDS["y"][1])
    t.goto(BOUNDS["x"][0], BOUNDS["y"][1])
    t.goto(BOUNDS["x"][0], BOUNDS["y"][0])
    screen.update()


def UpdateEquation(eq):
    global equation

    for pair in REPLACE.items():
        eq = eq.replace(pair[0], pair[1])

    equation = eq

    i = 1
    pi = math.pi

    if equation == "":
        return 2, None
    try:
        x = random.randint(-10, 10)
        n = x
        i = 1
        eval(equation)

    except Exception as e:
        if str(e) == "math domain error":
            return 0, None  # Remove!
            # return 3, None
        return 1, str(e)
    return 0, None


def ThrowError(code=0, ttl=None, extraData=None):
    msg = f"Code: {str(code)}\n{ERROR_MSG[code]}"

    if extraData is not None:
        msg += f"\n\n{extraData}"
    if ttl is None:
        ttl = f"Error!"

    tk.messagebox.showerror(title=ttl, message=msg)


def GraphProcess(equString, colour, iValue):
    success = UpdateEquation(equString)

    if success[0] != 0:
        success = (success[0], ("\n" + success[1]) if success[1] is not None else None)
        ThrowError(success[0], extraData=f"'{equString}'{(success[1]) if success[1] is not None else ''}")
        return

    DrawFunction(colour, iValue)


def ProcessAllGraphs():
    global zoom, GRAPH_INCREASE
    zoom = float(zoomEntry.get()) / 2
    if zoom == 0:
        zoom = 0.5
        zoomEntry.delete(0, "end")
        zoomEntry.insert(0, "1")

    GRAPH_INCREASE = float(accuracy.get())

    colourCount = 0
    counter = -1
    row = 1

    screen.clearscreen()
    DrawAxis()

    for i in entries:
        row += 1
        counter += 1

        if i.get() == "":
            x = tk.Label(window, text=f"Equation {counter + 1}")
            x.config(font=("Arial", 12), fg="black")
            x.grid(row=row, column=16)
            continue

        GraphProcess(i.get(), COLOURS[colourCount], counter + 1)

        x = tk.Label(window, text=f"Equation {counter + 1}")
        x.config(font=("Arial", 12), fg=COLOURS[colourCount])
        x.grid(row=row, column=16)

        colourCount = (colourCount + 1) % len(COLOURS)

    DrawBorder(4)
    screen.update()


def ClearEntries():
    for i in entries:
        i.delete(0, "end")



if __name__ == "__main__":
    window = tk.Tk(className="Graphulator")
    entriesFont = font.Font(size=16, weight="bold")

    title = tk.Label(window, text="  Graphulator   ")
    author = tk.Label(window, text="A graphing calculator made by Harrison McGrath")
    title.config(font=("Arial", 20, "bold"))
    author.config(font=("Arial", 12))
    title.grid(row=0, column=0)
    author.grid(row=0, column=1)

    canvas = turtle.Canvas(master=window, width=GRAPH_WIDTH, height=GRAPH_HEIGHT)
    canvas.grid(padx=2, pady=2, row=1, column=0, rowspan=24, columnspan=16)  # , sticky='nsew')
    screen = turtle.TurtleScreen(canvas)
    screen.tracer(0)
    t = turtle.RawTurtle(screen)
    t.hideturtle()
    t.speed(100)

    graphButton = tk.Button(master=window, text="Update Graph", command=ProcessAllGraphs)
    graphButton.config(fg="black", font=entriesFont)
    graphButton.grid(padx=2, pady=2, row=1, column=16, rowspan=1, columnspan=3, sticky='nsew')

    clearButton = tk.Button(master=window, text="Clear Equations", command=ClearEntries)
    clearButton.config(fg="black", font= font.Font(size=12, weight="bold") )
    clearButton.grid(padx=2, pady=2, row=0, column=18, rowspan=1, columnspan=1, sticky='nsew')

    entries = []
    i = 0
    for row in range(2, 2+EQUATIONS_AMOUNT):
        txt = tk.Label(window, text=f"Equation {i + 1}")
        txt.config(font=("Arial", 12))
        txt.grid(row=row, column=16)
        txt = tk.Label(window, text=f"   y =")
        txt.config(font=("Arial", 12, "bold"))
        txt.grid(row=row, column=17)
        entries.append(tk.Entry(master=window))
        entries[i].grid(row=row, column=18)
        i += 1

    entries[0].insert(0, "sin(x)")

    zoomEntry = tk.Entry(master=window)
    zoomEntry.grid(row=21, column=18)
    zoomEntry.insert(0, "100")

    zoomTxt = tk.Label(window, text="Zoom %")
    zoomTxt.config(font=("Arial", 16))
    zoomTxt.grid(row=21, column=16, columnspan=2)

    accuracy = tk.Entry(master=window)
    accuracy.grid(row=22, column=18)
    accuracy.insert(0, "1")

    accuracyTxt = tk.Label(window, text="Accuracy")
    accuracyTxt.config(font=("Arial", 16))
    accuracyTxt.grid(row=22, column=16, columnspan=2)

    instant = tk.IntVar()
    instantButton = tk.Checkbutton(window, text = "Instant drawing", variable=instant)
    instantButton.config(font=("Arial", 16))
    instantButton.grid(row=23, column=16, columnspan=3)

    zoom = 50
    ProcessAllGraphs()

    window.mainloop()
