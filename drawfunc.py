import math
import numpy as np
import colours
import pygame

from numstr import *
from graph import *
from main import *

INCREMENT_FACTOR = .3

screenSize = [800, 600]
screenCentre = [400, 300]
zoomedOffset = [0, 0]
zoomedOffsetInverse = [0, 0]
orgPos = [0, 0]

offset = [0, 0]
zoom = 10


def UpdateValues(_screenSize, _screenCentre, _zoomedOffset, _zoomedOffsetInverse, _orgPos, _offset, _zoom):
    global screenSize, screenCentre, zoomedOffset, zoomedOffsetInverse, orgPos, offset, zoom

    screenSize = _screenSize
    screenCentre = _screenCentre
    zoomedOffset = _zoomedOffset
    zoomedOffsetInverse = _zoomedOffsetInverse
    orgPos = _orgPos
    offset = _offset
    zoom = _zoom


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


def SineTest(surface, bounds, equation):
    points = []
    start, end = bounds.W, bounds.E
    increment = ((end[0] - start[0]) / screenSize[0]) / INCREMENT_FACTOR

    for x in FloatRange(start[0], end[0], increment):
        points.append((x, eval(equation) ))

    lastX, lastY = points[0]
    drawOffset = -zoomedOffset[0] + screenCentre[0], -zoomedOffset[1] + screenCentre[1]

    for x, y in points:
        plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
        plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

        pygame.draw.line(surface, colours.PygameColour("red"), plotStart, plotEnd, 3)

        lastX, lastY = x, y
