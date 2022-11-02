from colours import *
from numstr import *
from evaluate import *

import pygame
import math
import numpy as np
     

LOG_2 = math.log(2, 10)
LOG_4 = math.log(4, 10)


MAX_ZOOM = 1e6
MIN_ZOOM = 1e-8


class Graph:
    writtenValueGap = 70

    def __init__(self, screenSize):
        self.screenSize = screenSize
        self.screenCentre = (screenSize[0] // 2, screenSize[1] // 2)
        self.zoomedOffset = (0, 0)
        self.zoomedOffsetInverse = (0, 0)
        self.orgPos = (0, 0)

        self.offset = [0, 0]
        self.zoom = 50

        self.bounds = CornerValues(self)
        self.lastFrameData = None

        self.fonts = []
        self.AssignFonts()



    def AssignFonts(self):
        self.fonts.append(None)
        for i in range(40):
            self.fonts.append(pygame.font.Font("monofonto.otf", i))

        # self.fonts.append(pygame.font.Font("monofonto.otf", 16))
        # self.fonts.append(pygame.font.Font("monofonto.otf", 12))
        # self.fonts.append(pygame.font.Font("monofonto.otf", 10))



    def ScreenHasBeenResized(self, newSize, renderer):
        self.screenSize = newSize
        self.screenCentre = (newSize[0] // 2, newSize[1] // 2)
        renderer.surface = pygame.Surface(newSize)



    def PerformPrecalculation(self):
        # Cap the zoom between min and max
        if self.zoom > MAX_ZOOM:
            self.zoom = MAX_ZOOM
        elif self.zoom < MIN_ZOOM:
            self.zoom = MIN_ZOOM

        self.zoomedOffset = self.offset[0] * self.zoom, self.offset[1] * self.zoom
        self.zoomedOffsetInverse = self.offset[0] / self.zoom, self.offset[1] / self.zoom

        self.orgPos = self.screenCentre[0] - self.zoomedOffset[0], self.screenCentre[1] + self.zoomedOffset[1]

        # calculating the bounds of the window, accounting for zooms and offsets.
        # this is calculated similarly to how WritePosOnGraph() is calculated
        # this is executed in the __init__ function of the class CornerValues.
        self.bounds = CornerValues(self)


    def GetGraphLineIncrement(self):
        # Get how much the values increment by on the origin lines
        logarithm = math.log(self.zoom, 10)

        lineGap: float
        factorMultiplier: float

        zoomFactor = self.zoom
        while not 1 <= zoomFactor < 10:
            if zoomFactor >= 10:
                zoomFactor /= 10
            else:
                zoomFactor *= 10

        fractionalValue = math.fabs(logarithm + 100 - math.trunc(logarithm + 100))
        
        if fractionalValue >= LOG_4:
            factorMultiplier = 5
        elif fractionalValue >= LOG_2:
            factorMultiplier = 10
        else:
            factorMultiplier = 20
            
        lineGap = factorMultiplier * zoomFactor
        realGap = 10 ** math.trunc(-logarithm) * (lineGap / zoomFactor)

        if realGap <= 0:
            realGap = 10 ** math.trunc(-logarithm)

        return lineGap, realGap



    def DrawGraphLines(self, renderer):
        # Draw the cyan lines that stretch across the graph

        increment, realGap = self.GetGraphLineIncrement()
        lineOffset = [self.orgPos[0] % increment, self.orgPos[1] % increment]

        n = -increment

        while n < self.screenSize[0] + increment or n < self.screenSize[1] + increment:
            startX, endX = (n + lineOffset[0], -lineOffset[1]), (n + lineOffset[0], self.screenSize[1] + lineOffset[1])
            startY, endY = (-lineOffset[0], n + lineOffset[1]), (self.screenSize[0] + lineOffset[0], n + lineOffset[1])

            pygame.draw.line(renderer.surface, colours["cyan"].colour, startX, endX)
            pygame.draw.line(renderer.surface, colours["cyan"].colour, startY, endY)

            n += increment

        return SigFig(realGap, 1)



    def DrawCommonXYWordsOnAxis(self, renderer, realGap):
        realGap *= 2

        if self.zoom <= 1 and self.zoom != MIN_ZOOM:
            realGap *= 10

        # Draw the X values
        xStart = Graph.FindNearestMultiple(self.bounds.W[0], realGap)
        xEnd = Graph.FindNearestMultiple(self.bounds.E[0], realGap) 
        
        # error: real gap is zero

        for x in np.append(np.arange(xStart, xEnd, realGap), xEnd):
            if math.fabs(x) < realGap / 10:
                continue

            posX = -self.zoomedOffset[0] + self.screenCentre[0] + x * self.zoom
            posY = self.zoomedOffset[1] + self.screenCentre[1]     # y is always 0 at the origin

            txtSurface = self.fonts[10].render(f"{GetNumString(x, True)}", True, colours["black"].colour)
            posX -= txtSurface.get_width() / 2
            posY += 2

            renderer.surface.blit(txtSurface, (posX, posY))


        # Draw the Y values
        yStart = Graph.FindNearestMultiple(self.bounds.S[1], realGap)
        yEnd = Graph.FindNearestMultiple(self.bounds.N[1], realGap)   
        
        for y in np.append(np.arange(yStart, yEnd, realGap), yEnd):
            if math.fabs(y) < realGap / 10:
                continue

            posX = -self.zoomedOffset[0] + self.screenCentre[0]   # x is always 0 at the origin
            posY = self.zoomedOffset[1] + self.screenCentre[1] - y * self.zoom    

            txtSurface = self.fonts[10].render(f"{GetNumString(y, True)}", True, colours["black"].colour)
            posX += 3
            posY -= txtSurface.get_height() / 2

            renderer.surface.blit(txtSurface, (posX, posY))

        # print((xStart, xEnd), (yStart, yEnd), realGap)   





    def DrawLinesFromOrigin(self, renderer):
        orgPos = orgPosX, orgPosY = self.orgPos
        lines = [(orgPos, (0, orgPosY)), (orgPos, (self.screenSize[0], orgPosY)),
                 (orgPos, (orgPosX, 0)), (orgPos, (orgPosX, self.screenSize[1]))]

        orgPos = orgPosX, orgPosY  = orgPosX + 1, orgPosY + 1
        greyLines = [(orgPos, (0, orgPosY)), (orgPos, (self.screenSize[0], orgPosY)),
                     (orgPos, (orgPosX, 0)), (orgPos, (orgPosX, self.screenSize[1]))]

        for i, line in enumerate(lines):
            pygame.draw.line(renderer.surface, colours["black"].colour, line[0], line[1], 1)
            pygame.draw.line(renderer.surface, colours["grey"].colour, greyLines[i][0], greyLines[i][1], 1)


    def DrawZeroAtOrigin(self, renderer):
        txtSurface = self.fonts[16].render("0", True, colours["black"].colour)
        renderPos = list(self.orgPos)   # Convert to list so individual values can be changed
        renderPos[0] -= txtSurface.get_width() + 2

        renderer.surface.blit(txtSurface, tuple(renderPos))  # Convert back to tuple


    def DrawXAndYWords(self, renderer):
        txtSurfaceX = self.fonts[16].render("x", True, colours["black"].colour)
        txtSurfaceY = self.fonts[16].render("y", True, colours["black"].colour)

        orgPos = list(self.orgPos)
        renderPosX = (self.screenSize[0] - txtSurfaceX.get_width() - 2, orgPos[1])
        renderPosY = (orgPos[0] + 4, -4)
        
        renderer.surface.blit(txtSurfaceX, renderPosX)  
        renderer.surface.blit(txtSurfaceY, renderPosY)


    def DrawCircleAtTracedPoint(self, renderer, equation, mousePos):
        if mousePos is None or equation is None or equation.equation == "":
            return

        try:
            x = (self.zoomedOffset[0] - self.screenCentre[0] + mousePos[0]) / self.zoom
            y = eval(equation.equation)
            yOnGraph = self.zoomedOffset[1] + self.screenCentre[1] - y * self.zoom
            pygame.draw.circle(renderer.surface, equation.colour.colour, (mousePos[0], yOnGraph), 4)
        except:
            return     




    def DrawBaseGraphSurface(self, renderer, currentEquation, mousePos):
        self.screenCentre = [self.screenSize[0] // 2, self.screenSize[1] // 2]
        self.PerformPrecalculation()
        realGap = self.DrawGraphLines(renderer)
        self.DrawCommonXYWordsOnAxis(renderer, realGap)
        self.DrawLinesFromOrigin(renderer)
        self.DrawZeroAtOrigin(renderer)
        self.DrawXAndYWords(renderer)
        self.DrawCircleAtTracedPoint(renderer, currentEquation, mousePos)



        
    @staticmethod
    def FindNearestMultiple(number, multiple):
        if multiple == 0:
            return number
        return multiple * round(number / multiple)



class CornerValues:
    def __init__(self, graph):
        if graph is None:
            return

        # Lots of calculation required to draw the graphs and have them scale and pan properly.
        # All based of this formula: (offset * zoom - 0.5 * dimension + pos) / zoom

        x, y = 0, 1

        # Variables to make the calculations more readable in the code
        ox = graph.offset[0]
        oy = graph.offset[1]   # make this value negative
        z = graph.zoom
        maxX = graph.screenSize[0]
        maxY = graph.screenSize[1]
        bound = {x: (-maxX / 2, maxX / 2), y: (-maxY / 2, maxY / 2)}

        # Calculating once all possible X and Y values
        N = (oy * z - 0.5 * maxY - bound[y][0]) / z + graph.screenCentre[1] / z
        S = (oy * z - 0.5 * maxY - bound[y][1]) / z + graph.screenCentre[1] / z
        W = (ox * z - 0.5 * maxX + bound[x][0]) / z + graph.screenCentre[0] / z
        E = (ox * z - 0.5 * maxX + bound[x][1]) / z + graph.screenCentre[0] / z
        CENTRE_X = (ox * z - 0.5 * maxX) / z + graph.screenCentre[0] / z
        CENTRE_Y = (oy * z - 0.5 * maxY) / z + graph.screenCentre[1] / z

        # Putting together these values into x and y tuples
        self.CENTRE = CENTRE_X, CENTRE_Y
        self.N = CENTRE_X, N
        self.NE = E, N
        self.E = E, CENTRE_Y
        self.SE = E, S
        self.S = CENTRE_X, S
        self.SW = W, S
        self.W = W, CENTRE_Y
        self.NW = W, N
        self.zoom = z


    def __str__(self):
        return f'''*** CORNER VALUES ***
0) N:    {self.N}
1) NE:   {self.NE}
2) E:    {self.E}
3) SE:   {self.SE}
4) S:    {self.S}
5) SW:   {self.SW}
6) W:    {self.W}
7) NW:   {self.NW}
8) CNTR: {self.CENTRE}
9) Zoom: {self.zoom}
'''

    def ShortString(self):
        return f"{self.NW}, {self.SE}, {self.CENTRE}, {self.zoom}"


    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, CornerValues):
            if __o.NW == self.NW and __o.SE == self.SE:
                return True
        return False
