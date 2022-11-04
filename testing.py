import sympy as sp
import time

x, y = sp.symbols("x y")

strEqu = input("Enter equation: ")
t = time.perf_counter()

try:
    sides = strEqu.split("=")

    if len(sides) == 2:
        lhs, rhs = tuple(sp.sympify(side) for side in sides)
    elif len(sides) == 1:
        lhs, rhs = y, sp.sympify(sides[0])
    else:
        raise ValueError("Too many equals signs (at most one)")

    equ = sp.Eq(lhs, rhs)
    equSolvedForY = sp.solve(equ, y)
except Exception as e:
    print(e)
    quit()

points = []
print(equSolvedForY, f"Computed in {time.perf_counter() - t} secs")

points = [[(i, solution.subs(x, i).evalf()) for i in range(720)] for solution in equSolvedForY]

exectime = time.perf_counter() - t
print(points)
print(exectime)
