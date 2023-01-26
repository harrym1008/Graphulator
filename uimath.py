from evaluate import *
from drawfunc import PlottedEquation
import numstr

import time



class UIMath:
    a = 0
    b = 0
    c = 0
    t = 0

    # Resets constants to the inputted values, and calculates T
    @classmethod
    def DefineConstants(cls, constants):
        cls.a = constants[0]
        cls.b = constants[1]
        cls.c = constants[2]
        cls.t = cls.Lerp(constants[3], constants[4], (time.perf_counter() % 10) / 10)


    # Return an ordered tuple of the constants
    @classmethod
    def GetConstants(cls):
        return (cls.a, cls.b, cls.c, cls.t)


    # Find the points on an equation where X = 0
    @classmethod
    def FindYIntercept(cls, strEqu):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t
        print("Hola", a, b, c, t)

        try:
            x, y = 0, sp.Symbol("y")
            strEqu = TranslateNumpyToSympy(strEqu)
            equ = PlottedEquation.ProduceSympyEquation(strEqu, getHandSides=False)
            ySolutions = PlottedEquation.ProduceEquationSolutions(equ, "y")
            return ySolutions
        except Exception as error:
            return error
            

    # Find the points on an equation where Y = 0
    @classmethod
    def FindXIntercept(cls, strEqu):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        try:
            x, y = sp.Symbol("x"), 0
            strEqu = TranslateNumpyToSympy(strEqu)
            equ = PlottedEquation.ProduceSympyEquation(strEqu, getHandSides=False)
            xSolutions = PlottedEquation.ProduceEquationSolutions(equ, "x")

            print(xSolutions)

            return xSolutions
        except Exception as error:
            return error


    # Removes duplicate points from the array
    @classmethod
    def RemoveDuplicatesFromArray(cls, array, sf=6):
        new = []
        newRounded = []
        for point in array:
            roundedPoint = numstr.SigFig(point[0], sf), numstr.SigFig(point[1], sf)
            if roundedPoint not in newRounded and point not in new:
                new.append(point)
                newRounded.append(roundedPoint)
        return new


    # Convert a set of either real or imaginary points to all real points
    @classmethod
    def ConvertToFloats(cls, array):
        realPoints = []
        for point in array:
            x = float(point[0])
            y = float(point[1])
            realPoints.append((x, y))

        return realPoints


    # Compare a value by rounding to significant figures first.
    # This is done so the smallest floating point imprecision doesn't affect the comparison.
    @staticmethod
    def CompareFloatsWithSigFig(x, y, sf=6):
        return numstr.SigFig(x, sf) == numstr.SigFig(y, sf)


    # Finds the intersections of two equations
    @classmethod
    def FindIntersections(cls, strEqu1, strEqu2):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        strEqu1 = TranslateNumpyToSympy(strEqu1)
        strEqu2 = TranslateNumpyToSympy(strEqu2)

        equ1 = PlottedEquation.ProduceSympyEquation(strEqu1, getHandSides=False)
        equ2 = PlottedEquation.ProduceSympyEquation(strEqu2, getHandSides=False)

        solvedForY = [sp.solve(equ1, "y"), sp.solve(equ2, "y")]
        solvedForX = [sp.solve(equ1, "x"), sp.solve(equ2, "x")]

        points = []

        print(f"{equ1}, {equ2}")

        for equ1Solution in solvedForY[0]:
            for equ2Solution in solvedForY[1]:
                x, y = sp.symbols("x y")

                equ = sp.Eq(equ1Solution, equ2Solution)
                xValues = sp.solve( equ, x )
                
                for xValue in xValues:
                    xNum = xValue.evalf()                    
                    if not xNum.is_real:    # Imaginary number
                        xNum = sp.re(xNum)


                    yValues1 = sp.solve( sp.Eq(equ1Solution, y), y)
                    yValues2 = sp.solve( sp.Eq(equ2Solution, y), y)

                    shortestSolutions = yValues1 if len(yValues1) <= len(yValues2) else yValues2

                    for solution in shortestSolutions:
                        newSolution = TranslateSympyToNumpy(str(solution))    
                        yNum = eval( newSolution )                            
                        points.append((xNum, yNum))
                        


        for equ1Solution in solvedForX[0]:
            for equ2Solution in solvedForX[1]:
                x, y = sp.symbols("x y")

                equ = sp.Eq(equ1Solution, equ2Solution)
                yValues = sp.solve( equ, y )
                
                for yValue in yValues:
                    yNum = yValue.evalf()                 
                    if not yNum.is_real:
                        yNum = sp.re(yNum)

                    y = yNum

                    xValues1 = sp.solve( sp.Eq(equ1Solution, x), x)
                    xValues2 = sp.solve( sp.Eq(equ2Solution, x), x)

                    shortestSolutions = xValues1 if len(xValues1) <= len(xValues2) else xValues2

                    for solution in shortestSolutions:   
                        xNum = eval(TranslateSympyToNumpy(str(solution)))                            
                        points.append((xNum, yNum))

        points = UIMath.ConvertToFloats(points)   # Make sure there are no imaginary values
        return UIMath.RemoveDuplicatesFromArray(points)     # Remove duplicate points from the array


    # Evaluates X for an equation at a given Y value
    @classmethod
    def EvaluateX(cls, equation, yValue: float):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        x, y = sp.symbols("x y")

        equation = TranslateNumpyToSympy(equation)
        equation = PlottedEquation.ProduceSympyEquation(equation, getHandSides=False)
        
        solvedForX = sp.solve(equation, x)
        points = []

        for solution in solvedForX:
            solution = solution.subs(y, yValue)
            points.append((solution.evalf(), yValue))
            

        points = UIMath.ConvertToFloats(points)

        return UIMath.RemoveDuplicatesFromArray(points)


    # Evaluates Y for an equation at a given X value
    @classmethod
    def EvaluateY(cls, equation, xValue: float):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        x, y = sp.symbols("x y")
        equation = TranslateNumpyToSympy(equation)
        equation = PlottedEquation.ProduceSympyEquation(equation, getHandSides=False)
        
        solvedForY = sp.solve(equation, y)
        points = []

        for solution in solvedForY:
            solution = solution.subs(x, xValue)
            points.append((xValue, solution.evalf()))
            

        points = UIMath.ConvertToFloats(points)

        return UIMath.RemoveDuplicatesFromArray(points)
            
    # Lerp stands for Linear Interpolation
    @staticmethod
    def Lerp(x, y, t):          
        return x + (y-x) * t


    # Attempt to convert an object to a float
    @staticmethod
    def TryConvertToFloat(x):
        try:
            return float(x)
        except Exception:
            return np.inf

