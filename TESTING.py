import time
from sympy import *
from numpy import *

init_printing(use_unicode=True)

x, y = symbols("x y")

lhs = parsing.sympy_parser.parse_expr("tan(x) ** y")  # input("LHS: "))
rhs = parsing.sympy_parser.parse_expr("tan(y) ** x")  # input("RHS: "))

eq = Eq(lhs, rhs)

maths = 0

t = time.perf_counter()
solved = solve(eq, y)
print(time.perf_counter() - t)
t = time.perf_counter()

print(solved)


for x in range(-400, 400):
    for i in solved:
        try:
            y = eval(str(i))
            print(x, y)
        except:
            pass
        finally:
            maths += 1

print(time.perf_counter() - t)

print(maths)