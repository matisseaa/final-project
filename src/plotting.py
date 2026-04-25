from __future__ import annotations
from pathlib import Path
from typing import Sequence #the resuls of the numerical methods will be an ordered collection of numbers
import matplotlib #for graphs
matplotlib.use("Agg") #we ran the code in a computer without it and the terminal did not graph correctly because
                     #it was not supporting graphs and many windows were being created and the system colapsed
import matplotlib.pyplot as plt #for graphs
import numpy as np

from .functions import MathFunction
from .models import Interval, RootResult


def plot_function(
    function: MathFunction, #expression to draw
    interval: Interval,
    path: str | Path, #path to save the mage produced
    roots: Sequence[float] | None = None, #list of roots found
    num_points: int = 100,
) -> Path:
    """plot function and saves figure
    
        Parameter:
            function: func to plot
            interval: plotting interval
            path: output file path
            roots: root values
            num_points: nº of points
                
        
        Return:
            path to saved plot
    """

    xs, ys = function.sample(interval, values = num_points) #ask the function t calculate pts 
                                                            #in an interval. xs shows values of x, ys values of f(x)
    figure, axis = plt.subplots() #creates figure and axis
    axis.plot(xs, ys, label = str(function)) #plots and adds a label w the expresion 
    axis.axhline(0.0)
    axis.set_xlabel("x")
    axis.set_ylabel("f(x)")
    axis.set_title("function plot") #title
    if roots: #if there are roots
        root_values = np.asarray(list(roots), dtype = float) #turn the list of roots into a float numpy array so
                                                            #they can be drawn. It basically did not allow us to 
                                                            #graph them when we were not using this line so we addede it
        
        axis.scatter(root_values, np.zeros_like(root_values), label = "roots") #we craete an array of zeros so 
                                                                                #we can graph the 
                                                                                #roots as (x,y) = (root, 0)
    axis.legend()
    figure.tight_layout() #we had to look up this command as some of the graphs were getting cut
    target = Path(path)
    figure.savefig(target) #save the image in the path
    plt.close(figure) #we were getting too many graphs opened when trying the code so we clean after the image is saved
    return target


def plot_convergence(results: Sequence[RootResult], path: str | Path) -> Path:
    """draws how the error evloves
    
        Parameters:
            results: sequence of root results
            path: output file path
        
        Return:
            path to saved plot
    """

    figure, axis = plt.subplots()
    for result in results:
        iterations = [record.iteration for record in result.history] #list with the steps of the method which 
                                                                        #will be the x axis
       
        error_in_eachstep = [max(abs(record.fx), 1e-12) for record in result.history] #we do the magnitude of 
                                                                                    #the value of f(x) and then 
                                                                                    #we use max() to prevent the 
                                                                                    #error being 0
        axis.plot(iterations, error_in_eachstep, marker="o", label = result.solver_name) #we added the marker = "o" to see the points and not only the line in the graph
    axis.set_xlabel("Iteration")
    axis.set_ylabel("error")
    axis.set_title("Residual convergence")
    axis.set_yscale("log")
    axis.legend()
    figure.tight_layout()
    target = Path(path)
    figure.savefig(target)
    plt.close(figure)
    return target


def errorplot(results: Sequence[RootResult], path: str | Path) -> Path:
    """compatibility wrapper for the older function name."""
    return plot_convergence(results, path)
