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

INCREMENT_FACTOR = 1.5

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
quitting = False

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
    def __init__(self, equString, colour, equationNumber):
        self.surface = pygame.Surface(screenSize, pygame.SRCALPHA)
        self.colour = colour
        self.equNumber = equationNumber

        self.surfaceNW = bounds.NW if bounds is not None else (0, 0)
        self.surfaceCentre = bounds.CENTRE if bounds is not None else (0, 0)
        self.surfaceSE = bounds.SE if bounds is not None else (0, 0)
        self.surfaceZoom = zoom

        self.oldString, self.equation = equString, equString
        self.ReplaceEquationString()

    def GetSurface(self):
        return self.surface

    def Update(self, equString):
        self.oldString = equString
        self.ReplaceEquationString()

    def ResetSurface(self, surface=None):
        if surface is not None:
            surface.fill(colours.TRANSPARENT)
            return surface

        self.surface.fill(colours.TRANSPARENT)

    def ReplaceEquationString(self):
        tempString = self.oldString
        for k, v in replacement.items():
            tempString = tempString.replace(k, v)
        self.equation = tempString

    def RedrawSurface(self):
        if self.equation == "":
            self.ResetSurface()
            return

        tempSurface = pygame.Surface(screenSize, pygame.SRCALPHA)
        tempSurface = self.ResetSurface(tempSurface)
        # self.surface.fill(colours.PygameColour("yellow"))

        # print(self.surfaceZoom, self.surfacePosition)

        points = []
        start, end = bounds.W, bounds.E
        increment = ((end[0] - start[0]) / screenSize[0]) / INCREMENT_FACTOR

        lastX = 0
        for x in np.arange(start[0], end[0], increment):
            try:
                points.append((x, - eval(self.equation)))
            except:
                points.append((x, 0))

        extremeLower, extremeUpper = bounds.N[1], bounds.S[1]

        lastX, lastY = points[0]
        drawOffset = -zoomedOffset[0] + screenCentre[0], -zoomedOffset[1] + screenCentre[1]


        for x, y in points:
            plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
            plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

            asymptoteCheck = (y > extremeUpper and lastY < extremeLower) or (lastY > extremeUpper and y < extremeLower)

            if not asymptoteCheck:
                pygame.draw.line(tempSurface, self.colour, plotStart, plotEnd, 3)

            lastX, lastY = x, y

        self.surfaceNW = bounds.NW if bounds is not None else (0, 0)
        self.surfaceSE = bounds.SE if bounds is not None else (0, 0)
        self.surface = tempSurface
        self.surfaceZoom = zoom

    def __str__(self):
        return f"{self.equation}"


def UpdateValues(_screenSize, _screenCentre, _zoomedOffset, _zoomedOffsetInverse,
                 _orgPos, _offset, _zoom, _equations, _bounds):
    global screenSize, screenCentre, zoomedOffset, zoomedOffsetInverse, orgPos, offset, \
        zoom, equations, bounds, surfaceMaxSize, surfaceCentre
    screenSize = _screenSize
    screenCentre = _screenCentre
    zoomedOffset = _zoomedOffset
    zoomedOffsetInverse = _zoomedOffsetInverse
    orgPos = _orgPos
    offset = _offset
    zoom = _zoom
    offset = _offset
    bounds = _bounds


def Initiate():
    for i in range(10):
        plottedEquList.append(PlottedEquation("", colours.lineColours[i % len(colours.lineColours)], i))


def DrawAllSurfaces(surface):
    global plottedEquList

    for i, plottedGraph in enumerate(plottedEquList):
        if plottedGraph.equation == "":
            continue

        plotSurface = plottedGraph.GetSurface()
        newPosition = (0, 0)

        if plottedGraph.surfaceNW != bounds.NW or plottedGraph.surfaceZoom != zoom:
            oldNW = plottedGraph.surfaceNW
            oldSE = plottedGraph.surfaceSE
            oldCentre = plottedGraph.surfaceCentre
            oldZoom = plottedGraph.surfaceZoom

            # calculating new zoom
            zoomScalar = zoom / oldZoom
            newScale = tuple([zoomScalar * x for x in screenSize])

            if plottedGraph.surfaceNW != bounds.NW:
                newPosition = np.subtract(tuple([zoom * x for x in oldNW]), zoomedOffset)

            plotSurface = pygame.transform.scale(plotSurface, newScale)
            newPosition = np.add(newPosition, screenCentre)

        surface.blit(plotSurface, newPosition)


def SetToQuit():
    global quitting
    quitting = True


def DrawingThread():
    global bounds, plottedEquList, equations

    iteration = 0
    wait = GetWaitTime()

    while True:
        if quitting:
            return

        # t = time.perf_counter()

        for i, equ in enumerate(equations):
            if equ != "" and graph.CheckIfPreCalculationIsNecessary():
                plottedEquList[i].Update(equ)

        for i in plottedEquList:
            if graph.CheckIfPreCalculationIsNecessary():
                i.RedrawSurface()

        time.sleep(wait)
        iteration += 1

        if iteration >= 3:
            wait = GetWaitTime()


def GetWaitTime():
    global INCREMENT_FACTOR

    counter = 0
    for i in equations:
        if i != "":
            counter += 1

    if counter == 0:
        counter = 1

    INCREMENT_FACTOR = 1.8 - counter * 0.12

    return counter * 0.04


def UpdateEquations(entries):
    global equations
    equations = [entry.get() for entry in entries]
