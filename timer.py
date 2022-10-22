import time


def ResetTimer():
    global t
    t = time.perf_counter()

def GetTimeSince(header, reset=True):
    since = time.perf_counter() - t
    
    if reset:
        ResetTimer()
        
    return f"{header}: {since} seconds"



t = 0
ResetTimer()

