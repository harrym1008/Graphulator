import colours
import main
import pygame
from vector2 import *

screenSize = [800, 600]
screenCentre = [400, 300]

offset = [0, 0]
zoom = 10

font = None
clock = pygame.time.Clock()
bounds = []


# 1, 2, 3, 4, 5
# 2, 4, 6, 8, 10
# 5, 10, 15, 20, 25


def DrawXY(surface):
    zoomedOffset = offset[0] * zoom, offset[1] * zoom

    drawCentre = 0 - zoomedOffset[0] + screenCentre[0], 0 - zoomedOffset[1] + screenCentre[1]

    maxLineEdges = [
        (0, drawCentre[1]),
        (screenSize[0], drawCentre[1]),
        (drawCentre[0], 0),
        (drawCentre[0], screenSize[1])
    ]

    for end in maxLineEdges:
        pygame.draw.line(surface, colours.PygameColour("black"), drawCentre, end, width=3)


def DrawGraphLines(surface):
    zoomedOffset = Vector2(offset[0] * zoom, offset[1] * zoom)

    for row in range(-12, 28):
        start = Vector2(0, row * (screenSize[0] / 16)) - zoomedOffset
        end = Vector2(screenSize[1], row * (screenSize[0] / 16)) - zoomedOffset

        pygame.draw.line(surface, colours.PygameColour("black"), start.Tuple(), end.Tuple())








def DrawAxis(surface):
    global screenCentre

    screenCentre = [screenSize[0] // 2, screenSize[1] // 2]
    surface.fill(colours.PygameColour("white"))
    DrawXY(surface)
    DrawGraphLines(surface)

    DrawDebugText(surface)


def DrawDebugText(surface):
    textToRender = [
        f"{round(clock.get_fps(), 3)} FPS",
        f"Offset: {Vector2(offset[0], offset[1])}",
        f"Zoom: {zoom}"
    ]

    for i, txt in enumerate(textToRender):
        txtSurface = font.render(txt, True, colours.PygameColour("red"))
        surface.blit(txtSurface, (0, i * 20))


def CreateFont():
    global font
    font = pygame.font.SysFont("Consolas", 20)