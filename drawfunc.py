from socket import INADDR_ALLHOSTS_GROUP
import sympy
import numpy as np
import math
import pygame
import time
import random

from numpy import sin
from graph import CornerValues
from vector2 import *
from colours import *
from enum import IntEnum


INCREMENT_FACTOR = 10
π = pi = 3.14159265358979323846
e = 2.7182818284590452353602875
Φ = φ = phi = goldenRatio = 1.618033988749894



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


    def RecalculatePoints(self, inData, inQueue, outQueue):
        firstPass = True

        # time.sleep(random.uniform(0, 0.2))
        while True:
            # wait for the in queue to have a length of 1 (this means data is present)
            while inQueue.qsize() < 1:
                time.sleep(0.01)

            if not firstPass:
                inData = inQueue.get()
            else:
                firstPass = False

                
            skip = self.equation == ""
            bounds = inData.bounds

            points = []
            start, end = bounds.W, bounds.E
            increment = (end[0] - start[0]) / (inData.screenSize[0] * INCREMENT_FACTOR)


            if not skip:
                for x in np.arange(start[0], end[0], increment):
                    try:
                        points.append((x, eval(self.equation)))
                    except Exception as e:
                        points.append((x, np.inf))
                        print(f"{e} -----> Error at x={x}")
            else:
                time.sleep(0.2)
                continue
            
            surface = self.ListToSurfaceInThread(points, inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize )
            outData = ThreadOutput(surface, bounds, inData.zoomedOffset)

            print(outData.serialisedSurface.GetSurface())
            np. set_printoptions(threshold=np.inf)
            print(outData.serialisedSurface.npArray)

            outQueue.put(outData)



    @classmethod
    def ListToSurfaceInThread(cls, array, equInstance, bounds, zoomedOffset, screenSize) -> pygame.Surface:
        surface = pygame.Surface(screenSize, pygame.SRCALPHA)
        surface.fill(colours["transparent"].colour)

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
                pygame.draw.line(surface, equInstance.colour.colour, plotStart, plotEnd, 3)

            if equInstance.isDottedLine:
                dottedCheckLine -= 1
                if dottedCheckLine < -9:
                    dottedCheckLine = 10

            lastX, lastY = x, y

        surface = pygame.transform.flip(surface, False, True)
        return surface




    @classmethod
    def ProduceSurfaceFromList(cls, graph, array, equInstance) -> pygame.Surface:
        startTime = time.perf_counter()
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
        # print(time.perf_counter() - startTime)
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





# This is a class that converts a pygame Surface into a serialisable
# Numpy array that can be transferred in queues

class SerialisedSurface:
    def __init__(self, surface):
        self.npArray = pygame.surfarray.array3d(surface)
        # self.alphaChannel = 

    def GetSurface(self):
        return pygame.surfarray.make_surface(self.npArray)




class NumberArrayToSurfaceData:
    def __init__(self, ss, b, z, zo, sc):
        self.screenSize = ss
        self.bounds = b
        self.zoom = z
        self.zoomedOffset = zo
        self.screenCentre = sc



class SurfaceAndBounds:
    def __init__(self, surface, bounds) -> None:
        self.surface = surface
        self.bounds = bounds
        self.zoom = bounds.zoom        

    def __str__(self) -> str:
        return f'''Surface: {self.surface}
Bounds: {self.bounds}
Zoom: {self.zoom}'''