from sympy import Eq, solve, sympify, latex
from sympy.parsing.sympy_parser import parse_expr
from sympy.core.numbers import I
from sympy.parsing.sympy_parser import T
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os


matplotlib.use("Agg")
def equation_solver(expr_str, plot_filename=None):
    
    try:

        if '=' not in expr_str:
            return {"error": "Not an equation"}
        
        
        
        lhs_str, rhs_str = expr_str.split('=')
        lhs = parse_expr(lhs_str.strip(), transformations=T[:11])
        rhs = parse_expr(rhs_str.strip(), transformations=T[:11])
        equation = Eq(lhs, rhs)
        solution = solve(equation)

        free_syms = sorted(list(equation.free_symbols), key=lambda s: s.name)

        all_real = all(not sol.has(I) for sol in solution)
        all_complex = all(sol.has(I) for sol in solution)

        result = {
            "number_of_solution": len(solution),
            "equation": latex(equation),
            "solution": [latex(sol) for sol in solution],
            "all_roots_real": all_real,
            "all_roots_complex": all_complex,
            "figure_path": None,
        }

        if len(free_syms) == 1:
            x_sym = free_syms[0]

            from sympy import lambdify
            f_sym = lhs - rhs
            f_num = lambdify(x_sym, f_sym, modules=["numpy", "math"])
            
            
            real_solutions = []
            for sol in solution:
                try:

                    val = complex(sol.evalf())
                    if abs(val.imag) < 1e-9: #sympy may treat is as complex with tiny imag part
                        real_solutions.append(val.real)
                except Exception:
                    pass
            
            #points for evaluation
            if real_solutions:
                smin = min(real_solutions)
                smax = max(real_solutions)
                span = max(1.0, smax - smin)
                x_min = smin - 2*span - 1
                x_max = smax + 2*span + 1
            else:
                x_min, x_max = -10, 10
            
            # Sample points
            xs = np.linspace(x_min, x_max, 800)
           
            ys = np.full_like(xs, np.nan, dtype=float)
            for i, xv in enumerate(xs):
                try:
                    yv = f_num(xv)
                    
                    ys[i] = float(yv)
                except Exception:
                    ys[i] = np.nan
            
            #plotting
            
            fig, ax = plt.subplots(figsize=(8,4.5))

            # Optional: change border thickness
            ax.spines['top'].set_linewidth(1)
            ax.spines['bottom'].set_linewidth(1)

            ax.plot(xs, ys, color='red')
            ax.axhline(0) 
            ax.set_xlabel(str(x_sym))
            ax.set_ylabel("f({})".format(x_sym))
            ax.set_title("Plot of f({}) = {}".format(x_sym, lhs_str.strip()))
            ax.grid(True, linestyle=':', linewidth=1)
            
           
            marked = []
            for r in real_solutions:
                try:
                    
                    y_r = f_num(r) #eval to zero
                    ax.scatter([r], [0]) #plots roots on x axis
                    marked.append(float(r))
                except Exception:
                    pass
            
            #Save figure
            fig.savefig(plot_filename, dpi=150, bbox_inches="tight")
            plt.close(fig)
            

            result["plotted_variable"] = str(x_sym)
            result["plotted_range"] = [float(x_min), float(x_max)]
            result["marked_roots"] = marked
        
        else:
            # no plot for multivariate
            result["figure_path"] = None
            result["plot_message"] = "Plot only produced for single-variable equations (found symbols: {}).".format(
                ",".join([str(s) for s in free_syms])
            )
        
        return result
    
    except Exception as e:
        return {"error": str(e)}