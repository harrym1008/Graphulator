import math

import colours
import pygame
import drawfunc
import main

from numstr import *
from vector2 import *
from main import *

screenSize = [800, 600]
screenCentre = [400, 300]
zoomedOffset = [0, 0]
zoomedOffsetInverse = [0, 0]
orgPos = [0, 0]

offset = [0, 0]
zoom = 30

mainFont = smallFont = tinyFont = None

clock = pygame.time.Clock()

LOG_2 = math.log(2, 10)
LOG_4 = math.log(4, 10)


# 1, 2, 3, 4, 5
# 2, 4, 6, 8, 10
# 5, 10, 15, 20, 25


class LastFrameData:
    def __init__(self, offsetX, offsetY, zoom):
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.zoom = zoom

    def __eq__(self, other):
        if other is None:
            return True
        return self.offsetX == other.offsetX and self.offsetY == other.offsetY and self.zoom == other.zoom


class CornerValues:
    def __init__(self, offset, zoom):
        # Lots of calculation required to draw the graphs and have them scale and pan properly.
        # All based of this formula: (offset * zoom - 0.5 * dimension + pos) / zoom

        x, y = 0, 1

        # Variables to make the calculations more readable in the code
        ox = offset[0]
        oy = offset[1]
        z = zoom
        maxX = screenSize[0]
        maxY = screenSize[1]
        bound = {x: (-maxX / 2, maxX / 2), y: (-maxY / 2, maxY / 2)}

        # Calculating once all possible X and Y values
        S = (oy * z - 0.5 * maxY - bound[y][0]) / z + screenCentre[1] / z
        N = (oy * z - 0.5 * maxY - bound[y][1]) / z + screenCentre[1] / z
        W = (ox * z - 0.5 * maxX + bound[x][0]) / z + screenCentre[0] / z
        E = (ox * z - 0.5 * maxX + bound[x][1]) / z + screenCentre[0] / z
        CENTRE_X = (ox * z - 0.5 * maxX) / z + screenCentre[0] / z
        CENTRE_Y = (oy * z - 0.5 * maxY) / z + screenCentre[1] / z

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


bounds = CornerValues(offset, zoom)
lastFrameData = None


def CheckIfPreCalculationIsNecessary():
    # Checks if any variables have changed, if not it is not necessary to recalculate the data
    # and stress the system further

    global lastFrameData

    if lastFrameData is None:
        return True

    newObject = LastFrameData(offset[0], offset[1], zoom)
    necessary = newObject != lastFrameData
    lastFrameData = newObject
    return necessary


def DrawXY(surface):
    # Draws the thicker main lines from the origin
    global orgPos
    orgPosX, orgPosY = orgPos

    lines = [(orgPos, (0, orgPosY)), (orgPos, (screenSize[0], orgPosY)),
             (orgPos, (orgPosX, 0)), (orgPos, (orgPosX, screenSize[1]))]

    for line in lines:
        pygame.draw.line(surface, colours.PygameColour("black"), line[0], line[1], 2)


def GetGraphLineIncrement():
    # Get how much the values increment by on the origin lines
    logarithm = math.log(zoom, 10)

    factor = zoom
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


def DrawGraphLines(surface):
    # Draw the cyan lines across the screen to represent the graph

    increment = GetGraphLineIncrement()
    lineOffset = [orgPos[0] % increment, orgPos[1] % increment]

    n = -increment

    while n < screenSize[0] + increment or n < screenSize[1] + increment:
        startX, endX = (n + lineOffset[0], -lineOffset[1]), (n + lineOffset[0], screenSize[1] + lineOffset[1])
        startY, endY = (-lineOffset[0], n + lineOffset[1]), (screenSize[0] + lineOffset[0], n + lineOffset[1])

        pygame.draw.line(surface, colours.PygameColour("cyan"), startX, endX)
        pygame.draw.line(surface, colours.PygameColour("cyan"), startY, endY)

        n += increment


def WriteGraphValues(surface):
    # Write X and Y values on the screen at regular intervals
    # draw X values
    pos = [screenCentre[0] - zoomedOffset[0], screenCentre[1] - zoomedOffset[1]]

    extents = [(-screenSize[0] * 70) // 2, (screenSize[0] * 70) // 2,
               (-screenSize[1] * 70) // 2, (screenSize[1] * 70) // 2]

    if pos[0] < 0:
        pos[0] = 0
    elif pos[0] > screenSize[0]:
        pos[0] = screenSize[0]

    if pos[1] < 0:
        pos[1] = 0
    elif pos[1] > screenSize[1]:
        pos[1] = screenSize[1]

    for i in range(extents[0], extents[1], 100):
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

    surface.blit(txtSurface, (orgPos[0] - 10, orgPos[1]))


def WritePosOnGraph(pos, surface, focusTime):
    # Writes the position of the mouse cursor on the graph

    if focusTime < 0:  # mouse is not focused on the window
        return

    # Calculate co-ordinates of the mouse position
    # x = (pos[0] / screenSize[0] - 0.5) * screenSize[0] / zoom + offset[0]
    # y = -(pos[1] / screenSize[1] - 0.5) * screenSize[1] / zoom + offset[1]

    # Simplified:
    x = (offset[0] * zoom - 0.5 * screenSize[0] + pos[0]) / zoom
    y = (-offset[1] * zoom + 0.5 * screenSize[1] - pos[1]) / zoom

    writtenPosition = GetCoordString(x, y)

    txtSurface = mainFont.render(writtenPosition, True, colours.PygameColour("blue"))

    renderX = pos[0] - txtSurface.get_width() / 2 - 4
    renderY = pos[1] - 32

    if renderX < 0:
        renderX = 0
    elif renderX > screenSize[0] - txtSurface.get_width():
        renderX = screenSize[0] - txtSurface.get_width()  #

    if renderY < 0:
        renderY = pos[1] + 16

    pygame.draw.rect(surface, colours.WHITE_BOX,
                     pygame.Rect(renderX, renderY, txtSurface.get_width(), txtSurface.get_height()))
    surface.blit(txtSurface, (renderX, renderY))

    '''
    writtenPosition = [f"x={GetNumString(x, True)}", f"y={GetNumString(y, True)}"]

    txtSurfaceX = smallFont.render(writtenPosition[0], True, colours.PygameColour("blue"))
    txtSurfaceY = smallFont.render(writtenPosition[1], True, colours.PygameColour("blue"))

    largerWidth = txtSurfaceX.get_width() if txtSurfaceX.get_width() > txtSurfaceY.get_width() else txtSurfaceY.get_width()
    renderX = pos[0] - 4 - txtSurfaceX.get_width() / 2
    renderY = pos[1] - 40

    if renderX < 0:
        renderX = 0
    elif renderX > screenSize[0] - largerWidth:
        renderX = screenSize[0] - largerWidth

    if renderY < 0:
        renderY = pos[1] + 16

    pygame.draw.rect(surface, colours.WHITE_BOX,
                     pygame.Rect(renderX, renderY, largerWidth, txtSurfaceX.get_height() + txtSurfaceY.get_height()))

    surface.blit(txtSurfaceX, (renderX, renderY))
    surface.blit(txtSurfaceY, (renderX, renderY + txtSurfaceY.get_height()))'''


def DrawAxis(surface, timeToExec):
    # Main function calling all others to draw graph lines, debug data and values

    global screenCentre

    screenCentre = [screenSize[0] // 2, screenSize[1] // 2]
    surface.fill(colours.PygameColour("white"))
    PreCalculation(surface)

    drawfunc.UpdateValues(screenSize, screenCentre, zoomedOffset, zoomedOffsetInverse,
                          orgPos, offset, zoom, [entry.get() for entry in main.equEntries], bounds)

    DrawGraphLines(surface)
    DrawXY(surface)
    WriteGraphValues(surface)

    DebugStuff(surface, timeToExec)


def DebugStuff(surface, timeToExec):
    # Stuff required for debugging the code

    '''for i, (x, y) in enumerate(bounds.GetTuple()):
        drawAt = x * zoom - zoomedOffset[0] + screenCentre[0], y * zoom - zoomedOffset[1] + screenCentre[1]
        pygame.draw.circle(surface, colours.PygameColour("green"), drawAt, 16)

        txt = mainFont.render(f"{round(x, 1)},{round(y, 1)}", True, colours.PygameColour("black"))
        surface.blit(txt, (drawAt[0] - txt.get_width()/2, drawAt[1] - txt.get_height()/2))'''

    textToRender = [
        f"{round(clock.get_fps(), 3)} FPS",
        f"Offset: {Vector2(offset[0], offset[1])}",
        f"Zoom: {SigFig(zoom * 100, 5)}%",
        f"Deltatime: {GetNumString(deltatime.deltaTime)}",
        f"Res: X:{screenSize[0]}, Y:{screenSize[1]}",
        f"Execution: {GetNumString(timeToExec * 1000)} ms"
    ]

    for i, txt in enumerate(textToRender):
        txtSurface = mainFont.render(txt, True, colours.PygameColour("blue"))
        surface.blit(txtSurface, (2, i * 16))

    '''for i, txt in enumerate(str(bounds).split("\n")):
        txtSurface = mainFont.render(txt, True, colours.PygameColour("red"))
        surface.blit(txtSurface, (2, 100 + i * 16))'''


def PreCalculation(surface):
    global zoomedOffset, zoomedOffsetInverse, orgPos, bounds

    if not CheckIfPreCalculationIsNecessary():
        return

    zoomedOffset = offset[0] * zoom, offset[1] * zoom
    zoomedOffsetInverse = offset[0] / zoom, offset[1] / zoom

    orgPosX, orgPosY = -zoomedOffset[0] + screenCentre[0], -zoomedOffset[1] + screenCentre[1]
    orgPos = [orgPosX, orgPosY]

    # calculating the bounds of the window, accounting for zooms and offsets.
    # this is calculated similarly to how WritePosOnGraph() is calculated
    # this is executed in the __init__ function of the class CornerValues.

    bounds = CornerValues(offset, zoom)


def CreateFont():
    # Generate the fonts
    # This is executed at the beginning of the script, this is because creating a font in Pygame
    # is quite a time-consuming process, so this is done first and then stored in a global variable

    global mainFont, smallFont, tinyFont
    mainFont = pygame.font.Font("monofonto.otf", 16)
    smallFont = pygame.font.Font("monofonto.otf", 12)
    # tinyFont = pygame.font.Font("monofonto.otf", 10)
