import sympy as sp



transformations = (sp.parsing.sympy_parser.standard_transformations,
                   sp.parsing.sympy_parser.implicit_multiplication_application,
                   sp.parsing.sympy_parser.convert_xor)
                   

expr = sp.parse_expr(input("Enter:"),
                  transformations=transformations)


print(str(expr))
