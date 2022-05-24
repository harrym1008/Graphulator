import math, matplotlib.pyplot as plt

equation = "math.sin(x/300)" #input("Enter an equation:\ny = ").replace("^", "**").replace("sin(", "math.sin(")

points = []


for x in range(-1800, 1800, 1):
    points.append([x, eval(equation)])

plt.scatter( [i[0] for i in points], [i[1] for i in points] )
plt.show()