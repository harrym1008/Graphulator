from typing import List

import pygame
import numpy as np
import drawfunc


class FunctionManager:
    def __init__(self, graph):
        self.currentEquations: List[drawfunc.PlottedEquation] = []
        self.surfaceBoundsData: List[drawfunc.SurfaceWithBounds] = []
        self.surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)


    def UpdateSurface(self, graph):
        for i, data in enumerate(self.surfaceBoundsData):
            if self.currentEquations[i].equation == "":
                continue

            newPosition = (0, 0)
            tempSurface = pygame.Surface(graph.screenSize, pygame.SRCALPHA)

            if data.bounds.NW != graph.bounds.NW or data.bounds.zoom != graph.zoom:
                if data.bounds.NW != data.bounds.NW:
                    newPosition = np.subtract(tuple([graph.zoom * x for x in graph.bounds.NW]), graph.zoomedOffset)

                zoomScalar = graph.zoom / data.bounds.zoom
                newScale = tuple([zoomScalar * x for x in graph.screenSize])
                tempSurface = pygame.transform.scale(data.surface, newScale)

            self.surface.blit(data.surface, newPosition)


    def UpdateThreads(self):
        for
