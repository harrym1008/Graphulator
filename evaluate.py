import numpy as np
import sympy as sp

replacements = []


π = pi = 3.141592653589793238
e = euler = 2.718281828459045
ϕ = golden = 1.61803398874989



def GetYValue(x, expression):
    y = eval(expression)
    return y


def GetReplacements():
    # Open replacements.txt in read mode
    with open("replacements.txt", "r") as file:
        # read all the lines
        lines = file.readlines()
        # loop through the lines
        for line in lines:
            # create the parts tuple
            # 1. Remove the \n from the string by stripping "\n"
            # 2. Split the string at the comma into a list
            # 3. Loop through both the words in the list
            # 4. Get rid of the double quotes in the string
            # 5. Convert the final list into a tuple
            # This is ready for appending into the replacements list
            parts = tuple([x.strip('"') for x in line.strip().split(",")])
            replacements.append(parts)


def ReplaceEquation(equation: str):
    for rep in replacements:
        equation = equation.replace(rep[0], rep[1])
    return equation

def UnreplaceEquation(equation: str):
    for rep in replacements:
        equation = equation.replace(rep[1], rep[0])
    return equation






GetReplacements()

if __name__ == "__main__":
    print(replacements)