import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
# Prevents the welcome message from pygame from spamming in the terminal

# External modules
import pygame
import numpy as np
from multiprocessing import cpu_count

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
minScreenSize = (192, 192)

running = True
targetFPS = 60
maxEquations = 2 if cpu_count() == 2 else 10

panSpeed = 2.5
zoomSpeed = 0.05
graphMouseStart = [-1, -1]
mouseStart = [-1, -1]
mouseMoved = (0, 0)
mouseFocusTime = 0
mouseButtonDown = False

numberKeys = [[pygame.K_1, pygame.K_KP_1],
              [pygame.K_2, pygame.K_KP_2],
              [pygame.K_3, pygame.K_KP_3],
              [pygame.K_4, pygame.K_KP_4],
              [pygame.K_5, pygame.K_KP_5],
              [pygame.K_6, pygame.K_KP_6],
              [pygame.K_7, pygame.K_KP_7],
              [pygame.K_8, pygame.K_KP_8],
              [pygame.K_9, pygame.K_KP_9],
              [pygame.K_0, pygame.K_KP_0]]


def Kill():
    # Sets global variable running to false, resulting in the closure of the program
    global running
    running = False


def PygameInput(events, keys, graph):
    global mouseStart, mouseMoved, graphMouseStart, mouseFocusTime, mouseButtonDown

    # Reset offset and panning
    if keys[pygame.K_r]:
        graph.zoom = 50
        graph.offset = [0, 0]
        graphUI.highlightedPoints.clear()

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
    focused = pygame.mouse.get_focused()
    if focused:
        mouseFocusTime = 0.1
    else:
        mouseFocusTime -= deltatime.deltaTime

    graph.zoom = SigFig(graph.zoom, 6)


def CurrentEquationInput(keys, currentEquationIndex):
    for i, nums in enumerate(numberKeys):
        if keys[nums[0]] or keys[nums[1]]:
            if i < maxEquations:
                return i
    return currentEquationIndex





if __name__ == "__main__":
    # Create pygame window and run the required initiation script
    pygame.init()
    clock = pygame.time.Clock()
    graphScreen = pygame.display.set_mode(screenSize, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    pygame.display.set_caption(f"Graphulator Screen View")
    
    #  ***** Instantiation of classes *****
    graph = Graph(screenSize)                   # Create and initialise an instance of the graph class
    graphUI = GraphUserInterface(graph)         # Create and initialise an instance of the graph UI class
    gui = UserInterface(graph, graphUI, Kill)   # Create and initialise an instance of the UI class
    graphRenderer = GraphRenderer(graph)        # Create and initialise an instance of the graph renderer class
    functionManager = FunctionManager(graph)    # Create and initialise an instance of the function manager class

    currentEquationIndex = 0

    # Starting equations
    for i in range(maxEquations):
        functionManager.AddAnotherEquation("")
    gui.entries[0].set("x=2y")
    gui.entries[1].set("2x=y")


    # Start main loop
    while running:     
        # Get pygame events and pressed keys
        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        # Execute input code
        PygameInput(events, keys, graph)
        currentEquationIndex = CurrentEquationInput(keys, currentEquationIndex)

        # Get data ready for next frames calculation
        mousePos = pygame.mouse.get_pos() if (mouseFocusTime > 0) else None 
        currentEquation = functionManager.currentEquations[currentEquationIndex]

        # Update constants
        gui.ResetConstants()
        constants = gui.GetConstants()
        functionManager.SetConstants(constants)

        # Get latest list of equations        
        equList = gui.GetListOfEquations()[:maxEquations]
        # Run replacement function on every equation in the list
        equList = [evaluate.ReplaceEquation(equ) if equ != "" else "" for equ in equList]
        functionManager.UpdateEquations(equList)

        # Frame update code
        graphRenderer.NewFrame()
        graph.DrawBaseGraphSurface(graphRenderer, currentEquation, mousePos) 
        graphUI.UpdateUISurface(graph, mousePos, currentEquation) 
        functionManager.UpdateThreads(graph)
        functionManager.BlitCurrentSurfaces(graph)
        
        # redraw the screen for that frame
        graphScreen.fill(colours["white"].colour)
        graphScreen.blit(graphRenderer.surface, (0, 0))
        graphScreen.blit(functionManager.surface, (0, 0))  
        graphScreen.blit(graphUI.surface, (0, 0)) 
        
        # update tkinter and pygame displays
        gui.root.update()
        pygame.display.update()        
        
        # Wait for 60 FPS
        clock.tick(targetFPS)
        deltatime.Update()
        pygame.display.set_caption(f"Graphulator Screen View - {round(clock.get_fps(), 2)} FPS")

        # Check for quitting / resizing
        for e in events:
            if e.type == pygame.QUIT:     # When the window is closed
                Kill()
                break
            if e.type == pygame.VIDEORESIZE:    # Executed when the pygame window is resized     
                screenSize = (max(e.w, minScreenSize[0]),
                              max(e.h, minScreenSize[1]))

                graphScreen = pygame.display.set_mode(screenSize,
                            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                graph.ScreenHasBeenResized(screenSize)
                graphRenderer.ScreenHasBeenResized(screenSize)
                graphUI.ScreenHasBeenResized(screenSize)
                functionManager.ScreenHasBeenResized(screenSize)
                panSpeed = sorted([screenSize[0], screenSize[1]])[1] * 0.00125 + 1
                # the sorted()[1] expression finds the smallest of either the width or the height


    # run this code on exit
    for equ in functionManager.myThreads:
        equ.terminate()

    print("Quitted")