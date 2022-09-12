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
            if not equ.active and equ.equation == "":
                equ.myThread.terminate()
                continue

            # if a thread should be running but is not (because it has just finished or 
            # the class has just been instantiated)
            if equ.active and not equ.myThread.is_alive():
                if equ.myReturnQueue.qsize() == 0:
                    equ.myThread = Process(target=equ.UpdateEquationType, args=(graph,))
                    equ.myThread.start()
                    continue

                try:
                    data: drawfunc.FinishedFunctionData = equ.myReturnQueue.get()         # get data from return queue
                    self.surfaceBoundsData[i] = data                                      # set data in data array
                    equ.myThread = Process(target=equ.UpdateEquationType, args=(graph,))  # create new process
                    equ.myThread.start()                                                  # start the process  

                except:
                    continue


    def BlitCurrentSurfaces(self, graph):
        self.surface.fill(colours["transparent"].colour)

        for i, data in enumerate(self.surfaceBoundsData):
            if self.currentEquations[i].equation == "" or data is None:
                print("Uh oh! Data was none")
                continue

            newPosition = (0, 0)
            tempSurface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)

            if data.bounds.NW != graph.bounds.NW or data.bounds.zoom != graph.zoom:
                if data.bounds.NW != data.bounds.NW:
                    newPosition = np.subtract(tuple([graph.zoom * x for x in graph.bounds.NW]), graph.zoomedOffset)

                zoomScalar = graph.zoom / data.bounds.zoom
                newScale = tuple([zoomScalar * x for x in graph.screenSize])
                tempSurface = pygame.transform.scale(data.surface, newScale)
            else:
                tempSurface = data.surface

            self.surface.blit(tempSurface, newPosition)
