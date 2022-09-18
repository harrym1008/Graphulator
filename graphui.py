import pygame
import graph
from colours import *
from numstr import *


class GraphUserInterface:
    def __init__(self, screenSize):
        self.screenSize = screenSize
        self.surface = pygame.Surface(screenSize, pygame.SRCALPHA, 32)
        self.surface = self.surface.convert_alpha()


    def ClearUISurface(self):
        self.surface.fill(colours["transparent"].colour)


    def ScreenHasBeenResized(self, newSize):
        self.surface = pygame.Surface(newSize, pygame.SRCALPHA, 32)
        self.screenSize = newSize


    def UpdateUISurface(self, font, graph, clock, mousePos):
        self.ClearUISurface()
        self.TopRightDebugData(font, graph, clock)
        self.WriteMousePosition(font, mousePos, graph)

    
    def WriteMousePosition(self, font, mousePos, graph):
        if mousePos is None:  # mouse is not focused on the window
            return

        # Calculate co-ordinates of the mouse position
        # x = (pos[0] / screenSize[0] - 0.5) * screenSize[0] / zoom + offset[0]
        # y = -(pos[1] / screenSize[1] - 0.5) * screenSize[1] / zoom + offset[1]

        # Simplified:
        x = (graph.offset[0] * graph.zoom - 0.5 * self.screenSize[0] + mousePos[0]) / graph.zoom
        y = (-graph.offset[1] * graph.zoom + 0.5 * self.screenSize[1] - mousePos[1]) / graph.zoom

        writtenPosition = GetCoordString(x, y)

        txtSurface = font.render(writtenPosition, True, colours["blue"].colour)

        renderX = mousePos[0] - txtSurface.get_width() / 2 - 4
        renderY = mousePos[1] - 32

        if renderX < 0:
            renderX = 0
        elif renderX > self.screenSize[0] - txtSurface.get_width():
            renderX = self.screenSize[0] - txtSurface.get_width()  #

        if renderY < 0:
            renderY = mousePos[1] + 16

        pygame.draw.rect(self.surface, colours["white"].colour,
                         pygame.Rect(renderX, renderY, txtSurface.get_width(), txtSurface.get_height()))
        self.surface.blit(txtSurface, (renderX, renderY))



    def TopRightDebugData(self, font, graph, clock):
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