# Prevents the welcome message from pygame from spamming in the terminal
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# Suppresses "RuntimeWarning" messages, these are not exceptions that crash the program
# They are just warnings that arise for example when an invalid operation is applied to a number
# This is fine because my program accounts for such invalid operations that will return erroneous values
# This code is here to prevent the message from being spammed in the terminal
import warnings
warnings.filterwarnings("ignore")

# External modules
import pygame

# Internal modules
import deltatime
import getjson
from colours import *
from numstr import *
from timer import *
from graph import Graph
from graphui import GraphUserInterface
from graphrender import GraphRenderer
from funcmgr import FunctionManager
from ui import UserInterface
from uimath import *

# Screen starts at this resolution by default
screenSize = tuple(getjson.GetData("screen_size"))
minScreenSize = (192, 192)

running = True
targetFPS = getjson.GetData("max_fps")
maxEquations = min(getjson.GetData("max_equations"), 10)  # make sure maximum is 10

basePanSpeed = getjson.GetData("base_pan_speed")
zoomSpeed = getjson.GetData("base_zoom_speed")
panSpeed = screenSize[0] * 0.0005 * basePanSpeed + 1     
# predefined equation to calculate what pan speed will be

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
# This array references both of the possible number keys 
# for the numpad and the top row of the keyboard


def Kill():
    # Sets global variable running to false, resulting in the closure of the program
    global running
    running = False


# This class performs all the necessary input actions for the mouse
class MouseData:
    BLANK = (-1, -1)

    def __init__(self):
        self.mousePosition = (0, 0)
        self.startPosition = self.BLANK
        self.graphPosition = self.BLANK
        self.focusTime = 0
        self.buttonDown = False


    # Subtracts two tuples which contain coordinates
    @staticmethod
    def MousePositionSubtraction(val1, val2):
        return (val1[0] - val2[0], val1[1] - val2[1])


    def ApplyMouseMovement(self, graph, events):
        # Check if button is down and get mouse position
        self.buttonDown = pygame.mouse.get_pressed()[0]   # left click only
        self.mousePosition = pygame.mouse.get_pos()
        # this returns the pixel position of the mouse where the origin is the top left of the window             

        # Zoom in and out with the scroll wheel
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 4:
                    graph.zoom *= 1 + zoomSpeed
                elif e.button == 5:
                    graph.zoom /= 1 + zoomSpeed

        # Main mouse click and drag functionality
        mouseMoved = (0, 0)

        # When the mouse has just been pressed
        if self.buttonDown and self.startPosition == self.BLANK:
            self.startPosition = self.mousePosition
            self.graphPosition = (graph.offset[0], graph.offset[1])

        # When the mouse has just stopped being pressed
        elif not self.buttonDown and self.mousePosition != self.BLANK:
            mouseMoved = MouseData.MousePositionSubtraction(self.mousePosition, self.startPosition)
            self.startPosition = self.BLANK
            self.graphPosition = self.BLANK

        # While the mouse is being pressed
        elif self.buttonDown:
            mouseMoved = MouseData.MousePositionSubtraction(self.mousePosition, self.startPosition)

        # Update the graph offset accordingly
        if self.startPosition != self.BLANK:
            graph.offset = [self.graphPosition[0] - mouseMoved[0] / graph.zoom,
                            self.graphPosition[1] + mouseMoved[1] / graph.zoom]   


    # Check if the mouse is on the window or not
    def UpdateMouseFocus(self):
        focused = pygame.mouse.get_focused()
        
        if focused:
            self.focusTime = 0.1
        else:
            self.focusTime -= deltatime.deltaTime

    def GetMousePos(self):
        if self.focusTime > 0:
            return self.mousePosition
        return None        
            


        

def KeyboardInput(keys, graph):
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


# Loops through the key buttons, check which one is pressed
def GetCurrentEquationInput(keys, currentEquationIndex):
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
    
    #  ***** Instantiation of main classes *****
    graph = Graph(screenSize)                               # Create and initialise an instance of the graph class
    graphUI = GraphUserInterface(graph)                     # Create and initialise an instance of the graph UI class
    gui = UserInterface(graph, graphUI, Kill)               # Create and initialise an instance of the UI class
    graphRenderer = GraphRenderer(graph)                    # Create and initialise an instance of the graph renderer class
    functionManager = FunctionManager(graph, maxEquations)  # Create and initialise an instance of the function manager class

    # Defines a variable that holds the index of the currently selected equation
    currentEquationIndex = 0
    mouse = MouseData()

    # Create equation instances and set the first as the default equation "y=sin x"
    for i in range(maxEquations):
        functionManager.AddEquation("")
    gui.entries[0].set("sin x")



    # Start main loop
    while running:     
        ResetTimer()

        # Get pygame events and pressed keys
        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        # Execute input code for the mouse
        mouse.ApplyMouseMovement(graph, events)
        mouse.UpdateMouseFocus()
        mousePos = mouse.GetMousePos()

        # Execute keyboard input code
        KeyboardInput(keys, graph)
        currentEquationIndex = GetCurrentEquationInput(keys, currentEquationIndex)

        # Get data ready for next frames calculation
        currentEquation = functionManager.currentEquations[currentEquationIndex]

        # Update constants
        gui.ResetConstants()
        constants = gui.GetConstants()
        functionManager.SetConstants(constants)
        UIMath.DefineConstants(constants)

        # Get latest list of equations        
        equList = gui.GetListOfEquations()[:maxEquations]
        functionManager.UpdateEquations(equList)

        # Frame update code
        gui.UpdateEquationNumberLabels(equList)
        graphRenderer.NewFrame()
        graph.DrawBaseGraphSurface(graphRenderer, mouse.GetMousePos()) 
        graphUI.UpdateUISurface(graph, mousePos, currentEquation, functionManager) 
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

                # Change the pan speed to coincide with the screen size
                smallestDimension = screenSize[0] if screenSize[0] < screenSize[1] else screenSize[1]
                panSpeed = smallestDimension * 0.0005 * basePanSpeed + 1
                

        # Wait for 60 FPS
        clock.tick(targetFPS)
        deltatime.Update()

        pygame.display.set_caption(f"Graphulator Screen View - {round(clock.get_fps(), 2)} FPS")


    # kill all running processes
    for equ in functionManager.myThreads:
        equ.terminate()

    # Program will now quit