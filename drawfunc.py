import sympy
import numpy as np
import math
import pygame
import time
import random

from numpy import sin
from serialsurf import SerialisedSurface
from graph import CornerValues
from vector2 import *
from colours import *
from enum import IntEnum


INCREMENT_FACTOR = 1.5
ANTIALIAS = False

π = pi = 3.14159265358979323846
e = euler = 2.7182818284590452353602875
phi = golden = 1.618033988749894



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
        self.type = 1

        self.boundsAtBeginning: CornerValues = CornerValues(None)


    def RecalculatePoints(self, inData, inQueue, outQueue):
        firstPass = True

        lastBounds = None
        savedPoints = []
        
        while True:
            # wait for the in queue to have a length of 1 (this means data is present)
            startTime = time.perf_counter()

            while inQueue.qsize() < 1:
                time.sleep(0.01)

            if not firstPass:
                inData = inQueue.get()
            else:
                firstPass = False

                
            bounds = inData.bounds

            skipNoEquation = self.equation == ""            
            skipSameBounds = (lastBounds == bounds if bounds is not None else False)
            lastBounds = bounds

            # print(bounds.NW, bounds.SE)

            points = []
            start, end = bounds.W, bounds.E
            increment = (end[0] - start[0]) / (inData.screenSize[0] * INCREMENT_FACTOR)


            # Compute all the points on the graph
            if not skipNoEquation and not skipSameBounds:
                for x in np.arange(start[0], end[0], increment):
                    try:
                        points.append((x, eval(self.equation)))
                    except Exception as e:
                        points.append((x, np.inf))
                        print(f"{e} -----> Error at x={x}")
                savedPoints = points
            elif not skipNoEquation and skipSameBounds:
                points = savedPoints
            
            
            # Produce a pygame surface from the points just calculated
            surface = self.ListToSurfaceInThread(points, inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize )
            
            # Place into a class of thread output data
            outData = ThreadOutput(surface, bounds, inData.zoomedOffset)

            outQueue.put(outData)
            # print(f"Full process took {time.perf_counter() - startTime}")



    @classmethod
    def ListToSurfaceInThread(cls, array, equInstance, bounds, zoomedOffset, screenSize) -> pygame.Surface:
        surface = pygame.Surface(screenSize, pygame.SRCALPHA)
        surface.fill(colours["transparent"].colour)

        if len(array) == 0:
            return surface

        zoom = bounds.zoom
        screenCentre = (screenSize[0] // 2, screenSize[1] // 2)
        dottedCheckLine = 10

        extremeUpper, extremeLower = bounds.N[1], bounds.S[1]
        lastX, lastY = array[0]
        drawOffset = screenCentre[0] - zoomedOffset[0], screenCentre[1] - zoomedOffset[1]

        for x, y in array:
            if y == np.inf:
                continue

            plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
            plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

            asymptoteCheck = (y > extremeLower and lastY < extremeUpper) or (lastY > extremeLower and y < extremeUpper)
            infCheck = y == np.inf

            if not asymptoteCheck and not infCheck and dottedCheckLine > 0:
                if ANTIALIAS:
                    pass
                else:
                    pygame.draw.line(surface, equInstance.colour.colour, plotStart, plotEnd, 3)

            if equInstance.isDottedLine:
                dottedCheckLine -= 1
                if dottedCheckLine < -9:
                    dottedCheckLine = 10

            lastX, lastY = x, y

        surface = pygame.transform.flip(surface, False, True)
        return surface

    '''# Antialiased line
    # https://stackoverflow.com/questions/30578068/pygame-draw-anti-aliased-thick-line
    @classmethod
    def AntiAliasedLine(cls, surface, start, end):
        X0, Y0 = start
        X1, Y1 = end

        centerL1 = (X0+X1) / 2'''



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




# Cluster of data inputted into the thread
class ThreadInput:
    def __init__(self, bounds, screenSize, zoomedOffset, equation):
        self.bounds = bounds
        self.screenSize = screenSize
        self.zoomedOffset = zoomedOffset
        self.equation = equation


# Cluster of data outputted from the thread
class ThreadOutput:
    def __init__(self, surface, bounds, zoomedOffset):
        self.bounds = bounds
        self.zoom = bounds.zoom
        self.zoomedOffset = zoomedOffset
        self.serialisedSurface = SerialisedSurface(surface)



class SurfaceAndBounds:
    def __init__(self, surface, bounds) -> None:
        self.surface = surface
        self.bounds = bounds
        self.zoom = bounds.zoom        

    def __str__(self) -> str:
        return f'''Surface: {self.surface}
Bounds: {self.bounds}
Zoom: {self.zoom}'''