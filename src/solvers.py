from __future__ import annotations
from abc import ABC, abstractmethod
from time import perf_counter
from typing import Iterator
from .exceptions import SolverError, ValidationError
from .functions import MathFunction
from .models import Interval, IterationRecord, RootResult


class RootSolver(ABC):
    """abstract class for ways of finding roots"""

    name = "abstract" #####################

    def __init__(self, limit: float = 1e-4, max_iterations: int = 100) -> None: #constructor
                                                                                #limit is the maximum error we have considered that the solution is good enough
        """Initializes the parameters of the solveers
        
            Parameters:
                limit: error tolerance
                max_iterations: max nº of iterations
                
            Returns:
                none
        """
        if limit <= 0.0:
            raise ValidationError("error has to be positive.")
        if max_iterations < 1:
            raise ValidationError("we need 1 iteration at least")
        self.limit = limit
        self.max_iterations = max_iterations

    @abstractmethod #child classes have to implement it
    def iterate(
        self,
        function: MathFunction,
        interval: Interval | None = None,
        initial_guesses: tuple[float, ...] | None = None, ########
    ) -> Iterator[IterationRecord]:
        """generate iteration steps
        
            Parameters:
                function: function to eval
                interval: interval
                initial_guesses: initial values
                
            Returns:
                iterator of records
        """

    def solve(
        self,
        function: MathFunction,
        interval: Interval | None = None,
        initial_guesses: tuple[float, ...] | None = None,
    ) -> RootResult:
        """runs solver until convergence or until it fails
        
            Parameters:
                function: function to eval
                interval: interval
                initial_guesses: initial values
                
            Returns:
                 rootresult w solution data
        """
        start = perf_counter() #initial moment
        history: list[IterationRecord] = [] #empty list 2 store eahc step
        converged = False #boolean we started it on false by default which will be changed later if needed
        message = "maximum iterations reached"

        try: #try except method for errors
            for record in self.iterate( #each record is an iteration
                function,
                interval = interval,
                initial_guesses = initial_guesses,
            ):
                history.append(record) #save the ctual record in the history
                smallerror = abs(record.fx) <= self.limit #check if the error is small enough
                step_small = record.error is not None and record.error <= self.limit #also check if the error 
                                                                                    #is small enough to consider
                                                                                    #that the method has converged
                if smallerror or step_small:
                    converged = True #change of the boolean
                    message = "limit reached"
                    break
        except SolverError:
            raise
        except Exception as e:
            raise SolverError("solver failure") from e

        if not history: 
            raise SolverError("no iterations produced")

        last_record = history[-1] #last register which will be used for the final result
        return RootResult(
            solver_name = self.name, #name of method
            root = last_record.x, #last x value calculated
            converged = converged, #the boolean to see if the method worked or not
            iterations = len(history),
            final_error = abs(last_record.fx),
            time_taken = perf_counter() - start, #time the method took
            history = history, #whole record to graph it later
            message = message)

class BisectionSolver(RootSolver): #since it is a method to solve roots it inherits from rootsolver
    """bisection method to find roots 

    1. start with interval where the function changes sign
    2. find midpoint 
    3. check in which half is the root
       - sign changes between left and midpoint, keep that half
       - otw, keep the half between midpoint and right
    4. repeat the process with this new interval
    5. stop when interval is small enough and 
    6. return midpoint as root

    """
    name = "bisection"

    def iterate( #use the abstract method from before
        self,
        function: MathFunction,
        interval: Interval | None = None,
        initial_guesses: tuple[float, ...] | None = None,
    ) -> Iterator[IterationRecord]:
        """perform bisection iteratiosn
        
            Parameters:
                function: function to solve
                interval: interval where the root is
                
            Returns:
                iterator of records
        """
        del initial_guesses

        if interval is None:
            raise SolverError("interval needed")

        left = interval.left
        right = interval.right
        f_left = float(function(left))
        f_right = float(function(right))

        if f_left == 0.0: #left endpoint is a root
            yield IterationRecord(1, left, f_left, error = 0.0, text = "left endpoint is root") #no error because we have the exact answer
            return #process ends because root is found
        if f_right == 0.0: #right endpoint is a root
            yield IterationRecord(1, right, f_right, error = 0.0, text = "right endpoint is root")
            return
        if f_left * f_right > 0.0: #to check is all the function is positive or negative which can't be for this method
            raise SolverError("no sign change")

        for iteration in range(1, self.max_iterations + 1):
            midpoint = (left + right) / 2.0
            f_mid = float(function(midpoint))
            error = abs(right - left) / 2.0 #we assume the error as half of the interval as the oot is somewhere there
            yield IterationRecord(
                iteration = iteration,#number of iteration
                x = midpoint, #the midpoint is the approx value of the root
                fx = f_mid, #how far we are from 0
                error = error)
            #check in which half the root is
            if f_left * f_mid <= 0.0:
                right = midpoint
                f_right = f_mid
            else:
                left = midpoint
                f_left = f_mid

class NewtonSolver(RootSolver): #since it is a method to solve roots it inherits from rootsolver
    """newton method to find roots
    
    follows the equation x_(n+1) = x_n - (((f_xn))/(f'_xn))
    """

    name = "newton"

    def iterate( #use the abstract method from before
        self,
        function: MathFunction,
        interval: Interval | None = None,
        initial_guesses: tuple[float, ...] | None = None, #x_n
    ) -> Iterator[IterationRecord]:
        """perform newton method
        
            Parameters:
                function: function to solve
                interval: interval
                initial_guesses: intial value
                
            Returns:
                iterator of records
        """
        if initial_guesses: 
            current = initial_guesses[0] #if an initial point is given the process starts from that point
        elif interval is not None: #if a point is not given but we have an interval the midpoint is used
            current = interval.midpoint()
        else:
            raise SolverError("initial points or interval missing")

        for iteration in range(1, self.max_iterations + 1): #until the method finishes or we reach the max iterations
            value = float(function(current)) #f(x_n)
            derivative = function.derivative(current) #f'(x_n)
            if abs(derivative) < 1e-5: #if derivative is to small newton fails:
                raise SolverError("derivative too close to zero")
            next_value = current - value / derivative #formula
            next_fx = float(function(next_value)) #f(x_(n+1))
            yield IterationRecord(
                iteration = iteration,
                x = next_value,
                fx = next_fx,
                error = abs(next_value - current),
            )
            current = next_value #update the actual point


class SecantSolver(RootSolver):
    """secant method using two previous approximations
    
    follows the equation x_(n+1) = x_n - (f_xn)*((x_n - x_(n-1))/(f(x_n)-f(x_(n-1))))
    
    
    """
    name = "secant"

    def iterate( #use the abstract method from before
        self,
        function: MathFunction,
        interval: Interval | None = None,
        initial_guesses: tuple[float, ...] | None = None,
    ) -> Iterator[IterationRecord]:
        """perform secant method iterations
        
            Parameters:
                function: function to solve
                interval: interval
                initial_guesses: intial values
                
            Returns:
                iterator of records
        """
        if initial_guesses and len(initial_guesses) >= 2: #secant method works with at least 2 initial guesses
            previous, current = initial_guesses[0], initial_guesses[1] 
        elif interval is not None: #if no initial guesses use interval
            previous, current = interval.left, interval.right
        else:
            raise SolverError("two initial guesses or interval needed")

        f_previous = float(function(previous))
        f_current = float(function(current))

        for iteration in range(1, self.max_iterations + 1):
            denominator = f_current - f_previous
            if abs(denominator) < 1e-10:
                raise SolverError("fail two consecutive values match") #cant divide by 0 so if the values are 
                                                                        #extremely close it won't work
            next_value = current - f_current * (current - previous) / denominator
            next_fx = float(function(next_value))
            yield IterationRecord(
                iteration = iteration,
                x = next_value,
                fx = next_fx,
                error = abs(next_value - current))
            previous, current = current, next_value #update values the actual value is the last one one and the
                                                    #next one is the actual
            f_previous, f_current = f_current, next_fx #also the functions

def build_solver(
    name: str,
    limit: float = 1e-5,
    max_iterations: int = 100,
    tolerance: float | None = None,
) -> RootSolver:
    """build solver from name
    
        Parameters:
            name: solver name
            limit: error tolerance
            max_iterations: max nº of iterations
            
        Returns:
            rootsolver instacne
    """

    if tolerance is not None:
        limit = tolerance

    adaptedname = name.strip().lower()
    mapping = {
        "bisection": BisectionSolver,
        "newton": NewtonSolver,
        "secant": SecantSolver,
    }
    try:
        return mapping[adaptedname](limit = limit, max_iterations = max_iterations) #search for the class calls 
                                                                                        #the function as if it 
                                                                                        #was a class to create 
                                                                                        #the object
    except KeyError as e:
        raise ValidationError("choose between bisection, newton, secant") from e
