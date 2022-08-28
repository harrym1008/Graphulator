import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import tkinter as tk
from tkinter import messagebox

import pygame
import numpy

import deltatime
from graph import *
from ui import *
from colours import *
from numstr import *
from drawfunc import *


screenSize = (800, 600)
running = True
targetFPS = 60

panSpeed = 2
zoomSpeed = 0.05
graphMouseStart = [-1, -1]
mouseStart = [-1, -1]
mouseMoved = (0, 0)
mouseFocusTime = 0


def Kill():
    global running

    running = False
    return not running


def PygameInput(events, graph):
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

    if keys[pygame.K_ESCAPE]:
        Kill()

    # Panning the graph with the mouse
    mouseClicked = pygame.mouse.get_pressed()

    if mouseClicked[0] and mouseStart == [-1, -1]:
        mouseStart = pygame.mouse.get_pos()
        # print("updating graph mouse start")
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

    graph.zoom = SigFig(graph.zoom, 6)




if __name__ == "__main__":
    guiScreen = tk.Tk()
    guiScreen.title("Graphulator v3")
    guiScreen.protocol("WM_DELETE_WINDOW", Kill)

    pygame.init()
    clock = pygame.time.Clock()
    graphScreen = pygame.display.set_mode(screenSize, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    graphScreen.fill(colours["white"].colour)

    # init code
    AssignFonts()
    graph = Graph(screenSize)
    functionHolder = FunctionHolder()
    functionHolder.AppendEquation(graph, "x", colours["red"].colour)


    # Start main loop
    while running:
        graph.DrawBaseGraphSurface()        

        graphScreen.fill(colours["white"].colour)
        graphScreen.blit(graph.baseSurface, (0, 0))

        # blit all surfaces to the screen

        functionHolder.UpdateEquations(graph)

        guiScreen.update()
        pygame.display.flip()
        
        # Wait for 60 FPS
        # clock.tick(targetFPS)
        deltatime.Update()

        events = pygame.event.get()
        PygameInput(events, graph)

        for e in events:
            if e.type == pygame.QUIT:
                if Kill():
                    break
            if e.type == pygame.VIDEORESIZE:
                graphScreen = pygame.display.set_mode((e.w, e.h),
                                                      pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                screenSize = (e.w, e.h)

                

