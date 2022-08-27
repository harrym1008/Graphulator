import numpy as np
from enum import IntEnum
from graph import *
from main import *
from multiprocessing import Process, Queue
import graph

# Constant values
π = pi = 3.14159265358979323846
e = 2.7182818284590452353602875

INCREMENT_FACTOR = 1.5

screenSize = [800, 600]
screenCentre = [400, 300]

zoomedOffset = [0, 0]
zoomedOffsetInverse = [0, 0]
orgPos = [0, 0]

offset = [0, 0]
zoom = 10

drawingSurfaceSize = np.multiply(screenSize, 1.2)
drawingSurfaceCentre = np.multiply(screenCentre, 1.2)

equations = []
bounds = None

DEGREES = False
quitting = False

changingMultiplier = -1

replacement = {
    "^": "**",
    "sin(": "np.sin(",
    "cos(": "np.cos(",
    "tan(": "np.tan(",
    "asin(": "np.arcsin(",
    "acos(": "np.arccos(",
    "atan(": "np.arctan(",
    "log(": "math.log10(",
    "float(": "math.floor(",
    "ceil(": "math.ceil(",
    "fact(": "Factorial("
}
plottedEquList = []


class EquationType(IntEnum):
    Equals = 0
    GreaterThanOrEqualTo = 1
    LessThanOrEqualTo = 2
    GreaterThan = 3
    LessThan = 4


class PlottedEquation:
    def __init__(self, equString, colour, equationNumber, equationType=EquationType.Equals):
        self.surface = pygame.Surface(screenSize, pygame.SRCALPHA)
        self.colour = colour
        self.equNumber = equationNumber

        self.surfaceNW = bounds.NW if bounds is not None else (0, 0)
        self.surfaceCentre = bounds.CENTRE if bounds is not None else (0, 0)
        self.surfaceSE = bounds.SE if bounds is not None else (0, 0)
        self.surfaceZoom = zoom

        self.oldString = self.equation = equString
        self.ReplaceEquationString()

        self.equationType = equationType
        self.dottedLine = self.equationType % 2 > 2

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
        if self.oldString == "":
            self.surface = self.ResetSurface(self.surface)
            return

        tempSurface = pygame.Surface(screenSize, pygame.SRCALPHA)
        tempSurface = self.ResetSurface(tempSurface)
        # self.surface.fill(colours.PygameColour("yellow"))

        # print(self.surfaceZoom, self.surfacePosition)

        points = []
        start, end = bounds.W, bounds.E
        increment = ((end[0] - start[0]) / screenSize[0]) / INCREMENT_FACTOR

        lastX = 0
        c = changingMultiplier

        for x in np.arange(start[0], end[0], increment):
            try:
                points.append((x, - eval(self.equation)))
            except Exception as e:
                points.append((x, np.inf))
                print(f"{e} ---> Error at x={x}")

        extremeLower, extremeUpper = bounds.N[1], bounds.S[1]

        lastX, lastY = points[0]
        drawOffset = -zoomedOffset[0] + screenCentre[0], -zoomedOffset[1] + screenCentre[1]

        dottedCheckLine = 10

        for x, y in points:

            if y == np.inf:
                continue

            plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
            plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

            asymptoteCheck = (y > extremeUpper and lastY < extremeLower) or (lastY > extremeUpper and y < extremeLower)
            infCheck = y != np.inf

            if not asymptoteCheck and dottedCheckLine > 0 and infCheck:
                pygame.draw.line(tempSurface, self.colour, plotStart, plotEnd, 3)

            if self.dottedLine:
                dottedCheckLine -= 1
                if dottedCheckLine < -9:
                    dottedCheckLine = 10

            lastX, lastY = x, y

        self.surfaceNW = bounds.NW if bounds is not None else (0, 0)
        self.surfaceSE = bounds.SE if bounds is not None else (0, 0)
        self.surface = tempSurface
        self.surfaceZoom = zoom

    def __str__(self):
        return f"{self.equation}"



def CreateNewSurface(q, equ, bounds, colour, dottedLine):
    tempSurface = pygame.Surface(screenSize, pygame.SRCALPHA)
    # self.surface.fill(colours.PygameColour("yellow"))

    # print(self.surfaceZoom, self.surfacePosition)

    points = []
    start, end = bounds.W, bounds.E
    increment = ((end[0] - start[0]) / screenSize[0]) / INCREMENT_FACTOR

    lastX = 0
    c = changingMultiplier

    for x in np.arange(start[0], end[0], increment):
        try:
            points.append((x, - eval(equ)))
        except Exception as e:
            points.append((x, np.inf))
            print(f"{e} ---> Error at x={x}")

    extremeLower, extremeUpper = bounds.N[1], bounds.S[1]

    lastX, lastY = points[0]
    drawOffset = -zoomedOffset[0] + screenCentre[0], -zoomedOffset[1] + screenCentre[1]

    dottedCheckLine = 10

    for x, y in points:

        if y == np.inf:
            continue

        plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
        plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

        asymptoteCheck = (y > extremeUpper and lastY < extremeLower) or (lastY > extremeUpper and y < extremeLower)
        infCheck = y != np.inf

        if not asymptoteCheck and dottedCheckLine > 0 and infCheck:
            pygame.draw.line(tempSurface, colour, plotStart, plotEnd, 3)

        if dottedLine:
            dottedCheckLine -= 1
            if dottedCheckLine < -9:
                dottedCheckLine = 10

        lastX, lastY = x, y

    surfaceNW = bounds.NW if bounds is not None else (0, 0)
    surfaceSE = bounds.SE if bounds is not None else (0, 0)

    dataTuple = (surfaceNW, surfaceSE, tempSurface, zoom)
    q.put(dataTuple)



def UpdateValues(_screenSize, _screenCentre, _zoomedOffset, _zoomedOffsetInverse,
                 _orgPos, _offset, _zoom, _equations, _bounds):
    global screenSize, screenCentre, zoomedOffset, zoomedOffsetInverse, orgPos, offset, \
        zoom, equations, bounds, surfaceMaxSize, surfaceCentre, drawingSurfaceSize, drawingSurfaceCentre
    screenSize = _screenSize
    screenCentre = _screenCentre
    zoomedOffset = _zoomedOffset
    zoomedOffsetInverse = _zoomedOffsetInverse
    orgPos = _orgPos
    offset = _offset
    zoom = _zoom
    offset = _offset
    bounds = _bounds

    drawingSurfaceSize = np.multiply(screenSize, 1.2)
    drawingSurfaceCentre = np.multiply(screenCentre, 1.2)


def Factorial(n):
    x = int(n)
    val = 1
    for i in range(2, x + 1):
        val *= i
    return val


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



currentProcesses = []
returnQueues = []


def DrawingProcessesThread():
    global bounds, plottedEquList, equations

    while True:


        time.sleep(0.1)



def UpdateProcesses():
    global bounds, plottedEquList, equations

    for i in range(len(currentProcesses)):
        currentProcesses[i].terminate()

    currentProcesses.clear()
    returnQueues.clear()


    for i, equ in enumerate(equations):
        graphObject =
        newProcess = Process()
        currentProcesses.append()






'''def DrawingThread():
    global bounds, plottedEquList, equations

    iteration = 0
    wait = GetWaitTime()

    while True:
        executionStart = time.perf_counter()

        if quitting:
            return

        for i, equ in enumerate(equations):
            if graph.CheckIfPreCalculationIsNecessary():
                plottedEquList[i].Update(equ)

        for i in plottedEquList:
            if graph.CheckIfPreCalculationIsNecessary():
                i.RedrawSurface()

        executionLength = time.perf_counter() - executionStart

        if wait < executionLength:
            executionLength = wait

        print(f"ExecutionLength: {executionLength}, Waiting: {wait - executionLength}")
        time.sleep(wait - executionLength)

        iteration += 1

        if iteration >= 3:
            wait = GetWaitTime()'''



def UpdateEquations(entries):
    global equations
    equations = [entry.get() for entry in entries]
