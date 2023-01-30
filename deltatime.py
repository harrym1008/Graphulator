import time
import getjson


# Class that deals with frametimes between frames, makes sure multiplier is correct for the
# main class when it calls the multiplier function
# The class makes it so despite stutters something moves at a constant speed


class DeltaTime:
    def __init__(self):
        self.baseFPS = getjson.GetData("max_fps")
        self.multiplier = 1

        self.deltatime = 1 / self.baseFPS
        self.fps = self.baseFPS
        self.lastFrameTime = 0


    # Updates deltatime by comparing it to the last frametime
    def Update(self):
        now = time.perf_counter()
        # time.perf_counter() is an extremely accurate value for the current time value
        # it returns a number of seconds which can be compared to the last number

        self.deltaTime = now - self.lastFrameTime
        self.lastFrameTime = now
        
        self.multiplier = self.deltaTime * self.baseFPS
        self.fps = 1/self.deltaTime
