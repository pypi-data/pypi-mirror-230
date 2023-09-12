from .latex2sympy import latex2sympy, latex2latex

# latex2latex(r'A_1=\begin{bmatrix}1 & 2 & 3 & 4 \\ 5 & 6 & 7 & 8\end{bmatrix}')
# latex2latex(r'b_1=\begin{bmatrix}1 \\ 2 \\ 3 \\ 4\end{bmatrix}')
# tex = r"(x+2)|_{x=y+1}"
# tex = r"\operatorname{zeros}(3)"
tex = r"\operatorname{rows}(\begin{bmatrix}1 & 2 \\ 3 & 4\end{bmatrix})"
# print("latex2latex:", latex2latex(tex))
math = latex2sympy(tex)
# math = math.subs(variances)
print("latex:", tex)
# print("var:", variances)
print("raw_math:", math)
# print("math:", latex(math.doit()))
# print("math_type:", type(math.doit()))
# print("shape:", (math.doit()).shape)
print("cal:", latex2latex(tex))
