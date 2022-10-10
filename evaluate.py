import numpy as np
from sympy import *


x, y, z = symbols("x y z")



def StringToExpression(string):
    return sympify(string)


def EvaluateY(expr: Expr, xValue):
    return expr.subs(x, xValue)




e = StringToExpression("sin(x)")
print(EvaluateY(e, 5))