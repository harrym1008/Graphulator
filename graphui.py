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

        self.highlightedPoints = []


    def ClearUISurface(self):
        self.surface.fill(colours["transparent"].colour)


    def ScreenHasBeenResized(self, newSize):
        self.surface = pygame.Surface(newSize, pygame.SRCALPHA, 32)
        self.screenSize = newSize


    def UpdateUISurface(self, graph, mousePos, equation):
        self.ClearUISurface()
        self.TopRightDebugData(graph)
        self.DrawHighlightedPoints(graph)
        # self.DrawFramerateGraph()
        x, y = self.WriteMousePosition(mousePos, graph)
        self.DrawCurrentEquationXY(equation, x, y)
        


    
    def WriteMousePosition(self, mousePos, graph):
        if mousePos is None:  # mouse is not focused on the window
            return np.inf, np.inf

        font = self.fonts[12]

        # Calculate co-ordinates of the mouse position
        # x = (pos[0] / screenSize[0] - 0.5) * screenSize[0] / zoom + offset[0]
        # y = -(pos[1] / screenSize[1] - 0.5) * screenSize[1] / zoom + offset[1]

        # Simplified:
        x = (graph.offset[0] * graph.zoom - 0.5 * self.screenSize[0] + mousePos[0]) / graph.zoom
        y = (-graph.offset[1] * graph.zoom - 0.5 * self.screenSize[1] + mousePos[1]) / -graph.zoom

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

        return (x, y)


    def DrawHighlightedPoints(self, graph):
        for currentPoint in self.highlightedPoints:
            x = -graph.zoomedOffset[0] + graph.screenCentre[0] + currentPoint[0] * graph.zoom
            y = graph.zoomedOffset[1] + graph.screenCentre[1] - currentPoint[1] * graph.zoom

            pygame.draw.circle(self.surface, colours["black"].colour,
                               (x, y), 5)
            pygame.draw.circle(self.surface, colours["white"].colour,
                               (x, y), 3)

            text = f"({NStr(currentPoint[0], short=True)}, {NStr(currentPoint[1], short=True)})"
            renderedText = self.fonts[12].render(text, True, colours["black"].colour)
            
            textLocation = x - renderedText.get_width() // 2, y - renderedText.get_height() // 2 - 16
            boxLocation = textLocation[0] - 2, textLocation[1] - 2
            boxSize = renderedText.get_width() + 4, renderedText.get_height() + 4

            rectangle = pygame.Rect(boxLocation[0], boxLocation[1], boxSize[0], boxSize[1])
            pygame.draw.rect(self.surface, colours["faded white"].colour, rectangle)
            self.surface.blit(renderedText, (textLocation[0], textLocation[1]))




    def TopRightDebugData(self, graph):
        font = self.fonts[20]
        # Check to make sure the program will not divide by zero on the first frame
        # ---> fps returns 0 on frame 1

        textToRender = [
            f"X = {NStr(graph.offset[0])}",
            f"Y = {NStr(graph.offset[1])}",
            f"Zoom: {SigFig(graph.zoom * 100, 5)}%"
        ]  # List of text to render on the screen

        for i, txt in enumerate(textToRender):
            rendered = font.render(txt, True, colours["blue"].colour)
            self.surface.blit(rendered, (2, i*20))
            # create surface of the text and blit it onto the surface





    def DrawCurrentEquationXY(self, equation, x, y):
        if equation is None or equation.equation == "":
            return
            
        font = self.fonts[16]
        invalidInputValues = GraphUserInterface.XAndYCheckForNullValues(equation, x, y)
        pushPixels = 2 if not invalidInputValues else 1.2

        equString = UnreplaceEquation(equation.equation)
        equationText = font.render(f"[{equation.index+1}] {equString}", True, equation.colour.colour)
        
        rectangle = pygame.Rect(0, self.screenSize[1] - equationText.get_height()*pushPixels - 2, self.screenSize[0], 
                                equationText.get_height() * pushPixels + 2)
        pygame.draw.rect(self.surface, colours["faded white"].colour, rectangle)
        self.surface.blit(equationText, (0, self.screenSize[1] - equationText.get_height() * pushPixels))

        if invalidInputValues:
            return

        points = GraphUserInterface.GetXAndYValues(equation, x, y)

        xString = "x="
        yString = "y="

        for xPoint in points[0]:
            if isinstance(xPoint, Exception):
                xString += f"ERROR: {xPoint}, "
                continue
            xString += NStr(xPoint) + ", "

        for yPoint in points[1]:
            if isinstance(yPoint, Exception):
                yString += f"ERROR: {yPoint}, "
                continue
            yString += NStr(yPoint) + ", "

        xString = xString[:-2]
        yString = yString[:-2]

        xText = font.render(xString, True, colours["black"].colour)
        yText = font.render(yString, True, colours["black"].colour)

        yXPlacement = xText.get_width() + 30 if xText.get_width() + 30 > 128 else 128
        self.surface.blit(xText, (0, self.screenSize[1] - xText.get_height())) 
        self.surface.blit(yText, (yXPlacement, self.screenSize[1] - yText.get_height()))


        '''if not invalidX:
            t = time.perf_counter() % 10
            
            xText = font.render(f"x={NStr(x)}", True, colours["black"].colour)

            yValues = ""
            try:
                for solution in equation.solutions:
                    yValues += NStr(float(eval(solution))) + ", "
                yValues = yValues[:-2]
            except Exception as e:
                yValues = f"ERROR: {e}"
              
            yText = font.render(f"y={yValues}", True, colours["black"].colour)  
            yXPlacement = xText.get_width() + 30 if xText.get_width() + 30 > 128 else 128

            self.surface.blit(xText, (0, self.screenSize[1] - xText.get_height())) 
            self.surface.blit(yText, (yXPlacement, self.screenSize[1] - yText.get_height()))'''



    @staticmethod
    def XAndYCheckForNullValues(equation, x, y):
        return (x in [np.inf, np.NINF, np.nan] and len(equation.solutions["y"]) > 0) or \
               (y in [np.inf, np.NINF, np.nan] and len(equation.solutions["x"]) > 0)


    @staticmethod
    def GetXAndYValues(equation, x, y):
        t = time.perf_counter() % 10
        xArr = []
        yArr = []

        for solution in equation.solutions["y"]:
            try:
                yArr.append(float(eval(solution)))
            except Exception as e:
                yArr.append(e)

            if x not in xArr:
                xArr.append(x)
            print("Y solution")

        for solution in equation.solutions["x"]:
            try:
                xArr.append(float(eval(solution)))
            except Exception as e:
                xArr.append(e)

            if y not in yArr:
                yArr.append(y)
            print("X solution")

        return xArr, yArr


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

            

