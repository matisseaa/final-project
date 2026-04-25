from __future__ import annotations
from abc import ABC, abstractmethod #enables us to create an abstract class and methods 
                                    #that will be implemented by subclasses
from typing import Iterable #we added iterable to provide more flexibility when inputting th coefficients
import numpy as np
from .models import Interval

class MathFunction(ABC):
    """abstract base class(inherites from ABC) for scalar functions."""

    def __init__(self, name: str) -> None: #constructor of the class
       """initializes object with a name

            Parameters:
                name: name of the object

            Return:
                None""" 
       self.name = name
        

    @abstractmethod #so any subclass of MathFunction implements this function
    def evaluate_scalar(self, x: float) -> float: #and can be evaluated at a scalar pt
        """evaluate the function at a scalar point
        
            Parameters:
                x: sclar point
                
            Return:
                None     
        """

    def __call__(self, x: float | np.ndarray) -> float | np.ndarray: #it allows an object to be called as a function
                                                                #we have basically done it so function are 
                                                                #treated like f(x) rather than 
                                                                #f.evaluate_scalar(x) which is not very natural
        """evaluates function on a scalar or numpy array
        
            Parameters:
                x: value or array

            Return:
                function value at x
        """

        if isinstance(x, np.ndarray): #check if x is is an array
            vectorized = np.vectorize(self.evaluate_scalar, otypes = [float]) #turns the function that can only 
                                                                            #receive scalars to a function that 
                                                                            #understands arraysand we add float as the output datatype
            return vectorized(x) #if x is an array, it applies the function to each element andeturns another array
        return self.evaluate_scalar(float(x)) #if x is not an array, evaluate_scalar is called and returns the scalar result

    def derivative(self, x: float, h: float = 1e-5) -> float: #approximation of derivative at x
        """approximate the derivative at x with the central difference formula
        
            Parameters:
                x: point
                h: step size
    
            Return:
                approx derivative at x
        """

        return float(
            (self.evaluate_scalar(x + h) - self.evaluate_scalar(x - h)) / (2.0 * h)) #three pt central difference formula

    def sample(self, interval: Interval, values: int = 100) -> tuple[np.ndarray, np.ndarray]: #point generator to test the function
        """samples the function over interval
        
            Parameters:
                interval: interval to sample
                values: nº of pounts
    
            Return:
                arrays of x
                f(x) values
        """
        xs = np.linspace(interval.left, interval.right, values) #creates de array of values uniformly distributed along the interval
        ys = np.asarray(self(xs), dtype = float) #evaluates the function at the points which we called "values" 
                                                    #with the result being an array of floats as we want
        return xs, ys

    def description(self) -> str:
        """retuns description of the function (like the expression we can read and understand)
        
              Parameters:
                  none
      
              Return:
                  function description 
        """
        return self.name

    def __str__(self) -> str: #dunder method that calls description()
        """retuns string representation of object
        
              Parameters:
                  none
      
              Return:
                  string representation of object 
        """
        return self.description() 

class Polynomial(MathFunction): #calss that represents a polynomial
    """represents a polynomial by coefficients (increasing degree order) """ # (1,2,3) would be 1 + 2x + 3x^2

    def __init__(self, coefficients: Iterable[float]) -> None:
        """initialize polynomial with given coeff
        
              Parameters:
                  coefficients: iterable of poly coeff
      
              Return:
                  none 
        """
        trimmed = self._trim_coefficients(tuple(float(value) for value in coefficients)) #tuple with the coefficients 
                                                                                        #as floats with the 0 removed
        self.coefficients = trimmed #save the new coeff
        super().__init__("Polynomial") #pass the name to the constructor of the parent class

    @staticmethod #method related to the class not to the object
    def _trim_coefficients(coefficients: tuple[float, ...]) -> tuple[float, ...]: #receives a tuple of coeffs and
    # returns another tupple with coefficients #but in this case removing the 0 if the first tuple contains zeros in it since a polynomial with a coefficient 0  can be ignored
        """remove zero coefficients from tuple
        
              Parameters:
                  coefficients: tuple of coeffs
      
              Return:
                  tuple without zero coefficients 
        """
        values = list(coefficients) or [0.0] #we turn the tuple into a list to do the values.pop later. With a tuple it doesn't work
        while len(values) > 1 and abs(values[-1]) < 1e-10: #there has to be at least 1 coeff and we eliminate all
                                #the coefficients which are extremely close to 0 since they are almost irrelevant
            values.pop() #eliminate the last coefficient until it is not 0 or close
        return tuple(values) #turn the result into a tuple again

    @property #############################################
    def degree(self) -> int:
        """return degree of polynomial
        
              Parameters:
                  none
      
              Return:
                  polynomial degree 
        """
        return len(self.coefficients) - 1 #since the 0 have been eliminated before, the degree of the polynomial 
                                            #is the number of terms -1

    def evaluate_scalar(self, x: float) -> float: #evaluate the function at a point through horner's rule
        """evaluate polynomial at a point using Horner's rule
        
            Parameters:
                x: point where polynomial is evaluated
    
            Return:
                polynomial value at x
        """
        result = 0.0 #cummulative result
        for coefficient in reversed(self.coefficients): ##
            result = result * x + coefficient ## Horner's method
        return float(result)

    def derivative_polynomial(self) -> "Polynomial":
        """returns the expression of the derivative
        
            Parameters:
                none
    
            Return:
                polynomial representing derivative
        """
        if self.degree == 0:
            return Polynomial((0.0,)) #the derivative of a constant polynomialis 0
        derived = [index * coefficient for index, coefficient in enumerate(self.coefficients)][1:] #traditional way of doing the derivative (a_n x^n --> n a_n x^(n-1))
        return Polynomial(derived)

    def derivative(self, x: float, h: float = 1e-5) -> float:
        """evaluates exact derivative polynomial at x
        
            Parameters:
                x: point where derivative is evaluated
                h: step
    
            Return:
                derivative value at x
        """
        return self.derivative_polynomial().evaluate_scalar(x) #uses both the derivative_polynomial to create the
                                                            #expression of the derivative and evaluate_scalar 
                                                            #to evaluate the derivative at a point x

    def __add__(self, other: "Polynomial") -> "Polynomial": #dunder method to add 2 polynomilas
        """adds two polynomials
        
           Parameters:
               other: polynomial to add
   
           Return:
               resulting polynomial
        """
        max_len = max(len(self.coefficients), len(other.coefficients)) #we added this line because the sum was 
                                                                    #not working when the two polynomials had a 
                                                                    #different number of coefficients
                                                                    
        left = list(self.coefficients) + [0.0] * (max_len - len(self.coefficients)) #so we made the first polynomial
                                                                                    #a list to be mutable and add
                                                                                    #zeros until reaching the 
                                                                                    #maximum length
                                                                                    
        right = list(other.coefficients) + [0.0] * (max_len - len(other.coefficients))#same with the second
        return Polynomial(a + b for a, b in zip(left, right)) #zip pairs the coefficients with same index

    def __sub__(self, other: "Polynomial") -> "Polynomial": #dunder method with same logic as __add__
        """substracts two polynomials
        
            Parameters:
                other: polynomial to substract
    
            Return:
                resulting polynomial
        """
        max_len = max(len(self.coefficients), len(other.coefficients))
        left = list(self.coefficients) + [0.0] * (max_len - len(self.coefficients))
        right = list(other.coefficients) + [0.0] * (max_len - len(other.coefficients))
        return Polynomial(a - b for a, b in zip(left, right)) 

    def __mul__(self, other: float | "Polynomial") -> "Polynomial": #dunder method that enables to multiply a 
                                                                    #polynomial by scalar or polynomial
        """multiplies two polynomials
        
            Parameters:
                other: polynomial or scalar to multiply
    
            Return:
                resulting polynomial
        """
        if isinstance(other, (int, float)):#check if other is a number
            return Polynomial(coefficient * float(other) for coefficient in self.coefficients) #multiply each coefficient by the scalar
        degree = self.degree + other.degree #if other is a polynomial sum the degrees of the polynomials
        result = [0.0] * (degree + 1) #we had to add this line to store the results, which is a list of n+1 
                                        #coeficients with n being the degree because without we were getting an 
                                        #error like the result was not appearing
        for i, left in enumerate(self.coefficients):
            for j, right in enumerate(other.coefficients):
                result[i + j] += left * right #multiplication of polynomials as we know by expanding the brackets basically
        return Polynomial(result)

    def __rmul__(self, other: float) -> "Polynomial": #dunder method which allows to multiplicate scalar by 
                                                        #polynomial and not only polynomial by scalar which was 
                                                        #the case if we only had the __mul__ function
        """multiplies two polynomials
        
            Parameters:
                other: scalar to multiply by
    
            Return:
                resulting polynomial
        """
        return self * other

    def __eq__(self, other: object) -> bool: #dunder method to see if two polynomials are the same
        """check if two polynomials are equal
        
            Parameters:
                other: object to compare
    
            Return:
                true if equal, false if not
        """
        if not isinstance(other, Polynomial): #if other is not a polynomial, it cannot be the same 
                                                #polynomial as the other one obviously
            return False
        if len(self.coefficients) != len(other.coefficients): #if two polynomials have a different number of coefficients they cannot be the same
            return False
        return np.allclose(self.coefficients, other.coefficients) #we use allclose instead of == because it 
                                                                    #allows for small differences between numbers 
                                                                    #so 1 and 1.0000001 is treated as equal

    def __str__(self) -> str: #dunder method that defines how the poly turns into txt
        """returns string representation of polynomial
        
            Parameters:
                none
    
            Return:
                polynomial as formatted str
        """
        pieces: list[str] = [] #empty list to store the terms
        for exponent, coefficient in reversed(list(enumerate(self.coefficients))): # iterate over coefficients with descending degree getting (exponent, coefficient)
            if abs(coefficient) < 1e-15: #ignore coefficients that are 0 or extremelly close
                continue
            sign = "-" if coefficient < 0 else "+" #save the sign of the term
            magnitude = abs(coefficient) #save the rest of the term
            if exponent == 0:
                core = f"{magnitude}"
            elif exponent == 1:
                if abs(magnitude - 1.0) < 1e-10: #if coeff is 1
                    core = "x"
                else:
                    core = f"{magnitude}x" #if coeff is not 1
            else: #exponent bigger than 1
                if abs(magnitude - 1.0) < 1e-10:
                    core = f"x^{exponent}"
                else:
                    core = f"{magnitude}x^{exponent}"
            pieces.append((sign, core)) #fill the list
        if not pieces:
            return "0" #if everything were 0 return 0 of course
        first_sign, first_core = pieces[0]
        rendered = first_core if first_sign == "+" else f"-{first_core}" #we wanted to be a bit picky and if the 
                                                                        #first term, so the term with the highest
                                                                        #degree is positive, don't show the + sign 
                                                                        #as it is like redndant
        for sign, core in pieces[1:]:
            rendered += f" {sign} {core}" #add the rest
        return rendered

    def description(self) -> str:
        """returns descriptive string of polynomial
        
            Parameters:
                none
    
            Return:
                descriptive str
        """
        return f"Polynomial: {self}"


class ExpressionFunction(MathFunction): #class that also inherits from mathfunction which creates functions froma string
    """creates functions from strings"""

    def __init__(self, expression: str) -> None: #receives the string with the expression
        """initialize function from expression str
        
            Parameters:
                expression: math expression as str
    
            Return:
                none
        """
        from .parsers import compile_expression #import from our file
        self.expression = expression
        self._evaluator = compile_expression(expression)
        super().__init__("ExpressionFunction") #calls the parent class constructor

    def evaluate_scalar(self, x: float) -> float:
        """evaluate the stored expression at x"
        
        Parameters:
            x: input value

        Return:
            expression value at x
        """
        return self._evaluator(x)

    def description(self) -> str:
        """returns descriptive string of polynomial
        
            Parameters:
                none
    
            Return:
                descriptive str
        """
        return f"Expression: {self.expression}"
