import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
# Prevents the welcome message from pygame from spamming in the terminal

# External modules
import tkinter as tk
import pygame
import numpy as np
import sympy as sp

# Internal modules
import deltatime
import evaluate
from colours import *
from numstr import *
from timer import *
from graph import Graph
from graphui import GraphUserInterface
from graphrenderer import GraphRenderer
from funcmgr import FunctionManager
from ui import UserInterface

# Screen starts at this resolution by default
screenSize = (720, 480)
minScreenSize = (128, 128)

running = True
targetFPS = 60

panSpeed = 2.5
zoomSpeed = 0.05
graphMouseStart = [-1, -1]
mouseStart = [-1, -1]
mouseMoved = (0, 0)
mouseFocusTime = 0
mouseButtonDown = False


def Kill():
    # Sets global variable running to false, resulting in the closure of the program
    global running
    running = False


def PygameInput(events, graph):
    global mouseStart, mouseMoved, graphMouseStart, mouseFocusTime, mouseButtonDown

    keys = pygame.key.get_pressed()

    # Reset offset and panning
    if keys[pygame.K_r]:
        graph.zoom = 50
        graph.offset = [0, 0]

    # Pan the screen with the keyboard arrow keys
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        graph.offset[0] -= panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        graph.offset[0] += panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        graph.offset[1] += panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        graph.offset[1] -= panSpeed * deltatime.GetMultiplier() / graph.zoom

    # Zoom the screen with + or - keys
    if keys[pygame.K_KP_PLUS] or keys[pygame.K_EQUALS]:
        graph.zoom *= 1 + zoomSpeed
    if keys[pygame.K_KP_MINUS] or keys[pygame.K_MINUS]:
        graph.zoom /= 1 + zoomSpeed

    # Kill the program if escape is pressed
    if keys[pygame.K_ESCAPE]:
        Kill()

    # Panning the graph while mouse is pressed
    mouseClicked = pygame.mouse.get_pressed()
    mouseButtonDown = mouseClicked[0]

    if mouseClicked[0] and mouseStart == [-1, -1]:
        mouseStart = pygame.mouse.get_pos()
        graphMouseStart = [graph.offset[0], graph.offset[1]]

    if not mouseClicked[0] and mouseStart != [-1, -1]:
        mouseMoved = tuple(np.subtract(pygame.mouse.get_pos(), mouseStart))
        mouseStart = [-1, -1]
        graphMouseStart = [-1, -1]

    elif mouseClicked[0]:
        mouseMoved = tuple(np.subtract(pygame.mouse.get_pos(), mouseStart))

    if mouseStart != [-1, -1]:
        graph.offset = [graphMouseStart[0] - mouseMoved[0] / graph.zoom, 
                        graphMouseStart[1] + mouseMoved[1] / graph.zoom]

    # Zoom in and out with the scroll wheel
    for e in events:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 4:
                graph.zoom *= 1 + zoomSpeed
            elif e.button == 5:
                graph.zoom /= 1 + zoomSpeed

    # Mouse focus
    if pygame.mouse.get_focused():
        mouseFocusTime = 0.1
    else:
        mouseFocusTime -= deltatime.deltaTime

    graph.zoom = SigFig(graph.zoom, 6)




if __name__ == "__main__":
    ResetTimer()
    # Create pygame window and run the required initiation script
    pygame.init()
    clock = pygame.time.Clock()
    graphScreen = pygame.display.set_mode(screenSize, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    graphScreen.fill(colours["white"].colour)
    pygame.display.set_caption("Graphulator v4 - Screen View")
    
    #  ***** Instantiation of classes *****
    guiWindow = UserInterface(Kill)             # Create and initialise an instance of the UI class
    graph = Graph(screenSize)                   # Create and initialise an instance of the graph class
    graphUI = GraphUserInterface(screenSize)    # Create and initialise an instance of the graph UI class
    graphRenderer = GraphRenderer(graph)        # Create and initialise an instance of the graph renderer class
    functionManager = FunctionManager(graph)    # Create and initialise an instance of the function manager class

    # Starting equations


    for i in range(1, 2):
        functionManager.AddAnotherEquation(f"sin(2*x)*{i}")
    # functionManager.AddAnotherEquation("sin(2*x)")

    # print(GetTimeSince("Start code"))

    # Start main loop
    while running:
        mousePos = pygame.mouse.get_pos() if (mouseFocusTime > 0) else None 
        currentEquation = functionManager.currentEquations[0]


        # Frame update code
        graphRenderer.NewFrame()        
        graph.DrawBaseGraphSurface(graphRenderer, currentEquation, mousePos) 
        graphUI.UpdateUISurface(graph.fonts, graph, clock, mousePos, currentEquation) 

        if functionManager.CheckIfUpdatingThreads():
            functionManager.UpdateThreads(graph)

        functionManager.BlitCurrentSurfaces(graph, graphRenderer.surface)
        
        # print(GetTimeSince("Frame update"))

        # redraw the screen for that frame
        graphScreen.fill(colours["white"].colour)
        graphScreen.blit(graphRenderer.surface, (0, 0))
        graphScreen.blit(functionManager.surface, (0, 0))  
        graphScreen.blit(graphUI.surface, (0, 0)) 
        
        # print(GetTimeSince("Blit surface"))
        # update tkinter and pygame displays
        guiWindow.root.update()
        # print(GetTimeSince("Update tkinter screen"))

        pygame.display.update()
        # print(GetTimeSince("Update pygame screen"))
        
        
        # Wait for 60 FPS
        clock.tick(targetFPS)
        deltatime.Update()
        
        # print(GetTimeSince("Wait for 60 FPS"))

        # Get pygame events, execute input code and check for quitting / resizing
        events = pygame.event.get()
        PygameInput(events, graph)

        for e in events:
            if e.type == pygame.QUIT:     # When the window is closed
                Kill()
                break
            if e.type == pygame.VIDEORESIZE:    # Allow screen to be resized                
                screenSize = (max(e.w, minScreenSize[0]),
                              max(e.h, minScreenSize[1]))

                graphScreen = pygame.display.set_mode(screenSize,
                            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                graph.ScreenHasBeenResized(screenSize, graphRenderer)
                graphUI.ScreenHasBeenResized(screenSize)
                functionManager.ScreenHasBeenResized(screenSize)
                panSpeed = sorted([screenSize[0], screenSize[1]])[1] * 0.00125 + 1
                # the sorted()[1] expression finds the smallest of either the width or the height

        
        # print(GetTimeSince("Inputs"))
        
    # run this code on exit
    for equ in functionManager.myThreads:
        equ.terminate()

    print("Quitted")