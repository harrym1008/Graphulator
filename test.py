import tkinter as tk
import turtle, math

GRAPH_WIDTH = GRAPH_HEIGHT = 700

BOUNDS = {"x": [-GRAPH_WIDTH // 2, GRAPH_WIDTH // 2-1],
          "y": [-GRAPH_HEIGHT // 2, GRAPH_WIDTH // 2-1]}

equation = ""
zoom = 10


def FloatRange(start, stop, step):
    n = []
    while start < stop:
        n.append(start)
        start += step
    return n



def DrawAxis():
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
    DrawBorder()



def UpdateEquation(eq):
    global equation
    equation = eq.replace("sin(", "math.sin(").replace("^", "**")



def DrawFunction():
    screen.tracer(3)
    UpdateEquation(entry1.get())
    print(equation)

    t.penup()
    t.pensize(5)
    t.pencolor("red")

    for x in FloatRange(BOUNDS["y"][0] / zoom, BOUNDS["y"][1] / zoom, 1/zoom):
        try:
            y = eval(equation)
            t.goto(x*zoom, y*zoom)
            t.pendown()
        except ZeroDivisionError:
            t.penup()
            continue

    screen.tracer(0)
    screen.update()



def DrawBorder(width = 5):
    t.penup()
    t.pencolor("black")
    t.pensize(width)
    t.goto(BOUNDS["x"][0], BOUNDS["y"][0])
    t.pendown()
    t.goto(BOUNDS["x"][1], BOUNDS["y"][0])
    t.goto(BOUNDS["x"][1], BOUNDS["y"][1])
    t.goto(BOUNDS["x"][0], BOUNDS["y"][1])
    t.goto(BOUNDS["x"][0], BOUNDS["y"][0])


def GraphProcess():
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

    DrawAxis()
    window.mainloop()
