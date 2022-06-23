import numpy as np
import sys, time, math

from vector2 import *
from graph import *


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



def SineTest(surface):
    arr = []
    for x in FloatRange(bounds[0][0], bounds[0][1], (bounds[0][1] - bounds[0][0])/screenSize[0]):
        arr.append((x, zoom*np.sin(x)))

    zoomedOffset = Vector2(offset[0] * zoom, offset[1] * zoom)

    for i in range(len(arr) - 1):
        start = Vector2(i, arr[i][1] + screenSize[1] / 2)
        end = Vector2(i, arr[i + 1][1] + screenSize[1] / 2)

        pygame.draw.line(surface, colours.PygameColour("red"), start.Tuple(), end.Tuple(), 3)
