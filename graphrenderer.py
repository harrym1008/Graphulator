import pygame
from colours import *


class GraphRenderer:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.surface = pygame.Surface(graph.screenSize)

    def NewFrame(self):
        self.surface.fill(colours["white"].colour)
