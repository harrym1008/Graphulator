from evaluate import *

import drawfunc
import numstr



class UIMath:
    @staticmethod
    def FindYIntercept(strEqu):
        try:
            x, y = 0, sp.Symbol("y")
            strEqu = UnreplaceEquation(strEqu)
            equ = drawfunc.PlottedEquation.ProduceSympyEquation(strEqu, getHandSides=False)
            ySolutions = drawfunc.PlottedEquation.ProduceEquationSolutions(equ, "y")
            return ySolutions
        except Exception as error:
            return error
            

    @staticmethod
    def FindXIntercept(strEqu):
        try:
            x, y = sp.Symbol("x"), 0
            strEqu = UnreplaceEquation(strEqu)
            equ = drawfunc.PlottedEquation.ProduceSympyEquation(strEqu, getHandSides=False)
            ySolutions = drawfunc.PlottedEquation.ProduceEquationSolutions(equ, "y")
            return ySolutions
        except Exception as error:
            return error


    def RemoveDuplicatesFromArray(array, sf=6):
        new = []
        newRounded = []
        for point in array:
            roundedPoint = numstr.SigFig(point[0], sf), numstr.SigFig(point[1], sf)
            if roundedPoint not in newRounded and point not in new:
                new.append(point)
                newRounded.append(roundedPoint)
        return new


    def RemoveImaginaryParts(array):
        realPoints = []
        for point in array:
            print(type(point[0]), type(point[1]))

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


    def CompareFloatsWithSigFig(x, y, sf=6):
        return numstr.SigFig(x, sf) == numstr.SigFig(y, sf)


    def FindIntersections(strEqu1, strEqu2):
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

        
if __name__ == "__main__":
    equations = [ ".75x+.2", "4xxx+4xx+x" ]

    points = UIMath.FindIntersections(equations[0], equations[1])
    print(points)