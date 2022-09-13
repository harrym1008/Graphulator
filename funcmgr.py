from multiprocessing import Process
from typing import List
from colours import *

import pygame
import numpy as np
import drawfunc


class FunctionManager:
    def __init__(self, graph):
        self.currentEquations: List[drawfunc.PlottedEquation] = []
        self.surfaceBoundsData: List[drawfunc.SurfaceWithBounds] = []
        self.surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)


    def AddAnotherEquation(self, equation):
        index = len(self.currentEquations)
        newEquation = drawfunc.PlottedEquation(equation, index)
        self.currentEquations.append(newEquation)
        self.surfaceBoundsData.append(None)



    def UpdateThreads(self, graph):
        for i, equ in enumerate(self.currentEquations):
            # check if a thread should not be running, if so end it
            if not equ.active or equ.equation == "":
                equ.myThread.terminate()
                continue

            # if a thread should be running but is not (because it has just finished or 
            # the class has just been instantiated)
            if equ.active and not equ.myReturnQueue.qsize(): #equ.myThread.is_alive():
                if equ.myThread is None:
                    equ.myThread = Process(target=equ.RecalculatePoints, args=(graph,))
                    equ.myThread.start()
                    continue

                data: drawfunc.FinishedFunctionData = equ.myReturnQueue.get()         # get data from return queue
                print(data)
                self.surfaceBoundsData[i] = data                                      # set data in data array
                print("OMGGGGGGGGGGGGGGGG")
                print(f"{self.surfaceBoundsData}")
                equ.myThread = Process(target=equ.RecalculatePoints, args=(graph,))   # create new process
                equ.myThread.start()  


    def BlitCurrentSurfaces(self, graph):
        self.surface.fill(colours["transparent"].colour)

        for i, data in enumerate(self.surfaceBoundsData):
            if self.currentEquations[i].equation == "" or data is None:
                continue

            dataSurface = drawfunc.PlottedEquation.ProduceSurfaceFromList(graph, data.numberArray, 
                          self.currentEquations[i])

            newPosition = (0, 0)
            tempSurface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)

            if data.bounds.NW != graph.bounds.NW or data.bounds.zoom != graph.zoom:
                if data.bounds.NW != data.bounds.NW:
                    newPosition = np.subtract(tuple([graph.zoom * x for x in graph.bounds.NW]), graph.zoomedOffset)

                zoomScalar = graph.zoom / data.bounds.zoom
                newScale = tuple([zoomScalar * x for x in graph.screenSize])
                tempSurface = pygame.transform.scale(dataSurface, newScale)
            else:
                tempSurface = dataSurface

            self.surface.blit(tempSurface, newPosition)



