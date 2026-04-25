from __future__ import annotations ##
import pyfiglet
import argparse #it allows to read commands from the terminal
import json #we use json for aesthetic issues  only
from typing import Any ######
from pathlib import Path
from .plotting import plot_function
from .methods_of_approx import central_difference, simpson_rule, trapezoidal_rule
from .parsers import parse_interval_spec
from .solvers import build_solver
from .text_json import build_function_from_spec
from .workflow import demo_config, run_full_report

def print_banner():
    version = "v0.1.0"

    banner = pyfiglet.figlet_format(
        "FUNCTION PARSER " + version,
        font = "slant"
    )

    print("#" * 75)
    print(banner)
    print("#" * 75)


def turn_into_dictionary(args: argparse.Namespace) -> dict[str, Any]:
    """takes the argument from CLI and creates dictionary describing the math function

    Parameters:
    args: arguments that contain the function information.

    Return:
    dictionary with the function kind and expression.
    """
    return {"kind": args.function_kind, "expression": args.expression}

def _build_parser() -> argparse.ArgumentParser:
    """defines all the commands and options available

    Returns:
        argumentparser object.
    """
    parser = argparse.ArgumentParser(
        prog = "numerical-workbench", #name of the project
        description = ".", #we can add a mini description to our project if needed
    )
    subparsers = parser.add_subparsers(dest="command", required = True) #activates the subcommands so 
                                                                    #the program can solve roots, integrate...
    # dest = "command" saves the command that has been inputted in the terminal and required = true forces to choose only one-

    demo_parser = subparsers.add_parser("show-demo-config", help = "Print a demo JSON config") ####mirar esto
    demo_parser.add_argument(
        "--kind",
        choices = ["polynomial", "expression"], #it only allows these 2 choices
        default = "polynomial", #if nothing is chosen, polynomial will be automatically selected
        help = "Choose the kind of demo configuration to print.", #text
    )
#the next lines create subcommands for a certain purpose, each one is different
    solve_parser = subparsers.add_parser("solve-root", help = "solve for a root using one method") #find a root
    solve_parser.add_argument("--function-kind", choices = ["polynomial", "expression"], required = True) #indicate the type of function to be used
    solve_parser.add_argument("--expression", required = True) #write the expression
    solve_parser.add_argument("--method", choices = ["bisection", "newton", "secant"], required = True) #choose a numeric method
    solve_parser.add_argument("--interval", required = True, nargs = 1) #select the interval
    solve_parser.add_argument("--tolerance", type = float, default = 1e-8)# precision
    solve_parser.add_argument("--max-iterations", type = int, default = 100) #limit of iterations

    integrate_parser = subparsers.add_parser("integrate", help = "Approximate a definite integral") #integrate
    integrate_parser.add_argument("--function-kind", choices =["polynomial", "expression"], required = True) #type of function
    integrate_parser.add_argument("--expression", required = True) #expression used
    integrate_parser.add_argument("--interval", required = True, nargs = 1) #interval
    integrate_parser.add_argument("--steps", type = int, default = 100) #number of intervals
    integrate_parser.add_argument("--derivative-at", type = float, default = None) #both integrates and finds derivative at a point if needed

    report_parser = subparsers.add_parser("report", help = "Execute the full workflow from a JSON config") #execute all the file from a json
    report_parser.add_argument("--config", default = None) #set a setting related to a file
    report_parser.add_argument("--output-dir", default = None, help = "change in the output directory?") #change the output directory
    return parser


def main() -> None:
    """executes CLI and runs the selected command

        Parameters:
            None

        Return:
            None
    """

    parser = _build_parser()
    args = parser.parse_args() #store what has been written in the terminal 
    print_banner()
    try:
#functioning of the commands mentioned above, basically, what happens when they are written 
        if args.command == "show-demo-config":
            print(json.dumps(demo_config(args.kind), indent = 2))
            return #generates an example config and shows it in a json format with indent 2 so the text is not extremely together
    
        if args.command == "solve-root":
            function = build_function_from_spec(turn_into_dictionary(args)) #turn the arguments into a dictionaryand creates the object
            interval = parse_interval_spec(args.interval[0]) #turns the input into an object "Interval"
            solver = build_solver(args.method, limit = args.tolerance, max_iterations = args.max_iterations) #constructs the numerical method chosen
            guesses = None
            result = solver.solve(function, interval = interval, initial_guesses=guesses) #executes the numerical method
            print(json.dumps(result.to_dict(), indent = 2))
            
            
            output_dir = Path("outputs/cli") #if the user wants to find a root we create a graph also so the result can be seen visually
            output_dir.mkdir(parents = True, exist_ok = True)
            safe_expr = args.expression.replace(" ", "").replace("*", "").replace("^", "")
            safe_expr = safe_expr.replace("/", "").replace("(", "").replace(")", "")
            plot_path = output_dir / f"{args.method}_{safe_expr}.png"
            plot_function(
                function,
                interval,
                plot_path,
                roots = [result.root] if result.converged else None
            )
            print(f"Plot saved to: {plot_path}")
            return
    
        if args.command == "integrate":
            function = build_function_from_spec(turn_into_dictionary(args)) #turn the arguments into a dictionaryand creates the object
            interval = parse_interval_spec(args.interval[0]) #turns the input into an object "Interval"
            summary = {
                "trapezoidal": trapezoidal_rule(function, interval, args.steps),
                "simpson": simpson_rule(function, interval, args.steps), # we save the result of both methods in 
                                                        #a dict in case we want to compare them later for example
            }
            if args.derivative_at is not None: #in case the user has asked for the derivative at a point
                summary["derivative"] = central_difference(function, args.derivative_at) #it is also added to the dict
            print(json.dumps(summary, indent = 2))
            return
    
        if args.command == "report":
            artifacts = run_full_report(config_path = args.config, output_directory=args.output_dir) #calls the functions that executes everything basically
            payload = { #dictionary with the pathsf the files
                "output_directory": str(artifacts.output_directory),
                "summary_markdown": str(artifacts.summary_markdown),
                "summary_json": str(artifacts.summary_json),
                "function_plot": str(artifacts.function_plot),
                "convergence_plot": str(artifacts.convergence_plot),
                "history_files": {key: str(value) for key, value in artifacts.history_files.items()},
            } #we have turned everything into a text because we were getting an error when combinining with json, so this has solved the problem
            print(json.dumps(payload, indent = 2))
            return
   
    except Exception as e:
        print(f"Error: {e}") 

if __name__ == "__main__":
    main()
