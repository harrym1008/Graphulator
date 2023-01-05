from evaluate import *

import drawfunc
import numstr



class UIMath:
    a = 0
    b = 0
    c = 0
    t = 0

    @classmethod
    def DefineConstants(cls, constants):
        cls.a = constants[0]
        cls.b = constants[1]
        cls.c = constants[2]
        cls.t = cls.Lerp(constants[3], constants[4], (time.perf_counter() % 10) / 10)


    @classmethod
    def GetConstants(cls):
        return (cls.a, cls.b, cls.c, cls.t)


    @classmethod
    def FindYIntercept(cls, strEqu):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t
        print("Hola", a, b, c, t)

        try:
            x, y = 0, sp.Symbol("y")
            strEqu = UnreplaceEquation(strEqu)
            equ = drawfunc.PlottedEquation.ProduceSympyEquation(strEqu, getHandSides=False)
            ySolutions = drawfunc.PlottedEquation.ProduceEquationSolutions(equ, "y")
            return ySolutions
        except Exception as error:
            return error
            

    @classmethod
    def FindXIntercept(cls, strEqu):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        try:
            x, y = sp.Symbol("x"), 0
            strEqu = UnreplaceEquation(strEqu)
            equ = drawfunc.PlottedEquation.ProduceSympyEquation(strEqu, getHandSides=False)
            xSolutions = drawfunc.PlottedEquation.ProduceEquationSolutions(equ, "x")
            return xSolutions
        except Exception as error:
            return error


    @classmethod
    def RemoveDuplicatesFromArray(cls, array, sf=6):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        new = []
        newRounded = []
        for point in array:
            roundedPoint = numstr.SigFig(point[0], sf), numstr.SigFig(point[1], sf)
            if roundedPoint not in newRounded and point not in new:
                new.append(point)
                newRounded.append(roundedPoint)
        return new


    @classmethod
    def RemoveImaginaryParts(cls, array):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        realPoints = []
        for point in array:

            try:
                x = point[0].as_real_imag()[0]
            except:
                x = point[0]
            
            try:
                y = point[1].as_real_imag()[0]
            except:
                y = point[1]

            realPoints.append((x, y))
        return realPoints


    @staticmethod
    def CompareFloatsWithSigFig(x, y, sf=6):
        return numstr.SigFig(x, sf) == numstr.SigFig(y, sf)


    @classmethod
    def FindIntersections(cls, strEqu1, strEqu2):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        strEqu1 = UnreplaceEquation(strEqu1)
        strEqu2 = UnreplaceEquation(strEqu2)

        equ1 = drawfunc.PlottedEquation.ProduceSympyEquation(strEqu1, getHandSides=False)
        equ2 = drawfunc.PlottedEquation.ProduceSympyEquation(strEqu2, getHandSides=False)

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
                    if not xNum.is_real:
                        xNum = sp.re(xNum)

                    x = xNum

                    yValues1 = sp.solve( sp.Eq(equ1Solution, y), y)
                    yValues2 = sp.solve( sp.Eq(equ2Solution, y), y)

                    shortestSolutions = yValues1 if len(yValues1) <= len(yValues2) else yValues2

                    for solution in shortestSolutions:    
                        yNum = eval(ReplaceEquation(str(solution)))                            
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

                    if True in [UIMath.CompareFloatsWithSigFig(point[1], yNum) for point in points]:
                        continue

                    xValues1 = sp.solve( sp.Eq(equ1Solution, x), x)
                    xValues2 = sp.solve( sp.Eq(equ2Solution, x), x)

                    shortestSolutions = xValues1 if len(xValues1) <= len(xValues2) else xValues2

                    for solution in shortestSolutions:   
                        xNum = eval(ReplaceEquation(str(solution)))                            
                        points.append((xNum, yNum))

        points = UIMath.RemoveImaginaryParts(points)
        return UIMath.RemoveDuplicatesFromArray(points)


    @classmethod
    def EvaluateX(cls, equation, yValue: float, constants):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        x, y = sp.symbols("x y")
        a = constants[0]


        equation = UnreplaceEquation(equation)
        equation = drawfunc.PlottedEquation.ProduceSympyEquation(equation, getHandSides=False)
        
        solvedForX = sp.solve(equation, x)
        points = []

        for solution in solvedForX:
            solution = solution.subs(y, yValue)
            points.append((solution.evalf(), yValue))
            

        points = UIMath.RemoveImaginaryParts(points)

        return UIMath.RemoveDuplicatesFromArray(points)


    @classmethod
    def EvaluateY(cls, equation, xValue: float):
        a, b, c, t = cls.a, cls.b, cls.c, cls.t

        x, y = sp.symbols("x y")
        equation = UnreplaceEquation(equation)
        equation = drawfunc.PlottedEquation.ProduceSympyEquation(equation, getHandSides=False)
        
        solvedForY = sp.solve(equation, y)
        points = []

        for solution in solvedForY:
            solution = solution.subs(x, xValue)
            points.append((solution.evalf(), xValue))
            

        points = UIMath.RemoveImaginaryParts(points)

        return UIMath.RemoveDuplicatesFromArray(points)
            

    @staticmethod
    def Lerp(x, y, t):          # Stands for Linear Interpolation
        return x + (y-x) * t


    @staticmethod
    def TryConvertToFloat(x):
        try:
            return float(x)
        except:
            return 0





        
if __name__ == "__main__":
    equations = [ "2y=.75x+.2", "4xxx+4xx+x" ]

    print(UIMath.EvaluateX(equations[1], 2))
    print(UIMath.EvaluateY(equations[1], 2))