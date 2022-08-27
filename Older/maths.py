import math


def InverseTrig(type, val):
    if type == "s":
        return math.asin(val)
    elif type == "c":
        return math.acos(val)
    else:
        return math.atan(val)



def StartFactorial(n):
    return Factorial(int(n))

def Factorial(n):
    if n < 2:
        return 1
    else:
        return n * Factorial(n-1)

def Logarithm(base, n):
    return math.log(n, base)
