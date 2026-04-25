from __future__ import annotations
import ast #abstract syntax trees
import math
import re #regex for symbols
from typing import Callable

from .exceptions import EvaluationError, ParseError
from .models import Interval

valid_functions: dict[str, object] = {
    "abs": abs,
    "cos": math.cos,
    "e": math.e,
    "exp": math.exp,
    "log": math.log,
    "pi": math.pi,
    "sin": math.sin,
    "sqrt": math.sqrt,
    "tan": math.tan,
}
valid_expressions = (
    ast.Add, #sum
    ast.BinOp, #binary ops
    ast.Call, #call funcs
    ast.Constant, #numbers
    ast.Div, #division
    ast.Expression,#whole expression
    ast.Load,#access to variables
    ast.Mult,#multipl
    ast.Name,#names
    ast.Pow,#power
    ast.Sub,#substraction
    ast.UAdd,# +x
    ast.UnaryOp,#operaciones w just a number
    ast.USub,# -x
)

_POLYNOMIAL_TERM_PATTERN = re.compile(
    r"(?:(?:\d+(?:\.\d*)?|\.\d+)?x(?:\^\d+)?)|(?:\d+(?:\.\d*)?|\.\d+)" #terms with x or terms w/out x
)

_INTERVAL_PATTERN = re.compile(
    r"\s*(?P<left>-?(?:\d+(?:\.\d*)?|\.\d+))\s*:\s*(?P<right>-?(?:\d+(?:\.\d*)?|\.\d+))\s*" #left endpoint and right endpoint
)


def _validate_ast(tree: ast.AST) -> None: #when we put nothing in the return when there is no error, 
                                        #we mean the function does not return anything, not that it returns "nothing"
    """function to validate info
    
        Parameters:
            tree: ast tree
        
        Return:
            nothing: if there is no error 
            corresponding parseerror: when something is wrong
    """
    for node in ast.walk(tree): #ast.walk() returns all the nodes so is a for loop for nod in nodes basically
        if not isinstance(node, valid_expressions):
            raise ParseError("expression not valid")
        if isinstance(node, ast.Name) and node.id not in valid_functions and node.id != "x": #if it is a name,
                                                                                            #check if is x or if it is a valid expression 
                                                                                            #that is in the dict
            raise ParseError("name not allowed")
        if isinstance(node, ast.Call): #checks if the function can be called since for example a function in terms of y is not valid in our program
            if not isinstance(node.func, ast.Name):
                raise ParseError("not a valid function to call")
            if node.func.id not in valid_functions:
                raise ParseError("function not allowed")

def compile_expression(expression: str) -> Callable[[float], float]:
    """compiles str expression into callable function
    
        Parameters:
            expression: math expression as str
        
        Return:
            function that evaluates the expression
    """

    normalized = expression.replace("^", "**") #after trying the code, we noticed that python understand powers
                                                #as **, not as ^ so we had to change if ^is written to representpower
    try: #try except method to handle errors
        tree = ast.parse(normalized, mode = "eval") #this line was added because we wrote a wong command when 
                                                    #trying the code, thinking that we wre in another part of 
                                                    #the computer and we almost messed up an OS of our computer,
                                                    #so basically we split the expression by making an ast tree
                                                    #so we cn verify each part can be analyzed correctly by our code 
                                                    #and with eval we ensure we are using an expression 100%
    except SyntaxError as e:
        raise ParseError("invalid expression") from e
    _validate_ast(tree)
    compiled = compile(tree, filename = "<expression>", mode = "eval") #compile is turning the tree into code that Python understands

    def evaluator(x: float) -> float: #we created a function basically to ensure that everything was working properly
        """introduce a value x, calculate the expression at x and control errors
        
            Parameter:
                x: value or which the expression is calculated
            
            Return:
                expression calculated at x and controls errors
        """
        scope = dict(valid_functions) #copy of the dictionary since we are going to modify it later
        scope["x"] = float(x) #adds x to the dict. key x saves value x
        try: #try except again
            value = eval(compiled, {"__builtins__": {}}, scope) #calculates the expression using the value of x
            return float(value)
        except ZeroDivisionError as e:
            raise EvaluationError("can't divide by 0") from e
        except Exception as e:  # pragma: no cover - defensive wrapper
            raise EvaluationError("expression can't be evaluated") from e
    return evaluator

def parse_polynomial(expression: str):
    """parse polynomial string into Polynomial obj

        Parameter:
            expression: polynomial as str
        
        Return:
            polynomial instance
    """

    from .functions import Polynomial #we import the class to later return an object of type polynomial
    cleaned = expression.lower().replace(" ", "") #everything lowercase and w/out spaces
    if not cleaned:
        raise ParseError("expression cannot be empty")
    terms = re.findall(r"[+-]?[^+-]+", cleaned) #divide the polynomial, the regex is basically a term that can 
                                                #have a sign + or - and then characters until the next sign
    coefficients_by_degree: dict[int, float] = {} #create dict of structure {power:coeff}

    for term in terms:
        sign = -1.0 if term.startswith("-") else 1.0
        term_by_itself = term[1:] if term.startswith(("+", "-")) else term #remove the sign and leave the term by itself
        term_by_itself = term_by_itself.replace("*", "") 

        if "x" in term_by_itself:
            coefficient_text, _, exponent_text = term_by_itself.partition("x") #we divide the polynomial in coefficient, term, power 
            coefficient = 1.0 if coefficient_text == "" else float(coefficient_text)
            exponent = 1 #exponent 1 unless stated different
            if exponent_text: #if there is something after the x
                if not exponent_text.startswith("^"):
                    raise ParseError("exponent has to be written with ^")
                try: 
                    exponent = int(exponent_text[1:]) #if we have ^something, we just use the something for the table
                except ValueError:
                    raise ParseError ("invalid exponent format")
        else: #the term doesn't have x
            coefficient = float(term_by_itself)
            exponent = 0
            #constant number
        coefficients_by_degree[exponent] = coefficients_by_degree.get(exponent, 0.0) + sign * coefficient #we add 
                                        #the polynomials with the same power to get the most simplified polynomial

    if not coefficients_by_degree:
        raise ParseError("no valid terms found")

    max_degree = max(coefficients_by_degree)
    coefficients = [0.0] * (max_degree + 1) #create list full of zeros of (max_degree + 1) eleemtns
    for exponent, coefficient in coefficients_by_degree.items(): #fill the list
        coefficients[exponent] = coefficient
    return Polynomial(coefficients)


def parse_interval_spec(spec: str) -> Interval: #recieve a string w an interval and return an object interval
    """parses string into an interval
    
      Parameter:
          spec: interval str
      
      Return:
          interval object  
    """
    match = _INTERVAL_PATTERN.fullmatch(spec) #everything has to match w the regex pattern
    if match is None:
        raise ParseError(
            "wrong interval format"
        )
    return Interval(float(match.group("left")), float(match.group("right")))
