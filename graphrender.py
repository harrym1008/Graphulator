import pygame
from colours import *


class GraphRenderer:
    def __init__(self, graph) -> None:
        self.surface = pygame.Surface(graph.screenSize)
        self.traceSurfaces = GraphRenderer.CreateTraceSurfaces(graph.screenSize)


    def NewFrame(self):
        self.surface.fill(colours["white"].colour)


    def ScreenHasBeenResized(self, newSize):
        self.surface = pygame.Surface(newSize)
        self.traceSurfaces = GraphRenderer.CreateTraceSurfaces(newSize)


    
    @staticmethod
    def CreateTraceSurfaces(screenSize):
        vertLine = pygame.Surface((screenSize[0], 1), pygame.SRCALPHA)
        vertLine.fill(colours["faded black"].colour)
        
        horzLine = pygame.Surface((1, screenSize[1]), pygame.SRCALPHA)
        horzLine.fill(colours["faded black"].colour)

        # for i in range(0, screenSize[0], 2):
        #     verticalLine.set_at((i, 0), colours["black"].colour)

        return (horzLine, vertLine)


        
