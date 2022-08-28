from re import I
import sympy
import numpy as np
import pygame

from vector2 import *
from colours import *
from enum import IntEnum
from multiprocessing import Process, Queue

π = pi = 3.14159265358979323846
e = 2.7182818284590452353602875

INCREMENT_FACTOR = 1.5



class EquationType(IntEnum):
    Equals = 0
    GreaterThanOrEqualTo = 1
    LessThanOrEqualTo = 2
    GreaterThan = 3
    LessThan = 4



class FunctionHolder:
    def __init__(self):
        self.plottedEquations = []
        self.processes = []
        self.returnQueues = []

        self.drawnFunctions = []


    def AppendEquation(self, graph, equation, colour):
        index = len(self.plottedEquations)

        self.drawnFunctions.append(None)
        self.plottedEquations.append( PlottedFunction(graph, equation, colour, 0) )
        self.returnQueues.append(Queue())
        self.processes.append( Process(target=self.plottedEquations[index].RedrawMySurface, 
                                       args=(graph, self.returnQueues[index])) )
        # self.processes[index].start()



    def UpdateEquations(self, graph):
        for i, plottedEquation in enumerate(self.plottedEquations):
            if not self.processes[i].is_alive():
                data = self.returnQueues[i].get()

                if data is not None:
                    self.drawnFunctions[i] = data
                self.processes[i] = Process(target=self.plottedEquations[i].RedrawMySurface, 
                                       args=(graph, self.returnQueues[i]))
                self.processes[i].start()


                












class PlottedFunction:
    def __init__(self, graph, equString, colour, equNumber, equationType=EquationType.Equals):
        self.surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)
        self.colour = colour
        self.equNumber = equNumber

        bounds = graph.bounds
        self.surfaceNW = bounds.NW if bounds is not None else (0, 0)
        self.surfaceCentre = bounds.CENTRE if bounds is not None else (0, 0)
        self.surfaceSE = bounds.SE if bounds is not None else (0, 0)
        self.surfaceZoom = graph.zoom
        self.bounds = bounds

        self.ReplaceEquationString(equString)

        self.equationType = equationType
        self.isDottedLine = self.equationType % 2 > 2

        self.currentProcess = self.returnQueue = None


    def ReplaceEquationString(self, string):
        self.equationString = self.equation = string


    def ResetSurface(self):
        self.surface.fill(colours["transparent"].colour)


    def RedrawMySurface(self, graph, queue):
        if self.equation == "":
            return
        
        self.ResetSurface()

        self.returnQueue = Queue()
        self.currentProcess = Process(target=self.CreateFunctionOnSurface, 
                                      args=(self.equation, self.colour, self.isDottedLine, graph, self.returnQueue))

        while self.currentProcess.is_alive():
            pass        # just wait

        queue.put(self.returnQueue.get())   # place into primary queue



    def __str__(self) -> str:
        return f"{self.equation}"




    def CreateFunctionOnSurface(equation, colour, isDottedLine, graph, queue):
        surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)
        surface.fill(colours["transparent"].colour)

        print("Started")

        if equation == "":
            queue.put(FinishedFunctionData(surface, graph.bounds, graph.zoom))
            return



        points = []
        start, end = graph.bounds.W, graph.bounds.E
        increment = (end[0] - start[0]) / (graph.screenSize[0] * INCREMENT_FACTOR)
        
        extremeLower, extremeUpper = graph.bounds.N[1], graph.bounds.S[1]
        lastX, lastY = points[0]
        drawOffset = graph.screenCentre[0] - graph.zoomedOffset[0], graph.screenCentre[1] - graph.zoomedOffset[1]
        dottedCheckLine = 10
        zoom = graph.zoom
        bounds = graph.bounds

            
        for x in np.arange(start[0], end[0], increment):
            try:
                points.append((x, -eval(equation)))
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
                    pygame.draw.line(surface, colour, plotStart, plotEnd, 3)

            if isDottedLine:
                dottedCheckLine -= 1
                if dottedCheckLine < -9:
                    dottedCheckLine = 10

            lastX, lastY = x, y

        finishedData = FinishedFunctionData(surface, bounds, zoom)
        queue.put(finishedData)
        print("Done")



class FinishedFunctionData:
    def __init__(self, surface, bounds, zoom):
        self.surface = surface
        self.bounds = bounds
        self.zoom = zoom



