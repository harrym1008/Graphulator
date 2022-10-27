from multiprocessing import Queue
from pickletools import uint8
from serialsurf import SerialisedSurface

import colours
import pygame
import numpy as np
import time


def GetColourMap(x, y) -> int:
    for i, col in enumerate(colours.colourMap.keys()):
        if tuple(npArray[x][y]) == col:
            return i
    return 0
    





pygame.init()
graphScreen = pygame.display.set_mode((800, 600))    


whiteSurface = pygame.Surface((800, 600))
whiteSurface.fill((255,255,255))

q = Queue()

ss = SerialisedSurface(whiteSurface)
npArray = ss.npArray
shape = npArray.shape


t = time.perf_counter()

g = np.vectorize(GetColourMap)
new = np.fromfunction(g, (800, 600), dtype=np.uint8)

print(time.perf_counter() - t)
print(new)
print(new.nbytes)