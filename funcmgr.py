from multiprocessing import Process, Queue
import threading
from typing import List
from colours import *

import time
import pygame
import numpy as np
import drawfunc


class FunctionManager:
    def __init__(self, graph):
        self.currentEquations: List[drawfunc.PlottedEquation] = []
        self.numbersBoundsData: List[drawfunc.FinishedFunctionData] = []
        self.surfaceBoundsData: List[drawfunc.SurfaceAndBounds] = []
        self.myThreads = []
        self.myReturnQueues = []
        
        self.surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)



    def ScreenHasBeenResized(self, newSize):
        self.surface = pygame.Surface(newSize, pygame.SRCALPHA)



    def AddAnotherEquation(self, equation):
        index = len(self.currentEquations)
        newEquation = drawfunc.PlottedEquation(equation, index)
        self.currentEquations.append(newEquation)

        self.numbersBoundsData.append(None)
        self.surfaceBoundsData.append(None)
        self.myThreads.append(None)
        self.myReturnQueues.append(Queue())



    def UpdateThreads(self, graph):
        for i, equ in enumerate(self.currentEquations):
            # check if a thread should not be running, if so end it
            if not equ.active or equ.equation == "":
                equ.myThread.terminate()
                continue

            # if a thread should be running but is not (because it has just finished or 
            # the class has just been instantiated)

            threadIsNotNone = self.myThreads[i] is not None
            threadHasFinished = self.myReturnQueues[i].qsize() > 0

            # print(self.myReturnQueues[i].qsize())

            if equ.active and threadHasFinished if threadIsNotNone else True:
                if self.myThreads[i] is None:
                    print("Created the new thread")
                    self.myThreads[i] = Process(target=equ.RecalculatePoints, args=(graph, self.myReturnQueues[i], time.perf_counter()))
                    self.myThreads[i].start()
                    continue

                data: drawfunc.FinishedFunctionData = self.myReturnQueues[i].get()         # get data from return queue
                print(f"{self.numbersBoundsData.__str__()}")
                self.myThreads[i] = Process(target=equ.RecalculatePoints, args=(graph, self.myReturnQueues[i], time.perf_counter()))   # create new process
                self.myThreads[i].start()
                self.numbersBoundsData[i] = data                                      # set data in data array
                self.surfaceBoundsData[i] = drawfunc.SurfaceAndBounds(drawfunc.PlottedEquation.ProduceSurfaceFromList(graph, data.numberArray, equ), data.bounds)
                # save the drawn surface to the array, so it does not have to be redrawn every frame


    def BlitCurrentSurfaces(self, graph):
        self.surface.fill(colours["transparent"].colour)

        for i, data in enumerate(self.surfaceBoundsData):
            if self.currentEquations[i].equation == "" or data is None:
                continue

            dataSurface = data.surface

            newPosition = (0, 0)
            zoomScalar = graph.zoom / data.bounds.zoom  
            newScale = tuple([zoomScalar * x for x in graph.screenSize])

            if data.bounds.CENTRE != graph.bounds.CENTRE or data.bounds.zoom != graph.zoom:
                newPosition = np.subtract(tuple([data.zoom * x for x in data.bounds.NW]), graph.zoomedOffset)
                newPosition = np.add(newPosition, np.divide( np.divide(graph.screenCentre,2), 1/zoomScalar))
            

            print(f"{newPosition} - {newScale} : done? {newScale != graph.screenSize}")

            if newScale != graph.screenSize:
                tempSurface = pygame.transform.scale(dataSurface, newScale)
            else:
                tempSurface = data.surface


            self.surface.blit(tempSurface, newPosition)



