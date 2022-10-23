import time
import main

baseFPS = 60

deltaTime = 1 / baseFPS
lastFrameTime = 0


def Update():
    global deltaTime, lastFrameTime

    now = time.perf_counter()

    deltaTime = now - lastFrameTime
    lastFrameTime = now


def GetMultiplier():
    return deltaTime * baseFPS