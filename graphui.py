import pygame
import numpy as np

from colours import *
from numstr import *
from evaluate import *


class GraphUserInterface:
    def __init__(self, graph):
        self.screenSize = graph.screenSize
        self.surface = pygame.Surface(graph.screenSize, pygame.SRCALPHA, 32)
        self.surface = self.surface.convert_alpha()

        self.fonts = graph.fonts

        self.lastFrame = time.perf_counter()
        self.frameRates = []
        self.maxFrameRates = 240


    def ClearUISurface(self):
        self.surface.fill(colours["transparent"].colour)


    def ScreenHasBeenResized(self, newSize):
        self.surface = pygame.Surface(newSize, pygame.SRCALPHA, 32)
        self.screenSize = newSize


    def UpdateUISurface(self, graph, mousePos, equation):
        self.ClearUISurface()
        self.TopRightDebugData(graph)
        x = self.WriteMousePosition(mousePos, graph)
        self.DrawCurrentEquationXY(equation, x)
        self.DrawFramerateGraph()
        


    
    def WriteMousePosition(self, mousePos, graph):
        if mousePos is None:  # mouse is not focused on the window
            return np.inf

        font = self.fonts[12]

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

        return x



    def TopRightDebugData(self, graph):
        font = self.fonts[20]
        # Check to make sure the program will not divide by zero on the first frame
        # ---> fps returns 0 on frame 1

        textToRender = [
            f"X = {GetNumString(graph.offset[0])}",
            f"Y = {GetNumString(graph.offset[1])}",
            f"Zoom: {SigFig(graph.zoom * 100, 5)}%"
        ]  # List of text to render on the screen

        for i, txt in enumerate(textToRender):
            rendered = font.render(txt, True, colours["blue"].colour)
            self.surface.blit(rendered, (2, i*20))
            # create surface of the text and blit it onto the surface





    def DrawCurrentEquationXY(self, equation, x):
        if equation is None or equation.equation == "":
            return
            
        font = self.fonts[16]
        invalidX = x in [np.inf, np.NINF, np.nan]
        pushPixels = 2 if not invalidX else 1.2

        equString = UnreplaceEquation(equation.equation)
        equationText = font.render(f"[{equation.index+1}] {equString}", True, equation.colour.colour)
        
        rectangle = pygame.Rect(0, self.screenSize[1] - equationText.get_height()*pushPixels - 2, self.screenSize[0], 
                                equationText.get_height() * pushPixels + 2)
        # pygame.draw.rect(self.surface, colours["white"].colour, rectangle)
        self.surface.blit(equationText, (0, self.screenSize[1] - equationText.get_height() * pushPixels))

        if not invalidX:
            t = time.perf_counter() % 10
            
            xText = font.render(f"x={GetNumString(x)}", True, colours["black"].colour)

            yValues = ""
            try:
                for solution in equation.solutions:
                    yValues += GetNumString(float(eval(solution))) + ", "
                yValues = yValues[:-2]
            except Exception as e:
                yValues = f"ERROR: {e}"
              
            yText = font.render(f"y={yValues}", True, colours["black"].colour)  
            yXPlacement = xText.get_width() + 30 if xText.get_width() + 30 > 128 else 128

            self.surface.blit(xText, (0, self.screenSize[1] - xText.get_height())) 
            self.surface.blit(yText, (yXPlacement, self.screenSize[1] - yText.get_height()))




    def DrawFramerateGraph(self):
        timeNow = time.perf_counter()
        frametime = timeNow - self.lastFrame
        self.lastFrame = timeNow

        self.frameRates.append(1 / frametime)

        if len(self.frameRates) > self.maxFrameRates:
            self.frameRates.pop(0)

        pygame.draw.line(self.surface, colours["magenta"].colour, 
                (self.screenSize[0] - self.maxFrameRates, self.screenSize[1] - 30*1.8), 
                (self.screenSize[0], self.screenSize[1] - 30*1.8), 2)

        pygame.draw.line(self.surface, colours["magenta"].colour, 
                (self.screenSize[0] - self.maxFrameRates, self.screenSize[1] - 60*1.8), 
                (self.screenSize[0], self.screenSize[1] - 60*1.8), 2)



        lastX: int
        for i, x in enumerate(range(self.screenSize[0] - len(self.frameRates), self.screenSize[0])):
            if i == 0:
                lastX = x
                continue

            pygame.draw.line(self.surface, colours["purple"].colour, 
                    (lastX, self.screenSize[1] - self.frameRates[i-1]*1.8), 
                    (x, self.screenSize[1] - self.frameRates[i]*1.8), 1)
            lastX = x

            
        
