import tkinter as tk
import turtle, math, random

GRAPH_WIDTH = GRAPH_HEIGHT = 700
INFINITY_POS = GRAPH_WIDTH * 2
GRAPH_INCREASE = 1

BOUNDS = {"x": [-GRAPH_WIDTH // 2, GRAPH_WIDTH // 2 - 1],
          "y": [-GRAPH_HEIGHT // 2, GRAPH_WIDTH // 2 - 1]}

REPLACE = {
    "^": "**",
    "asin(": "InverseTrig('s', ",
    "acos(": "InverseTrig('c', ",
    "atan(": "InverseTrig('t', ",
    "sin(": "math.sin(",
    "cos(": "math.cos(",
    "tan(": "math.tan(",
    "floor(": "math.floor(",
    "ceiling(": "math.ceil(",

    "skip": "skip"}

equation = ""
zoom = 30
processing = False

ERROR_MSG = ["Success",  # 0
             "Improper equation notation",  # 1
             "Empty equation input",  # 2
             "Out of domain"  # 3
             ]

def InverseTrig(type, val):
    if type == "s":
        return math.asin(val)
    elif type == "c":
        return math.acos(val)
    else:
        return math.atan(val)


def FloatRange(start, stop, step):
    n = []
    while start < stop:
        n.append(start)
        start += step
    return n


def DrawAxis():
    t.pencolor("black")
    screen.tracer(0)
    for i in range(BOUNDS["x"][0], BOUNDS["x"][1], 50):
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


def DrawFunction():
    screen.tracer( math.ceil(3 * GRAPH_INCREASE))

    t.penup()
    t.pensize(5)
    t.pencolor("red")

    lastWasInfinity = False

    for x in FloatRange(BOUNDS["y"][0] / zoom, BOUNDS["y"][1] / zoom, 1 / zoom / GRAPH_INCREASE):
        try:
            y = eval(equation)
            print(f"x = {x}: y = {y}")
            t.goto(x * zoom, y * zoom)
            t.pendown()
            # if lastWasInfinity:
            #    t.penup()
            #    lastWasInfinity = False
        except ZeroDivisionError as e:  # infinity
            print(e)
            # t.pendown()
            # lastWasInfinity = True
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

    if equation == "":
        return 2, None
    try:
        x = random.randint(-100, 100)
        eval(equation)
    except Exception as e:
        if str(e) == "math domain error":
            return 3, None
        return 1, str(e)
    return 0, None


def ThrowError(code=0, ttl=None, extraData=None):
    msg = f"Code: {str(code)}\n{ERROR_MSG[code]}"

    if extraData is not None:
        msg += f"\n\n{extraData}"
    if ttl is None:
        ttl = f"Error!"

    tk.messagebox.showerror(title=ttl, message=msg)


def GraphProcess():
    global zoom

    zoom = float(zoomEntry.get())
    success = UpdateEquation(entry1.get())

    if success[0] != 0:
        ThrowError(success[0], extraData=success[1])
        return

    screen.clearscreen()
    DrawAxis()
    DrawFunction()
    DrawBorder(4)


if __name__ == "__main__":
    window = tk.Tk()

    title = tk.Label(window, text="  Graphulator   ")
    author = tk.Label(window, text="A graphing calculator made by Harrison McGrath")
    title.config(font=("Arial", 20, "bold"))
    author.config(font=("Arial", 12))
    title.grid(row=0, column=0)
    author.grid(row=0, column=1)

    canvas = turtle.Canvas(master=window, width=GRAPH_WIDTH, height=GRAPH_HEIGHT)
    canvas.grid(padx=2, pady=2, row=1, column=0, rowspan=16, columnspan=16)  # , sticky='nsew')
    screen = turtle.TurtleScreen(canvas)
    screen.tracer(0)
    t = turtle.RawTurtle(screen)
    t.hideturtle()
    t.speed(100)

    graphButton = tk.Button(master=window, text="Update graph!", command=GraphProcess)
    graphButton.config(fg="black")
    graphButton.grid(padx=2, pady=2, row=1, column=16, rowspan=1, columnspan=2, sticky='nsew')

    entry1 = tk.Entry(master=window)
    entry1.grid(row=2, column=16)

    zoomEntry = tk.Entry(master=window)
    zoomEntry.grid(row=3, column=16)
    zoomEntry.insert(0, "50")

    DrawAxis()
    DrawBorder(4)

    window.mainloop()
