import re
from sympy import Eq, solve, sympify, latex
from sympy.parsing.sympy_parser import parse_expr
from sympy.core.numbers import I
from sympy.parsing.sympy_parser import T

def equation_solver(expr_str):
    
    try:

        if '=' not in expr_str:
            return {"error": "Not an equation"}
        
        lhs_str, rhs_str = expr_str.split('=')
        lhs = parse_expr(lhs_str.strip(), transformations=T[:11])
        rhs = parse_expr(rhs_str.strip(), transformations=T[:11])
        equation = Eq(lhs, rhs)
        solution = solve(equation)

        all_real = all(not sol.has(I) for sol in solution)
        all_complex = all(sol.has(I) for sol in solution)
        return {
            "number_of_solution": len(solution),
            "equation": latex(equation),
            "solution": [latex(sol) for sol in solution],
            "all_roots_real": all_real,
            "all_roots_complex": all_complex,
        }
    except Exception as e:
        return {"error": str(e)}