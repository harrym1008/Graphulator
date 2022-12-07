from ui import UserInterface
from evaluate import *

import drawfunc



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

