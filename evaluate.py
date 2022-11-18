import numpy as np
import sympy as sp
from scipy.special import lambertw
from math import exp
import time

replacements = []


π = pi = np.pi
e = euler = np.e
ϕ = golden = (1 + np.sqrt(5)) / 2
inf = np.inf




def GetYValue(x, expression):
    y = eval(expression)
    return y


def GetReplacements():
    # Open replacements.txt in read mode
    with open("replacements.txt", "r") as file:
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
            # This is ready for appending into the replacements list
            parts = [x.strip('"') for x in line.strip().split(",")]
            parts.append(f"#{i}#")
            replacements.append(parts)


def ReplaceEquation(equation: str):
    for rep in replacements:
        equation = equation.replace(rep[0], rep[2])
    for rep in replacements:
        equation = equation.replace(rep[2], rep[1])
    return equation

def UnreplaceEquation(equation: str):
    for rep in replacements:
        equation = equation.replace(rep[1], rep[2])
    for rep in replacements:
        equation = equation.replace(rep[2], rep[0])
    return equation



def factorial(x):
    x = int(x)
    val = 1
    for i in range(2, x+1):
        val *= i






GetReplacements()

if __name__ == "__main__":
    print(replacements)