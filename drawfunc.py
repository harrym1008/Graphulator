import sympy
import numpy as np
import math
import pygame
import time

from graph import CornerValues
from vector2 import *
from colours import *
from enum import IntEnum

π = pi = 3.14159265358979323846
e = 2.7182818284590452353602875
Φ = φ = phi = goldenRatio = 1.618033988749894

INCREMENT_FACTOR = 1.5



strToGraphType = {
    ">=": 4,
    "<=": 3,
    "=": 0,
    "<": 1, 
    ">": 2
}

fullLines = [0, 3, 4]






class EquationType(IntEnum):
    Equals = 0
    GreaterThanOrEqualTo = 1
    LessThanOrEqualTo = 2
    GreaterThan = 3
    LessThan = 4



class PlottedEquation:
    def __init__(self, equation, index):
        self.active = True
        self.equation = equation
        self.index = index
        self.colour = GetColourForPlotIndex(index)

        self.type = 0
        self.isDottedLine = False
        self.UpdateEquationType()

        self.boundsAtBeginning: CornerValues = None


    def RecalculatePoints(self, graphData, inQueue, outQueue):
        firstPass = True
        while True:
            startTime = time.perf_counter()

            # wait for the in queue to have a length of 1 (this means data is present)
            while inQueue.qsize() < 1:
                time.sleep(0.01)

            if not firstPass:
                graphData = inQueue.get()
            else:
                firstPass = False
            # print(graphData)


            # print(f"{graphData.bounds.NW}, {graphData.zoom}")

            if self.equation == "":
                data = FinishedFunctionData([], graphData.bounds)
                outQueue.put(data)
                return


            bounds = graphData.bounds

            points = []
            start, end = bounds.W, bounds.E
            increment = (end[0] - start[0]) / (graphData.screenSize[0] * INCREMENT_FACTOR)

            for x in np.arange(start[0], end[0], increment):
                try:
                    points.append((x, eval(self.equation)))
                except Exception as e:
                    points.append((x, np.inf))
                    print(f"{e} -----> Error at x={x}")
            

            data = FinishedFunctionData(points, bounds)
            outQueue.put(data)

            # print(f"Okay I am done. Calculated in {time.perf_counter() - startTime} seconds")
            # print(f"{graphData.bounds.NW}, {graphData.zoom}")



    @classmethod
    def ProduceSurfaceFromList(cls, graph, array, equInstance) -> pygame.Surface:
        surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)
        surface.fill(colours["transparent"].colour)

        bounds = graph.bounds
        zoom = graph.zoom
        dottedCheckLine = 10

        extremeUpper, extremeLower = bounds.N[1], bounds.S[1]
        lastX, lastY = array[0]
        drawOffset = graph.screenCentre[0] - graph.zoomedOffset[0], graph.screenCentre[1] - graph.zoomedOffset[1]

        for x, y in array:
            if y == np.inf:
                continue

            plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
            plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

            asymptoteCheck = (y > extremeLower and lastY < extremeUpper) or (lastY > extremeLower and y < extremeUpper)
            infCheck = y == np.inf

            if not asymptoteCheck and not infCheck and dottedCheckLine > 0:
                pygame.draw.line(surface, equInstance.colour.colour, plotStart, plotEnd, 3)

            if equInstance.isDottedLine:
                dottedCheckLine -= 1
                if dottedCheckLine < -9:
                    dottedCheckLine = 10

            lastX, lastY = x, y

        surface = pygame.transform.flip(surface, False, True)
        return surface




    def ConvertEquation(self):
        return self.equation


    def UpdateEquationType(self):
        self.type = strToGraphType["="]
        for string in strToGraphType.keys():
            if string in self.equation:
                self.type = strToGraphType[string]
                print(self.type)
                break
        self.isDottedLine = self.type not in fullLines




class FinishedFunctionData:
    def __init__(self, array, bounds):
        self.numberArray = array
        self.bounds = bounds
        self.zoom = bounds.zoom

    def __str__(self) -> str:
        return f'''Numbers: {self.numberArray}
Bounds: {self.bounds}
Zoom: {self.zoom}'''



class ThreadInputData:
    def __init__(self, zoom, bounds, screenSize):
        self.zoom = zoom
        self.bounds = bounds
        self.screenSize = screenSize
    
    def __str__(self) -> str:
        return f'''Zoom: {self.zoom}, ScreenSize: {self.screenSize}, Bounds: {self.bounds.ShortString()}\n'''



class SurfaceAndBounds:
    def __init__(self, surface, bounds) -> None:
        self.surface = surface
        self.bounds = bounds
        self.zoom = bounds.zoom        

    def __str__(self) -> str:
        return f'''Surface: {self.surface}
Bounds: {self.bounds}
Zoom: {self.zoom}'''