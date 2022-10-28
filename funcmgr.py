from multiprocessing import Process, Queue, cpu_count
from typing import List
from colours import *
from timer import *
from numstr import SigFig

import numpy as np
import pygame
import deltatime
import drawfunc
import time


UPDATE_HERTZ = 16
UPDATE_TIME = 1 / UPDATE_HERTZ if UPDATE_HERTZ > 0 else 0


class FunctionManager:
    def __init__(self, graph):
        self.currentEquations: List[drawfunc.PlottedEquation] = []
        self.surfaceBoundsData: List[drawfunc.SurfaceAndBounds] = []
        self.myThreads = []
        self.myInQueues = []
        self.myOutQueues = []
        self.myEventQueues = []
        
        self.surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)

        self.timeToNextUpdate = UPDATE_TIME



    def ScreenHasBeenResized(self, newSize):
        self.surface = pygame.Surface(newSize, pygame.SRCALPHA)



    def AddAnotherEquation(self, equation):
        index = len(self.currentEquations)

        newEquation = drawfunc.PlottedEquation(equation, index)
        self.currentEquations.append(newEquation)

        self.surfaceBoundsData.append(None)
        self.myThreads.append(None)
        self.myInQueues.append(Queue())
        self.myOutQueues.append(Queue())
        self.myEventQueues.append(Queue())



    def CheckIfUpdatingThreads(self):
        self.timeToNextUpdate -= deltatime.deltaTime

        if self.timeToNextUpdate < -1:
            self.timeToNextUpdate = UPDATE_TIME
            return True
        elif self.timeToNextUpdate < 0:
            self.timeToNextUpdate += UPDATE_TIME
            return True
        return False



    def UpdateEquations(self, array):
        for i in range(len(array)):
            if array[i] != self.currentEquations[i].equation:
                self.currentEquations[i].ChangeMyEquation(array[i])




    def UpdateThreads(self, graph):
        for i, equ in enumerate(self.currentEquations):
            # check if a thread should not be running, if so end it
            if not equ.active:
                self.myThreads[i].terminate()
                continue

            # if a thread should be running but is not (because it has just finished or 
            # the class has just been instantiated)

            threadIsNotNone = self.myThreads[i] is not None
            newDataIsAvailable = self.myOutQueues[i].qsize() > 0

            # print(self.myOutQueues[i].qsize())

            if equ.active and newDataIsAvailable if threadIsNotNone else True:
                threadData = drawfunc.ThreadInput(graph.bounds, graph.screenSize, graph.zoomedOffset, equ)

                if self.myThreads[i] is None:
                    print("Created the new thread")
                    self.myThreads[i] = Process(target=equ.RecalculatePoints, 
                                          args=(threadData, self.myInQueues[i], self.myOutQueues[i], self.myEventQueues[i]))
                    self.myThreads[i].start()
                    self.myInQueues[i].put(threadData)
                    continue

                data: drawfunc.ThreadOutput = self.myOutQueues[i].get()         # get data from return queue

                self.surfaceBoundsData[i] = drawfunc.SurfaceAndBounds(data.serialisedSurface.GetSurface(), data.bounds)
                
                # Put new events
                for event in self.GetEventData(i):
                    self.myEventQueues[i].put(event)

                self.myInQueues[i].put(threadData)                
                # save the drawn surface to the array, so it does not have to be redrawn every frame



    def GetEventData(self, index):
        return [Event(0, self.currentEquations[index].equation)]



    def BlitCurrentSurfaces(self, graph, surface):
        startTime = time.perf_counter()
        self.surface.fill(colours["transparent"].colour)

        for i, data in enumerate(self.surfaceBoundsData):
            if self.currentEquations[i].equation == "" or data is None:
                continue

            dataSurface = data.surface

            # equation for value: p = -oz + 0.5s + vz
            # p = position
            # o = offset
            # z = zoom
            # s = half of the screen size (the screen centre)
            # v = input value

            surfaceCorners = [(
                -graph.zoomedOffset[0] + graph.screenCentre[0] + data.bounds.NW[0] * graph.zoom, 
                graph.zoomedOffset[1] + graph.screenCentre[1] - data.bounds.NW[1] * graph.zoom
                ),(
                -graph.zoomedOffset[0] + graph.screenCentre[0] + data.bounds.SE[0] * graph.zoom, 
                graph.zoomedOffset[1] + graph.screenCentre[1] - data.bounds.SE[1] * graph.zoom
                )]

            pygame.draw.circle(surface, colours["yellow"].colour, surfaceCorners[0], 10)
            pygame.draw.circle(surface, colours["orange"].colour, surfaceCorners[1], 10)


            newScale = graph.screenSize
            newPosition = (0, 0)

            panOffset = (0, 0)
            zoomOffset = (0, 0)

            # check if the graph has been panned or zoomed and store if they have into boolean variables
            zoomed = data.zoom != graph.zoom
            panned = SigFig(data.bounds.CENTRE[0], 6) != SigFig(graph.bounds.CENTRE[0], 6) or \
                     SigFig(data.bounds.CENTRE[1], 6) != SigFig(graph.bounds.CENTRE[1], 6)
            # 6 is the amount of significant figures to round to, 
            # this allows enough precision for the floating-point value
            

            if panned or zoomed:
                newScale = (surfaceCorners[1][0] - surfaceCorners[0][0],
                            surfaceCorners[1][1] - surfaceCorners[0][1])
                newScale = tuple(int(np.abs(i)) for i in newScale)

                newPosition = (int(surfaceCorners[0][0]), int(surfaceCorners[0][1])) 


            try:
                if newScale != graph.screenSize:
                    tempSurface = pygame.transform.scale(dataSurface, newScale)
                else:
                    tempSurface = data.surface
                self.surface.blit(tempSurface, newPosition)
            except:
                # print("Error when blitting surface - ignoring and continuing")
                self.timeToNextUpdate = 0    # Force a frame update
        
        # print((time.perf_counter() - startTime) / (deltatime.deltaTime if deltatime.deltaTime != 0 else 1) * 100)



class Event:
    def __init__(self, type, data) -> None:
        self.type = type
        self.data = data

    def __str__(self):
        return f"'{self.type}' --> '{self.data}'"