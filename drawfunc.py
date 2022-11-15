import numpy as np
import pygame
import colours
import time

from evaluate import *
from serialsurf import SerialisedSurface
from graph import CornerValues
from enum import IntEnum


INCREMENT_FACTOR = 1.5
ANTIALIAS = False


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

        n = self.index + 1
        
        while True:
            # wait for the in queue to have a length of 1 (this means data is present)
            startTime = time.perf_counter()

            while inQueue.qsize() < 1:
                time.sleep(0.05)

            # Get equation events (how the equation has changed so the thread can be updated)
            forceUpdate = False
            while eventQueue.qsize() > 0:
                forceUpdate = True
                event = eventQueue.get()
                if event.type == 0:
                    currentEquation = event.data
                

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

            start, end = bounds.W, bounds.E
            incrementY = (end[0] - start[0]) / (bounds.screenSize[0] * INCREMENT_FACTOR)
            incrementX = (end[0] - start[0]) / (bounds.screenSize[1] * INCREMENT_FACTOR)

            # Compute all the points on the graph
            if (not skipNoEquation and not skipSameBounds) or (not skipNoEquation and forceUpdate):
                # Loop through all Y solutions
                for i, solution in enumerate(solutions["y"]):
                    yPoints.append([])
                    for x in np.arange(start[0], end[0], incrementY):
                        try:
                            yPoints[i].append((x, float( eval(solution) )))  #GetYValue(x, currentEquation) )))
                        except Exception as e:
                            yPoints[i].append((x, np.inf))
                            
                # Loop through all X solutions
                for i, solution in enumerate(solutions["x"]):
                    xPoints.append([])
                    for y in np.arange(start[0], end[0], incrementX):
                        try:
                            xPoints[i].append((float( eval(solution)), y ))  #GetYValue(x, currentEquation) ))
                        except Exception as e:
                            xPoints[i].append((np.inf, y))
                points = yPoints + xPoints
                savedPoints = points
            elif not skipNoEquation and skipSameBounds:
                points = savedPoints


            surface: pygame.Surface


            # Produce a pygame surface from the points just calculated
            if solutionCount == 1:

                if len(solutions["y"]) == 1:
                    surface = PlottedEquation.DrawSurfaceFromArray_YEquals(points[0], 
                                inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize )
                elif len(solutions["x"]) == 1:
                    surface = PlottedEquation.DrawSurfaceFromArray_XEquals(points[0], 
                                inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize )
            else:
                surface = pygame.Surface(inData.screenSize, pygame.SRCALPHA)
                if solutionCount > 1:
                    for i in range(solutionCount):
                        isYEquals = i < len(solutions["y"])
                        if isYEquals:
                            tempSurface = PlottedEquation.DrawSurfaceFromArray_YEquals(points[i], 
                                        inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize)
                        else:
                            tempSurface = PlottedEquation.DrawSurfaceFromArray_XEquals(points[i], 
                                        inData.equation, inData.bounds, inData.zoomedOffset, inData.screenSize)

                        surface.blit(tempSurface, (0, 0))


            # Place into a class of thread output data
            outData = ThreadOutput(surface, bounds, inData.zoomedOffset, skipNoEquation, solutions["y"])

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

        if lhs == "x" or rhs == "x":
            return {"y": empty,"x": xS}
        if lhs == "y" or rhs == "y":
            return {"y": yS,"x": empty}
        return {"y": yS, "x": xS}


    @staticmethod
    def ProduceEquationSolutions(equ, category):
        x, y = sp.symbols("x y")
        try:
            solveFor = x if category == "x" else y
            solved = sp.solve(equ, solveFor)
            print(solved)
            return [ReplaceEquation(str(solution)) for solution in solved]
        except:
            return []


    @staticmethod
    def ProduceSympyEquation(strEqu, getHandSides=True):
        y = sp.symbols("y")
        returns = None, "", ""
        
        try:
            sides = strEqu.split("=")

            if len(sides) == 2:
                lhs, rhs = tuple(sp.sympify(side) for side in sides)
            elif len(sides) == 1:
                lhs, rhs = y, sp.sympify(sides[0])
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
            invalidNumberCheck = y in [np.inf, np.NINF, np.nan] or \
                                 x in [np.inf, np.NINF, np.nan] or \
                                 lastY in [np.inf, np.NINF, np.nan] or \
                                 lastX in [np.inf, np.NINF, np.nan]

            if invalidNumberCheck:
                continue

            if not asymptoteCheck and not invalidNumberCheck:
                # pygame.draw.line(surface, equInstance.colour.faded, 
                #  (plotStart[0], plotStart[1] + 2), (x * zoom + drawOffset[0], screenSize[1]), 2)
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
            invalidNumberCheck = y in [np.inf, np.NINF, np.nan] or \
                                 x in [np.inf, np.NINF, np.nan] or \
                                 lastY in [np.inf, np.NINF, np.nan] or \
                                 lastX in [np.inf, np.NINF, np.nan]

            if invalidNumberCheck:
                continue

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




    def ConvertEquation(self):
        return self.equation


    def UpdateEquationType(self):
        self.type = strToGraphType["="]
        for string in strToGraphType.keys():
            if string in self.equation:
                self.type = strToGraphType[string]
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

                  
                            
