import math

import colours
import pygame
import deltatime

from numstr import *
from vector2 import *
from main import *

screenSize = [800, 600]
screenCentre = [400, 300]
zoomedOffset = [0, 0]
orgPos = [0, 0]

offset = [0, 0]
zoom = 1

font = None
clock = pygame.time.Clock()

LOG_2 = math.log(2, 10)
LOG_4 = math.log(4, 10)



'''bounds = {"high": [0, 0, 0],
          "mid": [0, 0, 0],
          "low": [0, 0, 0]}'''


# 1, 2, 3, 4, 5
# 2, 4, 6, 8, 10
# 5, 10, 15, 20, 25


def DrawXY(surface):
    global orgPos
    orgPosX, orgPosY = orgPos

    lines = [(orgPos, (0, orgPosY)), (orgPos, (screenSize[0], orgPosY)),
             (orgPos, (orgPosX, 0)), (orgPos, (orgPosX, screenSize[1]))]

    for line in lines:
        pygame.draw.line(surface, colours.PygameColour("black"), line[0], line[1], 2)


def GetGraphLineIncrement():
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
    increment = GetGraphLineIncrement()
    lineOffset = [orgPos[0] % increment, orgPos[1] % increment]

    n = -increment

    while n < screenSize[0] + increment or n < screenSize[1] + increment:
        startX, endX = (n + lineOffset[0], -lineOffset[1]), (n + lineOffset[0], screenSize[1] + lineOffset[1])
        startY, endY = (-lineOffset[0], n + lineOffset[1]), (screenSize[0] + lineOffset[0], n + lineOffset[1])

        pygame.draw.line(surface, colours.PygameColour("cyan"), startX, endX)
        pygame.draw.line(surface, colours.PygameColour("cyan"), startY, endY)

        n += increment


# Broken, please fix!
def WritePosOnGraph(pos, surface):
    if not pygame.mouse.get_focused():  # mouse is not focused on the window
        return

    # calculate co-ordinates of the mouse position
    x = -(pos[0] - screenCentre[0]) / zoom - offset[0] / zoom
    y = -(pos[1] - screenCentre[1]) / zoom - offset[1] / zoom

    writtenPosition = GetCoordString(x, y)

    txtSurface = font.render(writtenPosition, True, colours.PygameColour("blue"))

    renderX = pos[0] - txtSurface.get_width() / 2 - 4
    renderY = pos[1] - 18

    if renderX < 0:
        renderX = 0
    elif renderX > screenSize[0] - txtSurface.get_width():
        renderX = screenSize[0] - txtSurface.get_width()  #

    if renderY < 0:
        renderY = 0

    surface.blit(txtSurface, (renderX, renderY))


def DrawAxis(surface):
    global screenCentre

    screenCentre = [screenSize[0] // 2, screenSize[1] // 2]
    surface.fill(colours.PygameColour("white"))
    PreCalculation(surface)
    DrawGraphLines(surface)
    DrawXY(surface)

    DrawDebugText(surface)


def DrawDebugText(surface):
    textToRender = [
        f"{round(clock.get_fps(), 3)} FPS",
        f"Offset: {Vector2(offset[0], offset[1])}",
        f"Zoom: {SigFig(zoom * 100, 5)}%",
        f"Deltatime: {GetNumString(deltatime.deltaTime)}",
        f"Res: X:{screenSize[0]}, Y:{screenSize[1]}"
    ]

    for i, txt in enumerate(textToRender):
        txtSurface = font.render(txt, True, colours.PygameColour("blue"))
        surface.blit(txtSurface, (2, i * 16))


def PreCalculation(surface):
    global zoomedOffset, orgPos
    zoomedOffset = offset[0] * zoom, offset[1] * zoom

    orgPosX, orgPosY = -zoomedOffset[0] + screenCentre[0], -zoomedOffset[1] + screenCentre[1]
    orgPos = [orgPosX, orgPosY]


def CreateFont():
    global font
    font = pygame.font.SysFont("Consolas", 16)
