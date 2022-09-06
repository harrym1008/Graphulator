from colours import *
import pygame
import math
import ui
     

LOG_2 = math.log(2, 10)
LOG_4 = math.log(4, 10)


fonts = []


def AssignFonts():
    global fonts
    fonts = [pygame.font.Font("monofonto.otf", 16), pygame.font.Font("monofonto.otf", 12)]


class Graph:
    writtenValueGap = 70


    def __init__(self, screenSize):
        self.screenSize = screenSize
        self.screenCentre = (screenSize[0] // 2, screenSize[1] // 2)
        self.zoomedOffset = (0, 0)
        self.zoomedOffsetInverse = (0, 0)
        self.orgPos = (0, 0)

        self.offset = [0, 0]
        self.zoom = 30

        self.bounds = CornerValues(self)
        self.lastFrameData = None

        self.baseSurface = pygame.Surface(screenSize)


    def ScreenHasBeenResized(self, newSize):
        self.screenSize = newSize
        self.screenCentre = (newSize[0] // 2, newSize[1] // 2)
        self.baseSurface = pygame.Surface(newSize)


    def IsPrecalcNecessary(self):
        if self.lastFrameData is None:
            return True

        newObject = LastFrameData(self)
        necessary = newObject != self.lastFrameData
        self.lastFrameData = newObject
        return necessary


    def PerformPrecalculation(self):
        if not self.IsPrecalcNecessary():
            return

        self.zoomedOffset = self.offset[0] * self.zoom, self.offset[1] * self.zoom
        self.zoomedOffsetInverse = self.offset[0] / self.zoom, self.offset[1] / self.zoom

        self.orgPos = self.screenCentre[0] - self.zoomedOffset[0], self.screenCentre[1] - self.zoomedOffset[1]

        # calculating the bounds of the window, accounting for zooms and offsets.
        # this is calculated similarly to how WritePosOnGraph() is calculated
        # this is executed in the __init__ function of the class CornerValues.
        self.bounds = CornerValues(self)


    def GetGraphLineIncrement(self):
        # Get how much the values increment by on the origin lines
        logarithm = math.log(self.zoom, 10)

        factor = self.zoom
        while not 1 <= factor < 10:
            if factor >= 10:
                factor /= 10
            else:
                factor *= 10

        fractionalValue = math.fabs(logarithm + 100 - math.trunc(logarithm + 100))

        if fractionalValue >= LOG_4:
            return 5 * factor
        elif fractionalValue >= LOG_2:
            return 10 * factor
        else:
            return 20 * factor



    def DrawGraphLines(self):
        # Draw the cyan lines that stretch across the graph

        increment = self.GetGraphLineIncrement()
        lineOffset = [self.orgPos[0] % increment, self.orgPos[1] % increment]

        n = -increment

        while n < self.screenSize[0] + increment or n < self.screenSize[1] + increment:
            startX, endX = (n + lineOffset[0], -lineOffset[1]), (n + lineOffset[0], self.screenSize[1] + lineOffset[1])
            startY, endY = (-lineOffset[0], n + lineOffset[1]), (self.screenSize[0] + lineOffset[0], n + lineOffset[1])

            pygame.draw.line(self.baseSurface, colours["cyan"].colour, startX, endX)
            pygame.draw.line(self.baseSurface, colours["cyan"].colour, startY, endY)

            n += increment


    def WriteGraphValues(self):
        # Write X and Y values on the screen at regular intervals
        # Draw X values
        
        pos = [self.screenCentre[0] - self.zoomedOffset[0], self.screenCentre[1] - self.zoomedOffset[1]]
        extents = [(-self.screenSize[0] * Graph.writtenValueGap) // 2, (self.screenSize[0] * Graph.writtenValueGap) // 2,
                   (-self.screenSize[1] * Graph.writtenValueGap) // 2, (self.screenSize[1] * Graph.writtenValueGap) // 2]

        pos[0] = sorted((0, pos[0], self.screenSize[0]))[1]     # Code snippet to clamp pos[0] to a certain range
        pos[1] = sorted((0, pos[1], self.screenSize[1]))[1]     # Code snippet to clamp pos[1] to a certain range

        '''for i in range(extents[0], extents[1], 100):
            number = i / zoom
            if number == 0:
                continue
            txtSurface = smallFont.render(GetNumString(number, True), True, colours.PygameColour("black"))

            if pos[1] + 2 + txtSurface.get_height() > screenSize[1]:
                surface.blit(txtSurface, (pos[0] + i - txtSurface.get_width() / 2, screenSize[1] - txtSurface.get_height()))
                continue

            surface.blit(txtSurface, (pos[0] + i - txtSurface.get_width() / 2, pos[1] + 2))
            pygame.draw.line(surface, colours.PygameColour("black"),
                            (pos[0] + i, pos[1] - 1),
                            (pos[0] + i, pos[1] - 4))

        # draw Y values

        for i in range(extents[2], extents[3], 100):
            number = -i / zoom
            if number == 0:
                continue
            txtSurface = smallFont.render(GetNumString(number, True), True, colours.PygameColour("black"))

            if pos[0] + 2 + txtSurface.get_width() > screenSize[0]:
                surface.blit(txtSurface, (screenSize[0] - txtSurface.get_width(), pos[1] + i - txtSurface.get_height() / 2))
                continue

            surface.blit(txtSurface, (pos[0] + 2, pos[1] + i - txtSurface.get_height() / 2))
            pygame.draw.line(surface, colours.PygameColour("black"),
                            (pos[0] - 1, pos[1] + i),
                            (pos[0] - 4, pos[1] + i))

        txtSurface = smallFont.render("0", True, colours.PygameColour("black"))

        surface.blit(txtSurface, (orgPos[0] - 10, orgPos[1]))'''


    def DrawLinesFromOrigin(self):
        orgPos = orgPosX, orgPosY = self.orgPos

        lines = [(orgPos, (0, orgPosY)), (orgPos, (self.screenSize[0], orgPosY)),
                 (orgPos, (orgPosX, 0)), (orgPos, (orgPosX, self.screenSize[1]))]

        for line in lines:
            pygame.draw.line(self.baseSurface, colours["black"].colour, line[0], line[1], 2)



    def DrawBaseGraphSurface(self):
        self.screenCentre = [self.screenSize[0] // 2, self.screenSize[1] // 2]
        self.baseSurface.fill(colours["white"].colour)

        self.PerformPrecalculation()
        self.DrawGraphLines()
        self.DrawLinesFromOrigin()
        self.WriteGraphValues()
        ui.DrawDebugDataOnGraphScreen(self, fonts[0])


    def UpdateScreenSize(self, newSize):
        self.screenSize = newSize


        

class LastFrameData:
    def __init__(self, graph):
        self.offsetX = graph.offset[0]
        self.offsetY = graph.offset[1]
        self.zoom = graph.zoom

    def __eq__(self, other):
        if other is None:
            return True
        return self.offsetX == other.offsetX and self.offsetY == other.offsetY and self.zoom == other.zoom


class CornerValues:
    def __init__(self, graph):
        # Lots of calculation required to draw the graphs and have them scale and pan properly.
        # All based of this formula: (offset * zoom - 0.5 * dimension + pos) / zoom

        x, y = 0, 1

        # Variables to make the calculations more readable in the code
        ox = graph.offset[0]
        oy = graph.offset[1]
        z = graph.zoom
        maxX = graph.screenSize[0]
        maxY = graph.screenSize[1]
        bound = {x: (-maxX / 2, maxX / 2), y: (-maxY / 2, maxY / 2)}

        # Calculating once all possible X and Y values
        S = (oy * z - 0.5 * maxY - bound[y][0]) / z + graph.screenCentre[1] / z
        N = (oy * z - 0.5 * maxY - bound[y][1]) / z + graph.screenCentre[1] / z
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

    def GetTuple(self):
        return self.N, self.NE, self.E, self.SE, self.S, self.SW, self.W, self.NW, self.CENTRE

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
'''
