import time
import getjson

baseFPS = getjson.GetData("max_fps")

deltaTime = 1 / baseFPS
lastFrameTime = 0


# Updates deltatime by comparing it to the last frametime
def Update():
    global deltaTime, lastFrameTime

    now = time.perf_counter()
    # time.perf_counter() is an extremely accurate value for the current time value
    # it returns a number of seconds which can be compared to the last number

    deltaTime = now - lastFrameTime
    lastFrameTime = now


# Multiplies deltatime to the baseFPS, normally this value will be one
def GetMultiplier():
    return deltaTime * baseFPS
