import math

SUPERSCRIPT = "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"  # ⁺⁻⁼⁽⁾"
MULT = "×"


def GetNumString(n: float, sigfigs: int = 3) -> str:
    if n == 0:
        return "0"

    powersOf10 = math.log(math.fabs(n), 10)
    print(powersOf10)

    if 8 > powersOf10 > -4:
        s = str(SigFig(n, sigfigs))
        print(f"/{s}/")

        try:
            print(s[-2:])
            if s[-2:] == ".0":
                return s[-2:]
        finally:
            return s
    return StandardForm(n, sigfigs)


def SigFig(x, sig):
    return round(x, sig - int(math.floor(math.log(abs(x), 10))) - 1)


def StandardForm(n: float, dp: int = 3) -> str:
    if n == 0:
        return f"0.0{MULT}10{StringToSuperscript(0)}"

    negative = "-" if n < 0 else ""
    n = math.fabs(n)
    x = math.log(n, 10)
    normalisedN = n / 10 ** math.trunc(x)

    # fix weird quirk with numbers less than 1
    while normalisedN > 10 or normalisedN < 1:
        if normalisedN > 10:
            normalisedN /= 10
            x += 1
        elif normalisedN < 1:
            normalisedN *= 10
            x -= 1

    return f"{negative}{round(normalisedN, dp)}{MULT}10{StringToSuperscript(int(x))}"


def StringToSuperscript(n: int) -> str:
    string = ""

    for i in range(len(str(n))):
        if str(n)[i] == "-":
            string += SUPERSCRIPT[10]
            continue

        string += SUPERSCRIPT[int(str(n)[i])]

    return string


print(GetNumString(0.000002))
print(GetNumString(3482957.3245))
print(GetNumString(-21.432))
