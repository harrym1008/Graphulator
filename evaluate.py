import numpy as np
import sympy as sp
from scipy.special import lambertw
from math import exp, log, log10

translations = []


π = pi = np.pi
e = euler = np.e
ϕ = golden = (1 + np.sqrt(5)) / 2
inf = np.inf






def GetReplacements():
    # Open tlacements.txt in read mode
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
            # 5. Convert the final list into a tuple
            # This is ready for appending into the translations list
            parts = [x.strip('"') for x in line.strip().split(",")]
            parts.append(f"#{i}#")
            translations.append(parts)


def TranslateSympyToNumpy(equation: str):
    for t in translations:
        equation = equation.replace(t[0], t[2])
    for t in translations:
        equation = equation.replace(t[2], t[1])
    return equation


def TranslateNumpyToSympy(equation: str):
    for t in translations:
        equation = equation.replace(t[1], t[2])
    for t in translations:
        equation = equation.replace(t[2], t[0])
    return equation



def factorial(x):
    # This is a good rough estimation for the factorial method
    return np.sqrt(2 * pi * x) * (x/e)**x



GetReplacements()