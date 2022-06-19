import tkinter as tk
from tkinter import messagebox

import colours
import graph
import time
import pygame


running = True
screenSize = [800, 600]
FPS = 60

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
        txt.grid(row=row+EQUATIONS_OFFSET, column=0)
        txt = tk.Label(guiScreen, text=f"   y =")
        txt.config(font=("Arial", 12, "bold"))
        txt.grid(row=row+EQUATIONS_OFFSET, column=1)
        equations.append(tk.Entry(master=guiScreen))
        equations[row].grid(row=row+EQUATIONS_OFFSET, column=2)




def Main():
    pass


def Kill():
    global running
    running = False

    if not messagebox.askyesno("Quit", "Do you really wish to quit?"):
        return False

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


        graph.offset[0] += 0.1
        graph.offset[1] += 1
        graph.DrawAxis(graphScreen)



        # updating screens, quitting from pygame, resizing and waiting for 60 FPS

        guiScreen.update()
        clock.tick(FPS)
        pygame.display.set_caption(f"Display Window - {round(clock.get_fps(), 2)} FPS")

        pygame.display.flip()

        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                if Kill():
                    break
            if e.type == pygame.VIDEORESIZE:
                graphScreen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                screenSize = [e.w, e.h]

                graph.screenSize = screenSize
                graph.screenCentre = [e.w//2, e.h//2]




if __name__ == "__main__":
    guiScreen = tk.Tk()
    guiScreen.title("Graphulator v2")

    pygame.init()
    graphScreen = pygame.display.set_mode(screenSize, pygame.RESIZABLE)
    pygame.display.set_caption("Display Window")
    graphScreen.fill(colours.PygameColour("white"))

    # run Kill() when the tkinter window is closed
    guiScreen.protocol("WM_DELETE_WINDOW", Kill)

    # initiation code
    Initiate()
    clock = pygame.time.Clock()
    MainLoop()

