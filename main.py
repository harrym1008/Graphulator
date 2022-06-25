import time
import tkinter as tk
from tkinter import messagebox

import numpy
import pygame
import numstr
import colours
import deltatime
import drawfunc
import graph

clock = None

running = True
screenSize = [800, 600]
targetFPS = 60

panSpeed = 2
zoomSpeed = 0.05

graphMouseStart = [-1, -1]
mouseStart = [-1, -1]
mouseMoved = (0, 0)
mouseFocusTime = 0

equations = [ "numpy.tan( math.floor( x ** 2 ) )" ]


def Initiate():
    global guiScreen, screenSize
    title = tk.Label(guiScreen, text="Graphulator   ")
    title.config(font=("Arial", 20, "bold"))
    title.grid(row=0, column=0, columnspan=3)
    author = tk.Label(guiScreen, text="A graphing calculator made by Harrison McGrath", justify=tk.LEFT)
    author.config(font=("Arial", 8))
    author.grid(row=1, column=0, columnspan=3)

    equEntries = []

    EQUATIONS_AMOUNT = 10
    EQUATIONS_OFFSET = 2

    for row in range(EQUATIONS_AMOUNT):
        txt = tk.Label(guiScreen, text=f"   Equation {row + 1}")
        txt.config(font=("Arial", 12))
        txt.grid(row=row + EQUATIONS_OFFSET, column=0)
        txt = tk.Label(guiScreen, text=f"   y =")
        txt.config(font=("Arial", 12, "bold"))
        txt.grid(row=row + EQUATIONS_OFFSET, column=1)
        equEntries.append(tk.Entry(master=guiScreen))
        equEntries[row].grid(row=row + EQUATIONS_OFFSET, column=2)


def Kill():
    global running

    if not messagebox.askyesno("Quit", "Do you really wish to quit?"):
        return False

    running = False

    pygame.quit()
    guiScreen.destroy()
    quit()

    return True


def MainLoop():
    global screenSize, running, graphScreen, guiScreen, clock

    timer = 0
    timeToExec = 0


    while running:
        # main logic

        graph.DrawAxis(graphScreen, timeToExec)

        for eq in equations:
            drawfunc.SineTest(graphScreen, graph.bounds, eq)


        graph.WritePosOnGraph(pygame.mouse.get_pos(), graphScreen, mouseFocusTime)


        # updating screens, quitting from pygame, resizing and waiting for 60 FPS

        timeToExec = time.perf_counter() - timer
        graph.clock.tick(targetFPS)
        timer = time.perf_counter()
        deltatime.Update()

        guiScreen.update()
        pygame.display.flip()

        events = pygame.event.get()
        PygameInput(events)

        for e in events:

            if e.type == pygame.QUIT:
                if Kill():
                    break
            if e.type == pygame.VIDEORESIZE:
                graphScreen = pygame.display.set_mode((e.w, e.h), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                screenSize = [e.w, e.h]

                graph.screenSize = screenSize
                graph.screenCentre = [e.w // 2, e.h // 2]


def PygameInput(events):
    global mouseStart, mouseMoved, graphMouseStart, mouseFocusTime

    keys = pygame.key.get_pressed()

    # Keyboard controls
    if keys[pygame.K_LEFT]:
        graph.offset[0] -= panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_RIGHT]:
        graph.offset[0] += panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_UP]:
        graph.offset[1] -= panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_DOWN]:
        graph.offset[1] += panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_KP_PLUS]:
        graph.zoom *= 1 + zoomSpeed
    if keys[pygame.K_KP_MINUS]:
        graph.zoom /= 1 + zoomSpeed

    # Reset offset and panning
    if keys[pygame.K_r]:
        graph.zoom = 10
        graph.offset = [0, 0]


    # Panning the graph with the mouse
    mouseClicked = pygame.mouse.get_pressed()

    if mouseClicked[0] and mouseStart == [-1, -1]:
        mouseStart = pygame.mouse.get_pos()
        print("updating graph mouse start")
        graphMouseStart = [graph.offset[0], graph.offset[1]]

    if not mouseClicked[0] and mouseStart != [-1, -1]:
        mouseMoved = tuple(numpy.subtract(pygame.mouse.get_pos(), mouseStart))
        mouseStart = [-1, -1]
        graphMouseStart = [-1, -1]

    elif mouseClicked[0]:
        mouseMoved = tuple(numpy.subtract(pygame.mouse.get_pos(), mouseStart))

    # print((mouseStart, mouseMoved, graphMouseStart))

    if mouseStart != [-1, -1]:
        graph.offset[0] = graphMouseStart[0] - mouseMoved[0] / graph.zoom
        graph.offset[1] = graphMouseStart[1] - mouseMoved[1] / graph.zoom

    # Zoom in and out with the scroll wheel

    for e in events:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 4:
                graph.zoom *= 1 + zoomSpeed
            elif e.button == 5:
                graph.zoom /= 1 + zoomSpeed

    # Mouse focus
    if pygame.mouse.get_focused():
        mouseFocusTime = 0.25
    else:
        mouseFocusTime -= deltatime.deltaTime

    graph.zoom = round(graph.zoom, 10)


graphScreen = None
guiScreen = None

if __name__ == "__main__":
    guiScreen = tk.Tk()
    guiScreen.title("Graphulator v2")

    pygame.init()
    graphScreen = pygame.display.set_mode(screenSize, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    pygame.display.set_caption("Display Window")
    graphScreen.fill(colours.PygameColour("white"))

    graph.CreateFont()

    # run Kill() when the tkinter window is closed
    guiScreen.protocol("WM_DELETE_WINDOW", Kill)

    # initiation code
    Initiate()
    MainLoop()

