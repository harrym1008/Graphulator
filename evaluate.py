import numpy as np
import sympy as sp
import math as m

from scipy.special import lambertw
from math import exp, log, log10
# these imports that seem to do nothing are used in the eval() function

translations = []


# Defines Constants: pi, euler's constant, golden ratio and infinity
π = pi = np.pi
e = euler = np.e
ϕ = golden = (1 + np.sqrt(5)) / 2
inf = np.inf





# Load in all of the translations from the TXT file
def GetReplacements():
    # Open translations.txt in read mode
    with open("translations.txt", "r") as file:
        # read all the lines
        lines = file.readlines()

        # loop through the lines

        for i, line in enumerate(lines):
            # create the parts tuple
            # 1. Remove the \n from the string by stripping "\n"
            # 2. Split the string at the comma into a list
            # 3. Loop through both the words in the list
            # 4. Get rid of the double quotes in the string
            # This is ready for appending into the translations list

            # All of these steps are carried out in the line below
            parts = [x.strip('"') for x in line.strip().split(",")]
            parts.append(f"#{i}#")
            translations.append(parts)


# Translates a string from using sympy to numpy
def TranslateSympyToNumpy(equation: str):
    for t in translations:
        equation = equation.replace(t[0], t[2])
    for t in translations:
        equation = equation.replace(t[2], t[1])
    return equation


# Translates a string from using numpy to sympy
def TranslateNumpyToSympy(equation: str):
    for t in translations:
        equation = equation.replace(t[1], t[2])
    for t in translations:
        equation = equation.replace(t[2], t[0])
    return equation



def Lerp(x, y, t):          # Stands for Linear Interpolation
    return x + (y-x) * t



def factorial(val):
    return m.factorial(int(val))



# Run this when the module is first imported
GetReplacements()