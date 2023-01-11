import timer, math
import numpy as np
import sympy as sp




x, y = sp.symbols("x y")

eq = sp.Eq(sp.sympify("x^2 - y"), 4)
expr = sp.solve(eq, x)[1]

f = sp.lambdify(x, expr, "numpy")
a = np.arange(100, 10000, 1)

print(expr)



data1 = []
data2 = []

timer.ResetTimer()
for i in range(10000):
    data1.append(eval(f"np.sqrt(4+i)"))

timer.GetTimeSince("Numpy sin")
for i in range(10000):
    data2.append(eval(f"math.sqrt(4+i)"))

timer.GetTimeSince("Math sin")

print(f(10.1))


narr = np.arange(0, 10000, 0.9)
narr2 = f(narr)
timer.GetTimeSince("numpy array sin")



# y = sin((x+2)/3)