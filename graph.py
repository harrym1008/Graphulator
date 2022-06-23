import colours
import pygame
import deltatime

from standardform import *
from vector2 import *
from main import *

screenSize = [800, 600]
screenCentre = [400, 300]
zoomedOffset = [0, 0]
orgPos = [0, 0]

offset = [0, 0]
zoom = 2.5

font = None
clock = pygame.time.Clock()

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


def DrawGraphLines(surface):

    increment = 16 * zoom
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
    x, y = (pos[0] - screenCentre[0]) * zoom + zoomedOffset[0], (pos[1] - screenCentre[1]) * zoom + zoomedOffset[1]
    writtenPosition = f"{GetNumString(x)}, {GetNumString(y)}"

    txtSurface = font.render(writtenPosition, True, colours.PygameColour("blue"))
    surface.blit(txtSurface, (pos[0] - txtSurface.get_width()/2, pos[1] - 16))




def DrawAxis(surface):
    global screenCentre

    screenCentre = [screenSize[0] // 2, screenSize[1] // 2]
    surface.fill(colours.PygameColour("white"))
    CalculateBounds(surface)
    DrawGraphLines(surface)
    DrawXY(surface)

    DrawDebugText(surface)


def DrawDebugText(surface):
    textToRender = [
        f"{round(clock.get_fps(), 3)} FPS",
        f"Offset: {Vector2(offset[0], offset[1])}",
        f"Zoom: {GetNumString(zoom * 100)}%",
        f"Delta-time: {GetNumString(deltatime.deltaTime)}",
        f"Res: X:{screenSize[0]}, Y:{screenSize[1]}"
    ]

    for i, txt in enumerate(textToRender):
        txtSurface = font.render(txt, True, colours.PygameColour("blue"))
        surface.blit(txtSurface, (2, i * 16))


def CalculateBounds(surface):
    global bounds, zoomedOffset, orgPos
    zoomedOffset = offset[0] * zoom, offset[1] * zoom

    orgPosX, orgPosY = -zoomedOffset[0] + screenCentre[0], -zoomedOffset[1] + screenCentre[1]
    orgPos = [orgPosX, orgPosY]

    # txtSurface = font.render("(0, 0)", True, colours.PygameColour("blue"))
    # surface.blit(txtSurface, orgPos)


def CreateFont():
    global font
    font = pygame.font.SysFont("Consolas", 16)
