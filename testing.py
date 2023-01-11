import timer, math
import numpy as np


timer.ResetTimer()
for i in range(1000):
    eval(f"np.sin(i)")
timer.GetTimeSince("Numpy sin")
for i in range(1000):
    eval(f"math.sin(i)")

timer.GetTimeSince("Math sin")



narr = np.arange(0, 1000, 1)
narr2 = np.sin(narr + 2)
timer.GetTimeSince("numpy array sin")



# y = sin((x+2)/3)