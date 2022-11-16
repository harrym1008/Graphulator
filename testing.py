from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))

expr = parse_expr(input("Enter:"),
                  transformations=transformations)

print(expr)
