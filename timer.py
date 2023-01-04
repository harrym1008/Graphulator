import time
import numstr


def ResetTimer():
    global t
    t = time.perf_counter()

def GetTimeSince(header, reset=True):
    since = time.perf_counter() - t
    since = numstr.SigFig(since, 3)

    if reset:
        ResetTimer()
        
    print( f"{header}: {since} seconds")



t = 0
ResetTimer()

