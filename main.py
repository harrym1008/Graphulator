from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import tkinter as tk
import pygame
import numpy

import deltatime
from graph import *
from colours import *
from numstr import *
from graphui import GraphUserInterface
from drawfunc import PlottedEquation
from graphrenderer import GraphRenderer
from funcmgr import FunctionManager

# Screen starts at this resolution by default
screenSize = (400, 300)
minScreenSize = (256, 256)

running = True
targetFPS = 60

panSpeed = 2
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
    return not running


def PygameInput(events, graph):
    global mouseStart, mouseMoved, graphMouseStart, mouseFocusTime, mouseButtonDown

    keys = pygame.key.get_pressed()

    # Pan the screen with the keyboard arrow keys
    if keys[pygame.K_LEFT]:
        graph.offset[0] -= panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_RIGHT]:
        graph.offset[0] += panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_UP]:
        graph.offset[1] -= panSpeed * deltatime.GetMultiplier() / graph.zoom
    if keys[pygame.K_DOWN]:
        graph.offset[1] += panSpeed * deltatime.GetMultiplier() / graph.zoom

    # Zoom the screen with + or - keys
    if keys[pygame.K_KP_PLUS] or keys[pygame.K_EQUALS]:
        graph.zoom *= 1 + zoomSpeed
    if keys[pygame.K_KP_MINUS] or keys[pygame.K_MINUS]:
        graph.zoom /= 1 + zoomSpeed

    # Reset offset and panning
    if keys[pygame.K_r]:
        graph.zoom = 10
        graph.offset = [0, 0]

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
        mouseMoved = tuple(numpy.subtract(pygame.mouse.get_pos(), mouseStart))
        mouseStart = [-1, -1]
        graphMouseStart = [-1, -1]

    elif mouseClicked[0]:
        mouseMoved = tuple(numpy.subtract(pygame.mouse.get_pos(), mouseStart))

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
        mouseFocusTime = 0.1
    else:
        mouseFocusTime -= deltatime.deltaTime

    graph.zoom = SigFig(graph.zoom, 6)



if __name__ == "__main__":
    # Create tkinter window
    guiScreen = tk.Tk()
    guiScreen.title("Graphulator v4")
    guiScreen.protocol("WM_DELETE_WINDOW", Kill)   
    # This makes it run the Kill method when the X button is pressed in the top right of the window

    # Create pygame window and run the required initiation script
    pygame.init()
    clock = pygame.time.Clock()
    graphScreen = pygame.display.set_mode(screenSize, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    graphScreen.fill(colours["white"].colour)
    pygame.display.set_caption("Graphulator v4 - Screen View")

    AssignFonts()       # Assigning fonts at the start - this takes lots of processing time, so it is done at the beginning
    graph = Graph(screenSize)     # Create and initialise an instance of the graph class
    graphUI = GraphUserInterface(screenSize)    # Create and initialise an instance of the graph UI class
    graphRenderer = GraphRenderer(graph)
    functionManager = FunctionManager(graph)

    functionManager.AddAnotherEquation("(3*x+7)*(x-5)")
    functionManager.AddAnotherEquation("x**3-4*x**2-35*x+20")


    # Start main loop
    while running:
        # Frame update code
        mousePos = pygame.mouse.get_pos() if (mouseFocusTime > 0 and not mouseButtonDown) else None

        graphRenderer.NewFrame()
        functionManager.UpdateThreads(graph)
        functionManager.BlitCurrentSurfaces(graph)
        graph.DrawBaseGraphSurface(graphRenderer) 
        graphUI.UpdateUISurface(graph.GetMainFont(), graph, clock, mousePos) 

        # redraw the screen for that frame
        graphScreen.fill(colours["white"].colour)
        graphScreen.blit(graphRenderer.surface, (0, 0))
        graphScreen.blit(functionManager.surface, (0, 0))  
        graphScreen.blit(graphUI.surface, (0, 0))      

        # update tkinter and pygame displays
        guiScreen.update()
        pygame.display.flip()
        
        # Wait for 60 FPS
        clock.tick(targetFPS)
        deltatime.Update()

        # Get pygame events, execute input code and check for quitting / resizing
        events = pygame.event.get()
        PygameInput(events, graph)

        for e in events:
            if e.type == pygame.QUIT:
                if Kill():
                    break
            if e.type == pygame.VIDEORESIZE:
                screenSize = (max(e.w, minScreenSize[0]),
                              max(e.h, minScreenSize[1]))

                graphScreen = pygame.display.set_mode(screenSize,
                            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                graph.ScreenHasBeenResized(screenSize, graphRenderer)
                graphUI.ScreenHasBeenResized(screenSize)
                functionManager.ScreenHasBeenResized(screenSize)
                panSpeed = sorted([screenSize[0], screenSize[1]])[1] * 0.00125 + 1
                # the sorted()[1] expression finds the smallest of either the width or the height

    # run this code on exit
    for equ in functionManager.myThreads:
        equ.terminate()

