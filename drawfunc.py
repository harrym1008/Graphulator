import numpy as np
import pygame
import colours
import time

from sympy.parsing.sympy_parser import standard_transformations, \
    implicit_multiplication_application, \
    convert_xor
from multiprocessing import cpu_count

from evaluate import *
from serialsurf import SerialisedSurface
from graph import CornerValues
from enum import IntEnum



INCREMENT_FACTOR = 1 if cpu_count() == 2 else 2
ANTIALIAS = False
TRANSFORMATIONS = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))

STR_GRAPH_TYPES = {
    "≥": 4,
    "≤": 3,
    "=": 0,
    "<": 1, 
    ">": 2
}

FULL_LINES = [0, 3, 4]



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
        self.colour = colours.GetColourForPlotIndex(index)

        self.type = 0
        self.isDottedLine = False
        self.UpdateEquationType()

        self.boundsAtBeginning: CornerValues = CornerValues(None)
        self.solutions = {"y": [],"x": []}


    def ChangeMyEquation(self, new):
        self.equation = new
        self.UpdateEquationType()




    def RecalculatePoints(self, inData, inQueue, outQueue, eventQueue):
        firstPass = True
        
        currentEquation = inData.equation.equation

        lastBounds = None
        savedPoints = []

        lastEquation = ""
        solutions = {"y": [],"x": []}
        solutionCount = len(solutions["x"]) + len(solutions["y"])

        print(f"Thread {self.index} has been started")

        a = 0
        b = 0
        c = 0
        tUpper = -10
        tLower = 10
        
        while True:
            # wait for the in queue to have a length of 1 (this means data is present)
            t = tLower + (tUpper-tLower) * (time.perf_counter() % 10) / 10

            while inQueue.qsize() < 1:
                time.sleep(0.1)

            # Get equation events (how the equation has changed so the thread can be updated)
            forceUpdate = False
            while eventQueue.qsize() > 0:
                forceUpdate = True
                event = eventQueue.get()
                if event.type == 0:
                    currentEquation = event.data
                elif event.type == 1:
                    a = event.data[0]
                    b = event.data[1]
                    c = event.data[2]
                    tLower = event.data[3]
                    tUpper = event.data[4]

                

            if not firstPass:
                inData = inQueue.get()
            else:
                firstPass = False


            if lastEquation != currentEquation:
                lastEquation = currentEquation
                solutions = PlottedEquation.GetSolutions(currentEquation)
                solutionCount = len(solutions["x"]) + len(solutions["y"])
                print(solutions, UnreplaceEquation(currentEquation))

                
            bounds = inData.bounds

            skipNoEquation = currentEquation == ""            
            skipSameBounds = (lastBounds == bounds if bounds is not None else False)
            lastBounds = bounds

            points = []
            yPoints = []
            xPoints = []

            start, end = bounds.SW, bounds.NE
            incrementY = (end[0] - start[0]) / (bounds.screenSize[0] * INCREMENT_FACTOR)
            incrementX = (end[0] - start[0]) / (bounds.screenSize[1] * INCREMENT_FACTOR)

            xRange = np.arange(start[0], end[0], incrementY)
            yRange = np.arange(start[1], end[1], incrementX)


            # Compute all the points on the graph
            if (not skipNoEquation and not skipSameBounds) or (not skipNoEquation and forceUpdate):
                # Loop through all Y solutions
                for i, solution in enumerate(solutions["y"]):
                    yPoints.append([])
                    for x in xRange:
                        try:
                            point = (x, float( eval(solution) ))
                        except:
                            point = (x, np.inf)
                        yPoints[i].append(point)
                            
                # Loop through all X solutions
                for i, solution in enumerate(solutions["x"]):
                    xPoints.append([])
                    for y in yRange:
                        try:
                            point = (float( eval(solution) ), y)
                        except:
                            point = (np.inf, y)
                        xPoints[i].append(point)
                points = yPoints + xPoints

                # points = PlottedEquation.GetLowHighValueXY(points, yRange)

                savedPoints = points
            elif not skipNoEquation and skipSameBounds:
                points = savedPoints
                

            surface = pygame.Surface(inData.screenSize, pygame.SRCALPHA)

            # Produce a pygame surface from the points just calculated
            if solutionCount == 1:

                if len(solutions["y"]) == 1:
                    surface = PlottedEquation.DrawSurfaceFromArray_YEquals(points[0], 
                                inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize )
                elif len(solutions["x"]) == 1:
                    surface = PlottedEquation.DrawSurfaceFromArray_XEquals(points[0], 
                                inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize )
            elif solutionCount > 1:
                for i in range(solutionCount):
                    isYEquals = i < len(solutions["y"])
                    if isYEquals:
                        tempSurface = PlottedEquation.DrawSurfaceFromArray_YEquals(points[i], 
                                    inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize)
                    else:
                        tempSurface = PlottedEquation.DrawSurfaceFromArray_XEquals(points[i], 
                                    inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize)

                    surface.blit(tempSurface, (0, 0))

            else:       # if there are no solutions
                time.sleep(0.3)


            # Place into a class of thread output data
            outData = ThreadOutput(surface, bounds, inData.zoomedOffset, (skipNoEquation or solutionCount == 0), solutions)

            outQueue.put(outData)
            # print(f"Full process took {time.perf_counter() - startTime}")



    @staticmethod
    def GetSolutions(strEqu):
        strEqu = UnreplaceEquation(strEqu)
        equ, lhs, rhs = PlottedEquation.ProduceSympyEquation(strEqu)
        print(equ, lhs, rhs)
        ySolutions = PlottedEquation.ProduceEquationSolutions(equ, "y")
        xSolutions = PlottedEquation.ProduceEquationSolutions(equ, "x")

        if equ is None:
            return {"y": [],"x": []}
        solutions = PlottedEquation.AssignSolutions(lhs, rhs, ySolutions, xSolutions)
        return solutions


    @staticmethod
    def AssignSolutions(lhs, rhs, yS, xS):
        empty = []

        if lhs == "y" or rhs == "y":
            return {"y": yS,"x": empty}
        if lhs == "x" or rhs == "x":
            return {"y": empty,"x": xS}
        return {"y": yS, "x": xS}


    @staticmethod
    def ProduceEquationSolutions(equ, category, replace=True):
        x, y = sp.symbols("x y")

        try:
            solveFor = x if category == "x" else y
            solved = sp.solve(equ, solveFor)
            print(solved)
            return [ReplaceEquation(str(solution)) if replace else str(solution) for solution in solved]
        except:
            return []


    @staticmethod
    def ProduceSympyEquation(strEqu, getHandSides=True):
        y = sp.symbols("y")
        returns = None, "", ""
        
        try:
            sides = strEqu.split("=")

            if len(sides) == 2:
                lhs, rhs = tuple(sp.parse_expr(side, transformations=TRANSFORMATIONS) for side in sides)
            elif len(sides) == 1:
                lhs, rhs = y, sp.parse_expr(sides[0], transformations=TRANSFORMATIONS)
            else:
                lhs, rhs = y, inf
                
            returns = sp.Eq(lhs, rhs), str(lhs), str(rhs)
        except:
            pass

        if getHandSides:
            return returns
        return returns[0]




    @staticmethod
    def DrawSurfaceFromArray_YEquals(array, equInstance, bounds, zoomedOffset, screenSize) -> pygame.Surface:
        surface = pygame.Surface(screenSize, pygame.SRCALPHA)
        surface.fill(colours.colours["transparent"].colour)

        if len(array) == 0:
            return surface

        zoom = bounds.zoom
        screenCentre = (screenSize[0] // 2, screenSize[1] // 2)
        dottedCheckLine = 10

        extremeUpper, extremeLower = bounds.S[1], bounds.N[1]
        lastX, lastY = array[0]
        drawOffset = screenCentre[0] - zoomedOffset[0], screenCentre[1] - zoomedOffset[1]

        for x, y in array:
            plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
            plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

            asymptoteCheck = (y > extremeLower and lastY < extremeUpper) or (lastY > extremeLower and y < extremeUpper)
            invalidNumberCheck = np.isnan(x) or np.isinf(x) or \
                                 np.isnan(y) or np.isinf(y) or \
                                 np.isnan(lastX) or np.isinf(lastX) or \
                                 np.isnan(lastY) or np.isinf(lastY)

            if not asymptoteCheck and not invalidNumberCheck:
                # pygame.draw.line(surface, equInstance.colour.faded, (plotStart[0], plotStart[1] + 2), (x * zoom + drawOffset[0], screenSize[1]), 2)
                if dottedCheckLine > 0:
                    pygame.draw.line(surface, equInstance.colour.colour, plotStart, plotEnd, 3)
                
            if equInstance.isDottedLine:
                dottedCheckLine -= 1
                if dottedCheckLine < -9:
                    dottedCheckLine = 10
                    

            lastX, lastY = x, y

        surface = pygame.transform.flip(surface, False, True)
        return surface



    @staticmethod
    def DrawSurfaceFromArray_XEquals(array, equInstance, bounds, zoomedOffset, screenSize) -> pygame.Surface:
        surface = pygame.Surface(screenSize, pygame.SRCALPHA)
        surface.fill(colours.colours["transparent"].colour)

        if len(array) == 0:
            return surface

        zoom = bounds.zoom
        screenCentre = (screenSize[0] // 2, screenSize[1] // 2)
        dottedCheckLine = 10

        extremeUpper, extremeLower = bounds.S[1], bounds.N[1]
        lastX, lastY = array[0]
        drawOffset = screenCentre[0] - zoomedOffset[0], screenCentre[1] - zoomedOffset[1]

        for x, y in array:
            plotStart = lastX * zoom + drawOffset[0], lastY * zoom + drawOffset[1]
            plotEnd = x * zoom + drawOffset[0], y * zoom + drawOffset[1]

            asymptoteCheck = (x > extremeLower and lastX < extremeUpper) or (lastX > extremeLower and x < extremeUpper)
            invalidNumberCheck = np.isnan(x) or np.isinf(x) or \
                                 np.isnan(y) or np.isinf(y) or \
                                 np.isnan(lastX) or np.isinf(lastX) or \
                                 np.isnan(lastY) or np.isinf(lastY)

            if not asymptoteCheck and not invalidNumberCheck:
                # pygame.draw.line(surface, equInstance.colour.faded, 
                #   (plotStart[0], plotStart[1] + 2), (x * zoom + drawOffset[0], screenSize[1]), 2)
                if dottedCheckLine > 0:
                    pygame.draw.line(surface, equInstance.colour.colour, plotStart, plotEnd, 3)
                
            if equInstance.isDottedLine:
                dottedCheckLine -= 1
                if dottedCheckLine < -9:
                    dottedCheckLine = 10
                    

            lastX, lastY = x, y

        surface = pygame.transform.flip(surface, False, True)
        return surface





    @staticmethod
    def GetLowHighValueXY(allPoints, length, high=True, forX=True):
        if len(allPoints) == 1:
            return allPoints
        elif len(allPoints) == 0:
            return [[]]

        newArray = allPoints[0]

        try:
            if forX:
                if high:
                    for i in range(length):
                        for current in range(1, allPoints):
                            if allPoints[current][i][0] > newArray[i][0]:
                                newArray[i][0] = allPoints[current][i][0]
                else:
                    for i in range(length):
                        for current in range(1, allPoints):
                            if allPoints[current][i][0] > newArray[i][0]:
                                newArray[i][0] = allPoints[current][i][0]
            else:
                if high:
                    for i in range(length):
                        for current in range(1, allPoints):
                            if allPoints[current][i][1] > newArray[i][1]:
                                newArray[i][1] = allPoints[current][i][1]
                else:
                    for i in range(length):
                        for current in range(1, allPoints):
                            if allPoints[current][i][1] > newArray[i][1]:
                                newArray[i][1] = allPoints[current][i][1]   
        except:
            pass     

        return newArray              





    def ConvertEquation(self):
        return self.equation


    def UpdateEquationType(self):
        self.type = STR_GRAPH_TYPES["="]
        for string in STR_GRAPH_TYPES.keys():
            if string in self.equation:
                self.type = STR_GRAPH_TYPES[string]
                break
        self.isDottedLine = self.type not in FULL_LINES




# Cluster of data inputted into the thread
class ThreadInput:
    def __init__(self, bounds, screenSize, zoomedOffset, equation):
        self.bounds = bounds
        self.screenSize = screenSize
        self.zoomedOffset = zoomedOffset
        self.equation = equation


# Cluster of data outputted from the thread
class ThreadOutput:
    def __init__(self, surface, bounds, zoomedOffset, null, solutions):
        self.bounds = bounds
        self.zoom = bounds.zoom
        self.zoomedOffset = zoomedOffset
        self.serialisedSurface = SerialisedSurface(surface, null)
        self.solutions = solutions


# Class that holds the produced surface and its bounds
class SurfaceAndBounds:
    def __init__(self, surface, bounds) -> None:
        self.surface = surface
        self.bounds = bounds
        self.zoom = bounds.zoom        

    def __str__(self) -> str:
        return f'''Surface: {self.surface}
Bounds: {self.bounds}
Zoom: {self.zoom}'''

                  
                            
