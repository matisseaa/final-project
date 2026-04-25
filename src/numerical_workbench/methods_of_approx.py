from __future__ import annotations #annotations allows to use typehints without any problem
import numpy as np #in order to do the majority of the mathematical operations that we have to use in 
                    #order to do approximated derivatives and integrals, numpy 
                    #is key and since it is not a default it has to be imported explicitly

from .exceptions import ValidationError
from .functions import MathFunction
from .models import Interval #the class "Interval" is defined in another file so in order to use it 
                            #in Simpson's and trapezoidal rule, we have to import it

def central_difference(function: MathFunction, x: float, h: float = 1e-5) -> float:
    """the three point central difference method is used to approximate the derivative of a function at a point x
        through a formula (which is defined in functions.py)

    Parameters:
        function: mathematical function which will be derivated 
        x: point where the derivative is evaluated
        h: step used in the formula of the three point central difference

    Return:
        approximate derivative value at x
    """
    if h == 0.0:
        raise ZeroDivisionError("cannot divide by 0")
        # the denominator in the formula is '2h' so dividing by zero will cause an error
    elif h < 0.0:
        raise ValidationError("h cannot be negative")
        # h has to be positive for the formula to work

    return function.derivative(x, h) #this line basically asks the function to compute its own derivative 
                                        #since each function may do it differently , and in this way, if a 
                                        #function which has an exact derivative is used, approximation will not 
                                        #be needed so the program is more efficient. Basically, this is an 
                                        #example of ploymorphism since the same method 'derivative' behaves 
                                        #differently depending on the type of function

    # the formula of the three point central difference method is defined in the functions.py file so that is 
    #why calling function.derivative, in case approximation has to be done through this method, it will be 
    #done with the formukla despite not being defined inside the function 

def trapezoidal_rule(function: MathFunction, interval: Interval, n_steps: int = 200) -> float:
    """approximates definite integrals using the trapezoidal rule, by dividing interval into
    n subintervals. Then, area under the curve is approx by summing the trapezoids

    Parameters:
        function: mathematical function which will be integrated
        interval: space where integral is approximated
        n_steps: number of subintervals

    Return:
        approximate value of the definite integral over the interval
    """

    if n_steps < 1:
        raise ValidationError("The number of steps must be at least 1") # withouat any subintervals it is 
                                                        #impossible to do the sum that bases the approximation

    xs = np.linspace(interval.left, interval.right, n_steps + 1) #each interval is delimited by two endpoints 
                                    #so the number of points will always be 1 more than the number of intervals
                                    #array
                                    
    ys = np.asarray(function(xs), dtype = float) #evaluate the function at the generated points in xs
                                                    #and store the results as floats.

    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(ys, xs)) #numpy has the trapezoidal rule already integrated so it is being called here
    return float(np.trapz(ys, xs))


def simpson_rule(function: MathFunction, interval: Interval, n_steps: int = 200) -> float:
    """approximates definite integrals using simpson rule, which normally is more accurate than 
       the trapezoidal rule. Also works with a formula

    Parameters:
        function: mathematical function which will be integrated
        interval: space where the integral is approximated
        n_steps: number of subintervals (has to be even)

    Return:
        approximate value of the definite integral over the interval
    """

    if n_steps < 2:
        raise ValidationError("Simpson's rule requires at least 2 steps.") #two intervals at least are required

    if n_steps % 2 != 0:
        raise ValidationError("Simpson's rule requires an even number of steps.") #nº of subintervals has to be even


    xs = np.linspace(interval.left, interval.right, n_steps + 1) ##
    ys = np.asarray(function(xs), dtype = float) ## same as in trapezoidal rule

    interval_width = (interval.right - interval.left) / n_steps

    
    total = ys[0] + ys[-1] + 4.0 * np.sum(ys[1:-1:2]) + 2.0 * np.sum(ys[2:-1:2]) ##
    return float((interval_width / 3.0) * total)#simpson formula
