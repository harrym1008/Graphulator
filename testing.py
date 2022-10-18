import pygame
import numpy as np
import time
import drawfunc
from multiprocessing import Queue


pygame.init()
graphScreen = pygame.display.set_mode((800, 600))    


whiteSurface = pygame.Surface((800, 600))
whiteSurface.fill((64,128,255))

'''imgData = None

newSurface = None


def ConvertToList():
    global imgData, whiteSurface, newSurface
    imgData = pygame.surfarray.array3d(whiteSurface)

def ConvertToSurface():
    global imgData, whiteSurface, newSurface
    imgData[100][100] = [255,255,255]
    newSurface = pygame.surfarray.make_surface(imgData)



startTime = time.perf_counter()
ConvertToList()
convertToList = time.perf_counter() - startTime

startTime = time.perf_counter()
ConvertToSurface()
convertFromList = time.perf_counter() - startTime

queue = Queue()
queue.put(imgData)

print("Put into queue")
queue.get()
print("Got from queue - success")



print(convertToList, convertFromList)
print(newSurface == whiteSurface)



graphScreen.blit(whiteSurface, (0, 0))
pygame.display.update()
time.sleep(1)
graphScreen.blit(newSurface, (0, 0))
pygame.display.update()
print("New")
time.sleep(15)
'''



q = Queue()

q.put(drawfunc.ThreadOutput(whiteSurface, 1, (0, 0)))
x = q.get()
print(x.serialisedSurface.GetSurface())