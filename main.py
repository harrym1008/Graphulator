import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
# Prevents the welcome message from pygame from spamming in the terminal

# External modules
import pygame

# Internal modules
import getjson
from colours import *
from numstr import *
from deltatime import DeltaTime
from graph import Graph
from graphui import GraphUserInterface
from graphrender import GraphRenderer
from funcmgr import FunctionManager
from ui import UserInterface
from uimath import *

# Set a constant for the minimum screen size
MIN_SCREEN_SIZE = (192, 192)


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


    def ApplyMouseMovement(self, graph, events, zoomSpeed):
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
    def UpdateMouseFocus(self, dt):
        focused = pygame.mouse.get_focused()
        
        if focused:
            self.focusTime = 0.1
        else:
            self.focusTime -= dt.deltatime

    def GetMousePos(self):
        if self.focusTime > 0:
            return self.mousePosition
        return None        
            


# Define the main class where the mainloop runs
class Graphulator:
    def __init__(self):
        # Predefined values are defined
        self.running = True
        self.currentEquationNumber = 0
        self.mousePos = (0, 0)

        # Load some data from the JSON file
        self.targetFPS = getjson.GetData("max_fps")
        self.screenSize = tuple(getjson.GetData("screen_size"))
        self.maxEquations = min(getjson.GetData("max_equations"), 10)  # make sure maximum is 10

        # Get default speeds from JSON file and calculate pan speed
        self.basePanSpeed = getjson.GetData("base_pan_speed")
        self.panSpeed = self.screenSize[0] * 0.0005 * self.basePanSpeed + 1
        self.zoomSpeed = getjson.GetData("base_zoom_speed")

        # Define pygame clock and the main screen
        self.clock = pygame.time.Clock()
        self.graphScreen = pygame.display.set_mode(self.screenSize, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption(f"Graphulator Screen View")

        # Create an instance of all the main classes
        self.graph = Graph(self.screenSize)
        self.graphUI = GraphUserInterface(self.graph)
        self.graphRenderer = GraphRenderer(self.graph)
        self.gui = UserInterface(self)
        self.functionManager = FunctionManager(self.graph, self.maxEquations)

        # Additional smaller classes which handle small areas of the program
        self.mouse = MouseData()
        self.deltatime = DeltaTime()

        # Set the program to show a sine wave be default
        self.gui.entries[0].set("sin x")

        
    # Stops mainloop() from looping
    def Kill(self):
        self.running = False


    # Update the constants in the static class UIMath
    def UpdateConstants(self):
        self.gui.ResetConstants()
        constants = self.gui.GetConstants()

        self.functionManager.SetConstants(constants)
        UIMath.DefineConstants(constants)


    # Handles Pygame events: quitting and resizing the screen
    def HandleEvents(self, events):
        for e in events:
            # When the cross button is pressed on the window
            if e.type == pygame.QUIT:
                self.Kill()

            # When the window is resized
            elif e.type == pygame.VIDEORESIZE:
                self.screenSize = ( max(e.w, MIN_SCREEN_SIZE[0]),
                                    max(e.h, MIN_SCREEN_SIZE[1]))
                self.graphScreen = pygame.display.set_mode(self.screenSize, 
                            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                
                self.graph.ScreenHasBeenResized(self.screenSize)
                self.graphRenderer.ScreenHasBeenResized(self.screenSize)
                self.graphUI.ScreenHasBeenResized(self.screenSize)
                self.functionManager.ScreenHasBeenResized(self.screenSize)
                
                smallestDimension = min(self.screenSize[0], self.screenSize[1])
                self.panSpeed = smallestDimension * 0.0005 * self.basePanSpeed + 1
                # Change pan speed to align with the new screen dimensions


    # Method which executes all necessary input functions 
    def HandleInput(self, keys, events):
        self.mouse.ApplyMouseMovement(self.graph, events, self.zoomSpeed)
        self.mouse.UpdateMouseFocus(self.deltatime)
        self.mousePos = self.mouse.GetMousePos()

        self.KeyboardInput(keys)    
        self.GetCurrentEquationInput(keys)   
        

    # Reset procedure 
    def ResetButtonPressed(self):
        self.graph.zoom = 50
        self.graph.offset = [0, 0]
        self.graphUI.highlightedPoints.clear()


    # Run the main keyboard input functions
    def KeyboardInput(self, keys):
        # Reset offset and panning if R is pressed
        if keys[pygame.K_r]:
            self.ResetButtonPressed()

        # Pan the screen with the keyboard arrow keys
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.graph.offset[0] -= self.panSpeed * self.deltatime.multiplier / self.graph.zoom
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.graph.offset[0] += self.panSpeed * self.deltatime.multiplier / self.graph.zoom
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.graph.offset[1] += self.panSpeed * self.deltatime.multiplier / self.graph.zoom
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.graph.offset[1] -= self.panSpeed * self.deltatime.multiplier / self.graph.zoom

        # Zoom the screen with + or - keys
        if keys[pygame.K_KP_PLUS] or keys[pygame.K_EQUALS]:
            self.graph.zoom *= 1 + self.zoomSpeed
        if keys[pygame.K_KP_MINUS] or keys[pygame.K_MINUS]:
            self.graph.zoom /= 1 + self.zoomSpeed

        # Kill the program if escape is pressed
        if keys[pygame.K_ESCAPE]:
            self.Kill()


    # Loops through the key buttons, check which one is pressed
    # This changes the current selected equation
    def GetCurrentEquationInput(self, keys):
        for i, nums in enumerate(numberKeys):
            if keys[nums[0]] or keys[nums[1]]:
                if i < self.maxEquations:
                    self.currentEquationNumber = i


    # Blit all of the rendered surfaces onto the actual pygame window
    def RenderNewFrame(self):
        self.graphScreen.fill(colours["white"].colour)
        self.graphScreen.blit(self.graphRenderer.surface, (0, 0))
        self.graphScreen.blit(self.functionManager.surface, (0, 0))  
        self.graphScreen.blit(self.graphUI.surface, (0, 0)) 



    def MainLoop(self):
        # Loop until the program stops
        while self.running:
            # Get pygame events and keys pressed
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            # Input handling and constants are updated
            self.HandleInput(keys, events)
            self.UpdateConstants()

            currentEquation = self.functionManager.currentEquations[self.currentEquationNumber]
            equList = self.gui.GetListOfEquations()[:self.maxEquations]
            self.functionManager.UpdateEquations(equList)
            self.gui.UpdateEquationNumberLabels(equList)

            self.graphRenderer.NewFrame()
            self.graph.DrawBaseGraphSurface(self.graphRenderer, self.mousePos)
            self.graphUI.UpdateUISurface(self, currentEquation)
            
            self.functionManager.UpdateThreads(self.graph)
            self.functionManager.BlitCurrentSurfaces(self.graph)

            # Run each frames update function
            self.RenderNewFrame()
            pygame.display.update()
            self.gui.root.update()

            self.HandleEvents(events)

            # Wait for the next frame
            self.clock.tick(self.targetFPS)
            self.deltatime.Update()
            pygame.display.set_caption(f"Graphulator Screen View - {round(self.clock.get_fps(), 2)} FPS")


        # Kill all running threads
        for equData in self.functionManager.equationsData:
            equData.thread.terminate()
            



if __name__ == "__main__":
    # Run the required initiation script for pygame
    pygame.init()

    # Create an instance of the main class then run the main loop
    graphulator = Graphulator()
    graphulator.MainLoop()

    quit()