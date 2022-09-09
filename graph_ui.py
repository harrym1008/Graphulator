import pygame
import graph as _graph
from colours import *
from numstr import *


class GraphUserInterface:
    def __init__(self, screenSize):
        self.screenSize = screenSize
        self.surface = pygame.Surface(screenSize, pygame.SRCALPHA, 32)
        self.surface = self.surface.convert_alpha()


    def ClearUISurface(self):
        self.surface.fill(colours["transparent"].colour)

    def UpdateScreenSize(self, newSize):
        self.screenSize = newSize

    def UpdateUISurface(self, font, graph, clock):
        self.ClearUISurface()
        fps = clock.get_fps()
        frametime = 1/fps if fps != 0 else 0
        # Check to make sure the program will not divide by zero on the first frame
        # ---> fps returns 0 on frame 1

        textToRender = [
            f"{round(fps, 3)} FPS",
            f"Offset: x={GetNumString(graph.offset[0])}, y={GetNumString(graph.offset[1])}",
            f"Zoom: {SigFig(graph.zoom * 100, 5)}%",
            f"Deltatime: {GetNumString(frametime)}",
            f"Res: X:{self.screenSize[0]}, Y:{self.screenSize[1]}",
        ]  # List of text to render on the screen

        for i, txt in enumerate(textToRender):
            rendered = font.render(txt, True, colours["blue"].colour)
            self.surface.blit(rendered, (2, i*16))
            # create surface of the text and blit it onto the surface