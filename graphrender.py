import pygame
from colours import *


# Holds the surface that the Graph class renders to
class GraphRenderer:
    def __init__(self, graph) -> None:
        self.surface = pygame.Surface(graph.screenSize)
        self.traceSurfaces = GraphRenderer.CreateTraceSurfaces(graph.screenSize)


    # Reset the surface
    def NewFrame(self):
        self.surface.fill(colours["white"].colour)


    # Run when the screen is resized
    def ScreenHasBeenResized(self, newSize):
        self.surface = pygame.Surface(newSize)
        self.traceSurfaces = GraphRenderer.CreateTraceSurfaces(newSize)


    # Produce surfaces for a transparent horizontal and vertical line    
    @staticmethod
    def CreateTraceSurfaces(screenSize):
        vertLine = pygame.Surface((screenSize[0], 1), pygame.SRCALPHA)
        vertLine.fill(colours["faded black"].colour)
        
        horzLine = pygame.Surface((1, screenSize[1]), pygame.SRCALPHA)
        horzLine.fill(colours["faded black"].colour)

        return (horzLine, vertLine)


        
