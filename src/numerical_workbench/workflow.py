from __future__ import annotations
from pathlib import Path
from time import perf_counter
from typing import Any
from .methods_of_approx import central_difference, simpson_rule, trapezoidal_rule
from .decorators import timed
from .text_json import (
    build_function_from_spec,
    ensure_directory,
    load_json,
    save_json,
    save_rows_to_csv,
    save_text,
)
from .models import Interval, ReportArtifacts, RootResult
from .plotting import plot_convergence, plot_function
from .solvers import build_solver


def demo_config(kind: str = "polynomial") -> dict[str, Any]: #kind is the type of function basically
    """returns a demo config dict
    
      Parameters:
          kind: type of function

      Return:
          config dictionary  
    """

    if kind == "expression": #this is not a polynomial
        function = {"kind": "expression", "expression": "cos(x) - x"} #example expression
        root_interval = {"left": 0.0, "right": 1.0} 
        secant_guesses = [0.0, 1.0] #initial points 4 secant method
        initial_guess = 0.6 #initual point for newton method
        plot_interval = {"left": -1.0, "right": 1.5} #interval to draw the func
    
    else:
        function = {"kind": "polynomial", "expression": "x^3 - x - 2"} #polynomial
        root_interval = {"left": 1.0, "right": 2.0}
        secant_guesses = [1.0, 2.0]
        initial_guess = 1.5
        plot_interval = {"left": 0.0, "right": 2.0}

    return { #eturns in a dictionay
        "function": function,
        "roots": {
            "methods": ["bisection", "newton", "secant"],
            "interval": root_interval,
            "initial_guess": initial_guess,
            "secant_guesses": secant_guesses,
            "limit": 1e-10,
            "max_iterations": 50,
        },
        
        "calculus": { #additional things we have been adding in previous files that can be very useful as extra info
            "interval": plot_interval,
            "derivative_at": initial_guess, #point where to calculate the derivative
            "steps": 50,
        },
        "report": { #settings for plots mainly
            "plot_interval": plot_interval,
            "plot_points": 50,
            "output_directory": "outputs/demo", #file to save results
        },
    }

def create_object_interval(data: dict[str, Any]) -> Interval: #turn a dict into an object interval
    """creates interval object from dictionary
    
        Parameters:
            data: dictionary with interval bounds

        Return:
            interval object
    """
    return Interval(float(data["left"]), float(data["right"]))


def _solver_initial_guesses(method: str, roots_section: dict[str, Any]) -> tuple[float, ...] | None:
    """returns the number of initial guesses for a given method
    
        Parameters:
            method: method name
            roots_section: config data

        Return:
            tuple of initial guesses or none
    """
    
    if method == "newton": 
        return (float(roots_section["initial_guess"]),) #tuple w 1 value. without the , we were not getting a tuple so we added it
    if method == "secant":
        first, second = roots_section["secant_guesses"] #secant needs two intial guesses
        return (float(first), float(second)) #tuple w 2 values
    return None #bisection does not need initial guess

def resultstxt(
    function_description: str,
    derivative_point: float,
    derivative_value: float,
    trapezoid_value: float,
    simpson_value: float,
    results: list[RootResult],
) -> str:
    """format results into a text report
    
        Parameters:
            function_description: function description
            derivative_point: point where derivated is evaluated
            derivative_value: derivative result
            trapezoid_value: trapezoidal result
            simpson_value: simpson result
            results: list of roots

        Return:
            formatted txt str
    """
    
    lines = [
        "report", #title
        "",
        f"function: `{function_description}`", #func description
        "",
        "results after finding roots",
        "",
        "| method | converged | root | iterations | final error |", #table
        "|---|---:|---:|---:|---:|", ]
    
    for result in results: #iterate through the three numerical methods
        lines.append(
            f"| {result.solver_name} | {result.converged} | {result.root:.4f} | "
            f"{result.iterations} | {result.final_error:.3e} |")
    
    lines.extend([
            "",
            "summary",
            "",
            f"derivative at x = {derivative_point:.4f}: {derivative_value:.5f}",
            "",
            f"trapezoidal estimate: {trapezoid_value:.4f}",
            "",
            f"simpson estimate: {simpson_value:.4f}",
            "",])
    return "\n".join(lines) #change of line so it is more legible

@timed
def run_full_report( #main funciton of the whole code which has everything
    config_path: str | Path | None = None,
    config: dict[str, Any] | None = None,
    output_directory: str | Path | None = None,
) -> ReportArtifacts:
    
    """runs the full workflow and generates files
    
        Parameters:
            config_path: optional path to config fale
            config: config dict
            output_directory: output folder path
            
        Returns:
            ReportArtifacts with output
        """

    start = perf_counter()

    if config is None:
        config = demo_config() #if config not given use the demo
    if config_path is not None:
        config = load_json(config_path) #if a file is given it loads it

    function = build_function_from_spec(config["function"]) #build the real math function
    #we divide the config in 3 ----> roots, calculus and report
    roots_section = config["roots"]
    calculus_section = config["calculus"]
    report_section = config["report"]

    root_interval = create_object_interval(roots_section["interval"])
    calculus_interval = create_object_interval(calculus_section["interval"])
    plot_interval = create_object_interval(report_section["plot_interval"])

    target_directory = ensure_directory(output_directory if output_directory is not None 
                                        else report_section["output_directory"]) #ensure the folder exists, and use it if so, and create it if not
    limit = float(roots_section.get("limit", 1e-5)) #precision
    max_iterations = int(roots_section.get("max_iterations", 100)) #max iterations
    method_names = [str(name).lower() for name in roots_section["methods"]] #bisection, newton, secant
    #initialize st of results and dict with the files of record
    results: list[RootResult] = []
    history_files: dict[str, Path] = {}
    
    for method_name in method_names: #iterate through each method
        solver = build_solver(method_name, limit = limit, max_iterations = max_iterations) #create the appropiate solver
        guesses = _solver_initial_guesses(method_name, roots_section)
        result = solver.solve(function, interval = root_interval, initial_guesses = guesses) #execute the whole method
        results.append(result) #save the result in the list
        history_files[method_name] = save_rows_to_csv( #save everyiteration in a csv
            result.history_rows(), target_directory / f"{method_name}_history.csv",
        )

    derivative_point = float(calculus_section["derivative_at"])
    derivative_value = central_difference(function, derivative_point) #derivative at a point
    integration_steps = int(calculus_section.get("steps", calculus_section.get("integration_steps", 100)))
    trapezoid_value = trapezoidal_rule(function, calculus_interval, integration_steps) #integral with trapeoid
    simpson_value = simpson_rule(function, calculus_interval, integration_steps) #integral with simpson

    function_plot = plot_function( #plot function and roots
        function,
        plot_interval,
        target_directory / "functionplot.png",
        roots = [result.root for result in results],
        num_points = int(report_section.get("plot_points", 100)),
    )
    convergence_plot = plot_convergence(results, target_directory / "plotofconvergenceofmethods.png") #plot how
                                                #methods converge so get closer and closer to the exact answer

    summary_dict = { 
        "function": str(function),
        "derivative_at": derivative_point,
        "derivative_value": derivative_value,
        "trapezoidal_integral": trapezoid_value,
        "simpson_integral": simpson_value,
        "solvers": [result.to_dict() for result in results],
        "workflow_timetaken": perf_counter() - start,
    }
    
    summary_json = save_json(summary_dict, target_directory / "summary.json") #save the summary as a json file
    summary_markdown = save_text( #save the summary as text as said before in this file
        resultstxt(
            str(function),
            derivative_point,
            derivative_value,
            trapezoid_value,
            simpson_value,
            results,
        ),
        target_directory / "summary.md",
    )

    return ReportArtifacts( #returns an object with all the key information
        output_directory = target_directory,
        summary_markdown = summary_markdown,
        summary_json = summary_json,
        function_plot = function_plot,
        convergence_plot = convergence_plot,
        history_files = history_files,
    )
