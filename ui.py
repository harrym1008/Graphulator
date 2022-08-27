import pygame
import graph as _graph
from colours import *
from numstr import *


def DrawDebugDataOnGraphScreen(graph, mainFont):
    
    textToRender = [
        # f"{round(clock.get_fps(), 3)} FPS",
        f"Offset: x={GetNumString(graph.offset[0])}, y={GetNumString(graph.offset[1])}",
        f"Zoom: {SigFig(graph.zoom * 100, 5)}%" #,
        # f"Deltatime: {GetNumString(deltatime.deltaTime)}",
        # f"Res: X:{screenSize[0]}, Y:{screenSize[1]}",
        # f"Execution: {GetNumString(timeToExec * 1000)} ms"
    ]

    for i, txt in enumerate(textToRender):
        txtSurface = mainFont.render(txt, True, colours["blue"].colour)
        graph.baseSurface.blit(txtSurface, (2, i * 16))