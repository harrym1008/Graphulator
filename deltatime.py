import time
import main

deltaTime = 0
lastFrameTime = 0


def Update():
    global deltaTime, lastFrameTime

    now = time.perf_counter()

    deltaTime = now - lastFrameTime
    lastFrameTime = now


def GetMultiplier():
    return deltaTime * main.FPS