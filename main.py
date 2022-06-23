import tkinter as tk
from tkinter import messagebox

import pygame
import standardform
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

threads = []


def Initiate():
    global guiScreen, screenSize
    title = tk.Label(guiScreen, text="Graphulator   ")
    title.config(font=("Arial", 20, "bold"))
    title.grid(row=0, column=0, columnspan=3)
    author = tk.Label(guiScreen, text="A graphing calculator made by Harrison McGrath", justify=tk.LEFT)
    author.config(font=("Arial", 8))
    author.grid(row=1, column=0, columnspan=3)

    equations = []

    EQUATIONS_AMOUNT = 10
    EQUATIONS_OFFSET = 2

    for row in range(EQUATIONS_AMOUNT):
        txt = tk.Label(guiScreen, text=f"   Equation {row + 1}")
        txt.config(font=("Arial", 12))
        txt.grid(row=row + EQUATIONS_OFFSET, column=0)
        txt = tk.Label(guiScreen, text=f"   y =")
        txt.config(font=("Arial", 12, "bold"))
        txt.grid(row=row + EQUATIONS_OFFSET, column=1)
        equations.append(tk.Entry(master=guiScreen))
        equations[row].grid(row=row + EQUATIONS_OFFSET, column=2)


def Kill():
    global running

    if not messagebox.askyesno("Quit", "Do you really wish to quit?"):
        return False

    running = False

    for t in threads:
        t.terminate()

    pygame.quit()
    guiScreen.destroy()
    quit()

    return True


def MainLoop():
    global screenSize, running, graphScreen, guiScreen, clock

    while running:
        # main logic

        '''graph.offset[0] += 0.3 * deltatime.GetMultiplier()

        if graph.offset[0] > 40:
            graph.offset[0] = -40

        graph.offset[1] += 0.2 * deltatime.GetMultiplier()

        if graph.offset[1] > 30:
            graph.offset[1] = -30'''

        graph.DrawAxis(graphScreen)
        # drawfunc.SineTest(graphScreen)
        graph.DrawDebugText(graphScreen)
        graph.WritePosOnGraph(pygame.mouse.get_pos(), graphScreen)

        # updating screens, quitting from pygame, resizing and waiting for 60 targetFPS

        guiScreen.update()
        graph.clock.tick(targetFPS)
        deltatime.Update()

        pygame.display.flip()
        PygameInput()

        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                if Kill():
                    break
            if e.type == pygame.VIDEORESIZE:
                graphScreen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                screenSize = [e.w, e.h]

                graph.screenSize = screenSize
                graph.screenCentre = [e.w // 2, e.h // 2]


def PygameInput():
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        graph.offset[0] += panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_RIGHT]:
        graph.offset[0] -= panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_UP]:
        graph.offset[1] += panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_DOWN]:
        graph.offset[1] -= panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_KP_PLUS]:
        graph.zoom *= 1 + zoomSpeed * deltatime.GetMultiplier()
    if keys[pygame.K_KP_MINUS]:
        graph.zoom /= 1 + zoomSpeed * deltatime.GetMultiplier()


graphScreen = None
guiScreen = None

if __name__ == "__main__":
    guiScreen = tk.Tk()
    guiScreen.title("Graphulator v2")

    pygame.init()
    graphScreen = pygame.display.set_mode(screenSize, pygame.RESIZABLE)
    print(graphScreen)
    pygame.display.set_caption("Display Window")
    graphScreen.fill(colours.PygameColour("white"))

    graph.CreateFont()

    # run Kill() when the tkinter window is closed
    guiScreen.protocol("WM_DELETE_WINDOW", Kill)

    # initiation code
    Initiate()
    MainLoop()


def GetResolution():
    return screenSize
