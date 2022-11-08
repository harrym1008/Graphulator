import sympy as sp
from scipy.optimize import fsolve
from numpy import *
import time

x, y = sp.symbols("x y")

strEqu = input("Enter equation: ")
t = time.perf_counter()

sides = strEqu.split("=")

if len(sides) == 2:
    lhs, rhs = tuple(sp.sympify(side) for side in sides)
elif len(sides) == 1:
    lhs, rhs = y, sp.sympify(sides[0])
else:
    raise ValueError("Too many equals signs (at most one)")

equ = sp.Eq(lhs, rhs)

func_np = sp.lambdify(x, equ, modules=["numpy"])
solution = fsolve(func_np, 0.5)
