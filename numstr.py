import math
import numpy as np

SUPERSCRIPT = "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"  # ⁺⁻⁼⁽⁾"


def NStr(n: float, short: bool = False) -> str:
    if n in [np.inf, np.NINF, np.nan] or math.isnan(n):
        return "ERROR"

    if n == 0:
        return "0"

    powersOf10 = int(math.log(math.fabs(n), 10))

    if (8 > powersOf10 > -4 and short) or (10 > powersOf10  > -4 and not short):
        if n % 1 == 0:
            return str(int(n))

        return GetFractionalNumber(n, powersOf10, 4 if short else 6)

    return StandardForm(n, 2 if short else 5)


def GetCoordString(x: float, y: float):
    return f"({NStr(x, short=True)}, {NStr(y, short=True)})"



def GetFractionalNumber(n, powersOf10, maxdp=6) -> str:
    dp = maxdp - powersOf10 if maxdp - powersOf10 >= 0 else 0
    dp = dp if powersOf10 > -2 else 2+maxdp
    floatN = round(n, dp)

    if floatN % 1 == 0:
        return str(int(floatN))
    return str(floatN)


def SigFig(x, sig):
    if x == 0:
        return 0
    return round(x, sig - int(math.log(abs(x), 10)) - 1)


def SigFig(x, figures):
    if x == 0:
        return 0
    logarithm = math.log(abs(x), 10)
    decPlaces = figures - int(logarithm)
    return round(x, decPlaces)



def StandardForm(n: float, dp: int = 3) -> str:
    if n == 0:
        return f"0.0×10{StringToSuperscript(0)}"

    negative = "-" if n < 0 else ""
    n = math.fabs(n)
    x = math.log(n, 10)
    normalisedN = n / 10 ** math.trunc(x)

    # guarantee that the standard form is between 1 and 10
    while round(normalisedN, dp) >= 10 or round(normalisedN, dp) < 1:
        if round(normalisedN, dp) >= 10:
            normalisedN /= 10
            x += 1
        elif round(normalisedN, dp) < 1:
            normalisedN *= 10
            x -= 1

    return f"{negative}{round(normalisedN, dp)}×10{StringToSuperscript(int(x))}"  #


def StringToSuperscript(n: int) -> str:
    string = ""

    for i in range(len(str(n))):
        if str(n)[i] == "-":
            string += SUPERSCRIPT[10]
            continue

        string += SUPERSCRIPT[int(str(n)[i])]

    return string
