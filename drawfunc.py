import math
import time

import numpy as np
import colours
import pygame

import graph
import main
from numstr import *
from graph import *
from main import *
import __main__


INCREMENT_FACTOR = 1

screenSize = [800, 600]
screenCentre = [400, 300]
zoomedOffset = [0, 0]
zoomedOffsetInverse = [0, 0]
orgPos = [0, 0]

offset = [0, 0]
zoom = 10

equations = []
bounds = None

DEGREES = False

replacement = {
    "sin(": "np.sin(",
    "cos(": "np.cos(",
    "tan(": "np.tan(",
    "sin-1(": "np.arcsin(",
    "cos-1(": "np.arccos(",
    "tan-1(": "np.arctan(",
    "log(": "math.log10(",
    "float(": "math.floor(",
    "ceil(": "math.ceil("
}

plottedEquList = []


class PlottedEquation:
    def __init__(self, equString, colour):
        self.surface = pygame.Surface(screenSize, pygame.SRCALPHA)
        self.colour = colour

        self.surfacePosition = bounds.NW if bounds is not None else (0, 0)
        self.surfaceSize = tuple(numpy.subtract(bounds.SE, bounds.NW)) if bounds is not None else (800, 600)

        self.oldString, self.equation = "cos(x)", "cos(x)" #equString, equString
        self.ReplaceEquationString()

    def GetSurface(self):
        return self.surface

    def Update(self, equString):
        self.oldString = "cos(x)"
        self.ReplaceEquationString()

    def ResetSurface(self):
        self.surface.fill(colours.TRANSPARENT)

    def ReplaceEquationString(self):
        tempString = self.oldString
        for k, v in replacement.items():
            tempString = tempString.replace(k, v)
        self.equation = tempString

    def RedrawSurface(self):
        self.ResetSurface()

        if self.equation == "":
            return

        points = []
        start, end = bounds.W, bounds.E
        increment = ((end[0] - start[0]) / screenSize[0]) / INCREMENT_FACTOR

        for x in FloatRange(start[0], end[0], increment):
            points.append((x, - eval(self.equation)))

        # extremeValues = bounds.N[1] + screenCentre[1], bounds.S[1] + screenCentre[1]

        lastX, lastY = points[0]
        drawOffset = -zoomedOffset[0] + screenCentre[0], -zoomedOffset[1] + screenCentre[1]

        for x, y in points:
            plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
            plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

            # if extremeValues[1] > plotStart[1] > extremeValues[0]:
            #     pass
            pygame.draw.line(self.surface, colours.PygameColour("red"), plotStart, plotEnd, 3)

            lastX, lastY = x, y

    def __str__(self):
        return f"{self.equation}"


def UpdateValues(_screenSize, _screenCentre, _zoomedOffset, _zoomedOffsetInverse,
                 _orgPos, _offset, _zoom, _equations, _bounds):
    global screenSize, screenCentre, zoomedOffset, zoomedOffsetInverse, orgPos, offset, zoom, equations, bounds

    screenSize = _screenSize
    screenCentre = _screenCentre
    zoomedOffset = _zoomedOffset
    zoomedOffsetInverse = _zoomedOffsetInverse
    orgPos = _orgPos
    offset = _offset
    zoom = _zoom
    offset = _offset
    bounds = _bounds


def GetBounds():
    return bounds


def FloatRange(start, stop, step, centre=None):
    if centre is not None:
        array = [centre]

        x = centre
        while x > start:
            x -= step
            array.append(x)
        x = centre
        while x < stop:
            x += step
            array.append(x)

        array.sort()
        return array

    n = []
    while start < stop:
        n.append(start)
        start += step
    return n


def DrawEquation(surface, bounds, equation):
    points = []
    start, end = bounds.W, bounds.E
    increment = ((end[0] - start[0]) / screenSize[0]) / INCREMENT_FACTOR

    for x in FloatRange(start[0], end[0], increment):
        points.append((x, - eval(equation)))

    extremeValues = bounds.N[1] + screenCentre[1], bounds.S[1] + screenCentre[1]

    lastX, lastY = points[0]
    drawOffset = -zoomedOffset[0] + screenCentre[0], -zoomedOffset[1] + screenCentre[1]

    for x, y in points:
        plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
        plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

        if extremeValues[1] > plotStart[1] > extremeValues[0]:
            pass
        pygame.draw.line(surface, colours.PygameColour("red"), plotStart, plotEnd, 3)

        lastX, lastY = x, y


def Initiate():
    for i in range(10):
        plottedEquList.append(PlottedEquation("", colours.PygameColour("red")))


def DrawAllSurfaces(surface):
    global plottedEquList

    t = time.perf_counter()
    for i, plottedGraph in enumerate(plottedEquList):
        if plottedGraph.equation == "":
            continue

        surface.blit(plottedGraph.GetSurface(), (0, 0))
    print((time.perf_counter() - t) * 1000, "ms")


def DrawingThread():
    global bounds, plottedEquList, equations

    # time.sleep(.1)

    # Start updating as much as possible
    # while main.running:

    t = time.perf_counter()
    for i, equ in enumerate(equations):
        if equ != "" and graph.CheckIfPreCalculationIsNecessary():
            plottedEquList[i].Update(equ)

    for i in plottedEquList:
        if graph.CheckIfPreCalculationIsNecessary():
            i.RedrawSurface()
    print((time.perf_counter() - t) * 1000, "ms")



def UpdateEquations(entries):
    global equations
    equations = [entry.get() for entry in entries]

