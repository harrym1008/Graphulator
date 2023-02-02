from multiprocessing import Process, Queue
from typing import List
from colours import *
from numstr import SigFig
from graph import GraphBounds

import getjson
import pygame
import drawfunc


# The class that holds equations and handles multiprocessing
class FunctionManager:
    def __init__(self, graph, maxEquations):
        self.currentEquations: List[drawfunc.PlottedEquation] = []
        self.equationsData: List[EquationData] = []
        
        self.nextToUpdate = 0
        self.maxEquations = maxEquations
        self.updatesPerFrame = getjson.GetData("graph_updates_per_frame")

        if self.updatesPerFrame > self.maxEquations:
            self.updatesPerFrame = self.maxEquations
        elif self.updatesPerFrame < 1:
            self.updatesPerFrame = 1
        
        self.surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)
        self.constants = (0, 0, 0, -10, 10)

        # This will only be shown while the program is waiting for the threads to start
        # This is usually unnoticeable but on slow computers it is there
        # to show the user that the program has not crashed.
        self.waitingForThread = self.CreateWaitingForThreadSurface(graph)      

        # Append the correct amount of equations
        for i in range(maxEquations):
            self.AddEquation("")  


    
    # Run this subroutine when the window is resized
    def ScreenHasBeenResized(self, newSize):
        self.surface = pygame.Surface(newSize, pygame.SRCALPHA)


    # Add another equation by appending a plotted equation and equation data
    def AddEquation(self, equation):
        index = len(self.currentEquations)
        newEquation = drawfunc.PlottedEquation(equation, index)
        newEquationData = EquationData()

        self.currentEquations.append(newEquation)
        self.equationsData.append(newEquationData)


    # Sets the constants in the class.
    # If they have changed, it sends an event to all of the threads with the new constants.
    def SetConstants(self, constants):
        if constants == self.constants:
            return
        self.constants = constants

        for equData in self.equationsData:
            equData.eventQueue.put(Event(1, constants))
            
            
    def GetConstants(self):
        return self.constants





    def UpdateEquations(self, array):
        for i in range(len(array)):
            if array[i] != self.currentEquations[i].equation:
                self.currentEquations[i].ChangeMyEquation(array[i])


    # Determine which threads to update given the data from the JSON file
    def UpdateThreads(self, graph):
        if self.updatesPerFrame == self.maxEquations:
            for i in range(self.maxEquations):
                self.UpdateSingleThread(graph, i)

        elif self.updatesPerFrame == 1:
            self.UpdateSingleThread(graph, self.nextToUpdate)
            self.nextToUpdate = (self.nextToUpdate + 1) % self.maxEquations

        else:
            threadsToUpdate = []
            for i in range(self.updatesPerFrame):
                threadsToUpdate.append(self.nextToUpdate)
                self.nextToUpdate = (self.nextToUpdate + 1) % self.maxEquations
                
            for i in threadsToUpdate:
                self.UpdateSingleThread(graph, i)



    # Update one threads data through the use of the 2-queue system
    def UpdateSingleThread(self, graph, i):
        equ = self.currentEquations[i]
        equData = self.equationsData[i]

        # if a thread should be running but is not (because it has just finished or 
        # the class has just been instantiated)

        threadIsNone = equData.thread is None
        newDataIsAvailable = self.QueueHasItem(equData.outQueue)

        bounds = GraphBounds(graph)              
        threadData = drawfunc.ThreadInput(bounds, graph.zoomedOffset, equ)

        if newDataIsAvailable and not threadIsNone:  
            data: drawfunc.ThreadOutput = equData.outQueue.get()         # get data from return queue
            
            equData.surfaceAndBounds = drawfunc.SurfaceAndBounds(data.serialisedSurface.GetSurface(), data.bounds)
            self.currentEquations[i].solutions = data.solutions
            
            # Put new events into the event queue
            for event in self.GetEventData(i):
                equData.eventQueue.put(event)

            equData.inQueue.put(threadData)         
            # save the drawn surface to the array, so it does not have to be redrawn every frame

        elif threadIsNone:
            print("Created the new thread")
            equData.thread = Process(target=equ.RecalculatePoints, 
                                     args=(threadData, equData.inQueue, equData.outQueue, equData.eventQueue))
            equData.thread.start()
            equData.inQueue.put(threadData)



    # Places an event in the event queue, holding the changed equation's string
    def GetEventData(self, index):
        return [Event(0, self.currentEquations[index].equation)]


    # Calculate the correct position to render the surface at, then blit it.
    def BlitCurrentSurfaces(self, graph):
        waitingMessage = False
        self.surface.fill(colours["transparent"].colour)

        surfaceBoundsData = [equData.surfaceAndBounds for equData in self.equationsData]

        for i, data in enumerate(surfaceBoundsData):
            if self.currentEquations[i].equation == "" or data is None:

                # Check if waiting for thread is going to being rendered or not
                if data is None and not waitingMessage and self.currentEquations[i].equation != "":
                    self.surface.blit(self.waitingForThread, (0, 0))
                    waitingMessage = True
                continue

            dataSurface = data.surface

            ss = data.bounds.screenSize
            sc = tuple([i // 2 for i in ss])

            # equation for value: p = -oz + 0.5s + vz
            # p = position
            # o = offset
            # z = zoom
            # s = half of the screen size (the screen centre)
            # v = input value

            surfaceCorners = [(
                -graph.zoomedOffset[0] + sc[0] + data.bounds.NW[0] * graph.zoom, 
                graph.zoomedOffset[1] + sc[1] - data.bounds.NW[1] * graph.zoom
                ),(
                -graph.zoomedOffset[0] + sc[0] + data.bounds.SE[0] * graph.zoom, 
                graph.zoomedOffset[1] + sc[1] - data.bounds.SE[1] * graph.zoom
                )]

            newScale = graph.screenSize
            newPosition = (0, 0)

            # check if the graph has been panned or zoomed and store if they have into booleans
            zoomed = data.zoom != graph.zoom
            panned = SigFig(data.bounds.CENTRE[0], 6) != SigFig(graph.bounds.CENTRE[0], 6) or \
                     SigFig(data.bounds.CENTRE[1], 6) != SigFig(graph.bounds.CENTRE[1], 6)
            # 6 is the amount of significant figures to round to, 
            # this allows enough precision for the floating-point value
            

            if panned or zoomed:
                newScale = (surfaceCorners[1][0] - surfaceCorners[0][0],
                            surfaceCorners[1][1] - surfaceCorners[0][1])
                newScale = tuple(int(abs(i)) for i in newScale)

                newPosition = (int(surfaceCorners[0][0]), int(surfaceCorners[0][1])) 


            try:
                scaleX = ss[0] / newScale[0]
                scaleY = ss[1] / newScale[1]
            except ZeroDivisionError:      # In case something goes wrong
                scaleX = 0.25
                scaleY = 0.25

            # Check if scaling should happen
            skipDueToSize = scaleX <= 0.25 or scaleY <= 0.25

            if skipDueToSize:           # Clear the surface, scaling will take too much time, wait an updated surface
                newPosition = (0, 0)
                newScale = ss
                tempSurface = pygame.Surface(newScale, pygame.SRCALPHA)
                
            elif newScale != graph.screenSize:      # Scale to correct dimensions
                tempSurface = pygame.transform.scale(dataSurface, newScale)
            else:
                tempSurface = data.surface   # Scaling not necessary

            self.surface.blit(tempSurface, newPosition)


    # Create the please wait for threads message surface while the threads are starting
    def CreateWaitingForThreadSurface(self, graph):
        s = pygame.Surface(graph.screenSize, pygame.SRCALPHA)

        msg = "Please wait: threads are starting"

        s.fill(colours["transparent"].colour)
        txtWhite = graph.fonts[36].render(msg, True, colours["white"].colour)
        txtBlack = graph.fonts[36].render(msg, True, colours["black"].colour)

        for offset in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            renderAt = (graph.screenSize[0] // 2 - txtBlack.get_width() // 2 + offset[0],
                        graph.screenSize[1] // 2 - txtBlack.get_height() // 2 + offset[1])
            s.blit(txtBlack, renderAt)
        renderAt = (graph.screenSize[0] // 2 - txtWhite.get_width() // 2,
                    graph.screenSize[1] // 2 - txtWhite.get_height() // 2)
        s.blit(txtWhite, renderAt)

        return s


    # Returns True if the queue is not empty, i.e. it has any value in it
    @staticmethod
    def QueueHasItem(queue):
        return queue.qsize() > 0




# Small class which holds data for each equation
class EquationData:
    def __init__(self):
        self.inQueue = Queue()
        self.outQueue = Queue()
        self.eventQueue = Queue()
        self.surfaceAndBounds: drawfunc.SurfaceAndBounds = None
        self.thread: Process = None


# Class that passes event data into the subprocess
class Event:
    def __init__(self, type, data) -> None:
        self.type = type
        self.data = data

    def __str__(self):
        return f"'{self.type}' --> '{self.data}'"

