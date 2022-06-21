import math

SUPERSCRIPT = "⁰¹²³⁴⁵⁶⁷⁸⁹"  # ⁺⁻⁼⁽⁾"
MULT = "×"


def FloatToStandardForm(n: float) -> str:
    x = math.log(n, 10)
    print(x)
    return f"{round(n, 2)}{MULT}10{StringToSuperscript(int(x))}"


def StringToSuperscript(n: int) -> str:
    string = ""

    for i in range(len(str(n))):
        string += SUPERSCRIPT[int(str(n)[i])]

    return string


print(FloatToStandardForm(999999999999))
