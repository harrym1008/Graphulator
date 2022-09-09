import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import tkinter as tk

import pygame
import numpy

import deltatime
from graph import *
from graph_ui import *
from colours import *
from numstr import *
from drawfunc import *

# Screen starts at this resolution by default
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
    # Sets global variable running to false, resulting in the closure of the program
    global running

    running = False
    return not running


def PygameInput(events, graph):
    global mouseStart, mouseMoved, graphMouseStart, mouseFocusTime

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
    guiScreen.title("Graphulator v3")
    guiScreen.protocol("WM_DELETE_WINDOW", Kill)   
    # This makes it run the Kill method when the X button is pressed in the top right of the window

    # Create pygame window and run the required initiation script
    pygame.init()
    clock = pygame.time.Clock()
    graphScreen = pygame.display.set_mode(screenSize, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    graphScreen.fill(colours["white"].colour)

    AssignFonts()       # Assigning fonts at the start - this takes lots of processing time, so it is done at the beginning
    graph = Graph(screenSize)     # Create and initialise an instance of the graph class
    graphUI = GraphUserInterface(screenSize)    # Create and initialise an instance of the graph UI class
    functionHolder = FunctionHolder()      # Create and initialise an instance of the function holder class
    functionHolder.AppendEquation(graph, "math.sin(x)", colours["red"].colour)


    # Start main loop
    while running:
        # Create surface for the graph
        graph.DrawBaseGraphSurface() 

        # Check if mouse is on the graph
        mousePos = pygame.mouse.get_pos() if mouseFocusTime > 0 else None
        graphUI.UpdateUISurface(graph.GetMainFont(), graph, clock, mousePos) 

        # redraw the screen for that frame
        graphScreen.fill(colours["white"].colour)
        graphScreen.blit(graph.baseSurface, (0, 0))
        graphScreen.blit(graphUI.surface, (0, 0))

        # blit all surfaces to the screen
        # functionHolder.UpdateEquations(graph)
        

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
                graphScreen = pygame.display.set_mode((e.w, e.h),
                                                      pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                screenSize = (e.w, e.h)
                graph.ScreenHasBeenResized(screenSize)
                graphUI.UpdateScreenSize(screenSize)
                panSpeed = sorted([e.w, e.h])[1] * 0.00125 + 1
                # the sorted()[1] expression finds the smallest of either the width or the height

                

