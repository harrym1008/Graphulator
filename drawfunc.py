import multiprocessing
from re import I
import sympy
import numpy as np
import pygame

import graph
from graph import CornerValues

from vector2 import *
from colours import *
from enum import IntEnum
from multiprocessing import Process, Queue

π = pi = 3.14159265358979323846
e = 2.7182818284590452353602875
Φ = φ = phi = goldenRatio = 1.618033988749894

INCREMENT_FACTOR = 1.5



class EquationType(IntEnum):
    Equals = 0
    GreaterThanOrEqualTo = 1
    LessThanOrEqualTo = 2
    GreaterThan = 3
    LessThan = 4



strToGraphType = {
    ">=": EquationType.GreaterThanOrEqualTo,
    "<=": EquationType.LessThanOrEqualTo,
    "=": EquationType.Equals,
    "<": EquationType.LessThan,
    ">": EquationType.GreaterThan
}







class EquationType(IntEnum):
    Equals = 0
    GreaterThanOrEqualTo = 1
    LessThanOrEqualTo = 2
    GreaterThan = 3
    LessThan = 4



class SurfaceWithBounds:
    def __init__(self, surface, bounds):
        self.surface: pygame.Surface = surface
        self.bounds: graph.CornerValues = bounds




class PlottedEquation:
    def __init__(self, equation, index):
        self.active = True
        self.equation = equation
        self.index = index
        self.colour = GetColourForPlotIndex(index)

        self.type = EquationType.Equals
        self.isDottedLine = False
        self.UpdateEquationType()

        # Create a thread and a return queue
        # The thread is a dummy that will not actually be started, a new one will be instantiated
        # It is only instantiated here so that its variable is_alive returns false
        self.myThread: multiprocessing.Process = Process(target=self.RedrawSurface, args=())
        self.myReturnQueue: multiprocessing.Queue = Queue()

        self.boundsAtBeginning: CornerValues = None




    def RedrawSurface(self, graph):
        surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)
        surface.fill(colours["transparent"].colour)

        if self.equation == "":
            data = SurfaceWithBounds(surface, graph.bounds)
            self.myReturnQueue.put(data)
            return



        bounds = graph.bounds
        zoom = bounds.zoom

        points = []
        start, end = bounds.W, bounds.E
        increment = (end[0] - start[0]) / (graph.screenSize[0] * INCREMENT_FACTOR)

        extremeUpper, extremeLower = bounds.N[1], bounds.S[1]
        lastX, lastY = 0, 0
        drawOffset = graph.screenCentre[0] - graph.zoomedOffset[0], graph.screenCentre[1] - graph.zoomedOffset[1]

        for x in np.arange(start[0], end[0], increment):
            try:
                points.append((x, -eval(self.equation)))
            except Exception as e:
                points.append((x, np.inf))
                print(f"{e} -----> Error at x={x}")


        for x, y in points:
            if y == np.inf:
                continue

            plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
            plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

            asymptoteCheck = (y > extremeUpper and lastY < extremeLower) or (lastY > extremeUpper and y < extremeLower)
            infCheck = y == np.inf

            if not asymptoteCheck and not infCheck and dottedCheckLine > 0:
                    pygame.draw.line(surface, self.colour, plotStart, plotEnd, 3)

            if self.isDottedLine:
                dottedCheckLine -= 1
                if dottedCheckLine < -9:
                    dottedCheckLine = 10

            lastX, lastY = x, y

        data = SurfaceWithBounds(surface, bounds)
        self.myReturnQueue.put(data)




    def ConvertEquation(self):
        return self.equation


    def UpdateEquationType(self):
        self.type = strToGraphType["="]
        for string in strToGraphType.keys():
            if string in self.equation:
                self.type = strToGraphType[string]
        self.isDottedLine = self.type % 2 > 2



class FinishedFunctionData:
    def __init__(self, surface, bounds, zoom):
        self.surface = surface
        self.bounds = bounds
        self.zoom = zoom



