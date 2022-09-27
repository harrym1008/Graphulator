from msilib import datasizemask
from multiprocessing import Process, Queue
from typing import List
from colours import *

import pygame
import drawfunc
import deltatime
import time


class FunctionManager:
    def __init__(self, graph):
        self.currentEquations: List[drawfunc.PlottedEquation] = []
        self.numbersBoundsData: List[drawfunc.FinishedFunctionData] = []
        self.surfaceBoundsData: List[drawfunc.SurfaceAndBounds] = []
        self.myThreads = []
        self.myInQueues = []
        self.myOutQueues = []
        
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
        self.myInQueues.append(Queue())
        self.myOutQueues.append(Queue())



    def UpdateThreads(self, graph):
        startTime = time.perf_counter()
        for i, equ in enumerate(self.currentEquations):
            # check if a thread should not be running, if so end it
            if not equ.active or equ.equation == "":
                equ.myThread.terminate()
                continue

            # if a thread should be running but is not (because it has just finished or 
            # the class has just been instantiated)

            threadIsNotNone = self.myThreads[i] is not None
            newDataIsAvailable = self.myInQueues[i].qsize() > 0

            # print(self.myInQueues[i].qsize())

            if equ.active and newDataIsAvailable if threadIsNotNone else True:
                threadData = drawfunc.ThreadInputData(graph.zoom, graph.bounds, graph.screenSize, graph.zoomedOffset)
                # print(threadData)

                if self.myThreads[i] is None:
                    print("Created the new thread")
                    self.myThreads[i] = Process(target=equ.RecalculatePoints, args=(threadData, self.myOutQueues[i], self.myInQueues[i]))
                    self.myThreads[i].start()
                    self.myOutQueues[i].put(threadData)
                    continue

                data: drawfunc.FinishedFunctionData = self.myInQueues[i].get()         # get data from return queue
                
                '''print("Creating new thread")
                self.myThreads[i] = Process(target=equ.RecalculatePoints, args=(threadData, self.myInQueues[i], time.perf_counter()))   # create new process
                self.myThreads[i].start()'''
                self.numbersBoundsData[i] = data                                      # set data in data array
                graphData = drawfunc.NumberArrayToSurfaceData(graph.screenSize, data.bounds, data.zoom, data.zoomedOffset, graph.screenCentre)
                self.surfaceBoundsData[i] = drawfunc.SurfaceAndBounds(
                    drawfunc.PlottedEquation.ProduceSurfaceFromList(graphData, data.numberArray, equ)
                    , data.bounds)

                self.myOutQueues[i].put(threadData)
                
                # save the drawn surface to the array, so it does not have to be redrawn every frame
        # print((time.perf_counter() - startTime) / (deltatime.deltaTime if deltatime.deltaTime != 0 else 1) * 100, end=" ")





    def BlitCurrentSurfaces(self, graph):
        startTime = time.perf_counter()
        self.surface.fill(colours["transparent"].colour)

        for i, data in enumerate(self.surfaceBoundsData):
            if self.currentEquations[i].equation == "" or data is None:
                continue

            dataSurface = data.surface

            # equation for X: p = -oz + 0.5s + xz
            # equation for Y: p = -oz + 0.5s - yz

            surfaceCorners = [(
                -graph.offset[0] * graph.zoom + 0.5 * graph.screenSize[0] + data.bounds.NW[0] * graph.zoom, 
                graph.offset[1] * graph.zoom + 0.5 * graph.screenSize[1] - data.bounds.NW[1] * graph.zoom
                ),(
                -graph.offset[0] * graph.zoom + 0.5 * graph.screenSize[0] + data.bounds.SE[0] * graph.zoom, 
                graph.offset[1] * graph.zoom + 0.5 * graph.screenSize[1] - data.bounds.SE[1] * graph.zoom
                )]

            newScale = (int(surfaceCorners[1][0] - surfaceCorners[0][0]), 
                        int(surfaceCorners[0][1] - surfaceCorners[1][1]))

            newPosition = (int(surfaceCorners[0][0]), int(surfaceCorners[1][1]))

            print(f"{surfaceCorners}   ----> {newPosition} - {newScale} : done? {newScale != graph.screenSize}")

            if newScale != graph.screenSize:
                try:
                    tempSurface = pygame.transform.scale(dataSurface, newScale)
                except pygame.error as e:
                    tempSurface = pygame.transform.scale(dataSurface, (256, 256))
                    print(e)
            else:
                tempSurface = data.surface


            self.surface.blit(tempSurface, newPosition)
        
        # print((time.perf_counter() - startTime) / (deltatime.deltaTime if deltatime.deltaTime != 0 else 1) * 100)



