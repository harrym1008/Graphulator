import timer, math
import numpy as np
import sympy as sp




def FastLogFloor(value):
    if value == 0:
        return 0

    value = abs(value)

    log = 0
    while value < 1 or value >= 10:
        if value < 1:
            log -= 1
            value *= 10
        if value >= 10:
            log += 1
            value /= 10

    return value


timer.ResetTimer()
for i in range(1, 10001):
    FastLogFloor(i)
timer.GetTimeSince("Fast log")


for i in range(1, 10001):
    math.floor(math.log(i))
timer.GetTimeSince("Slow log maybe")




# y = sin((x+2)/3)