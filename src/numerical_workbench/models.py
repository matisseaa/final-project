from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from .exceptions import ValidationError

@dataclass(frozen = True) #we have looked up the best way to reduce code and we found out datclasses whih suit our project perfectly
class Interval:
    """closed interval so left<=x<=right"""
    left: float
    right: float

    def __post_init__(self) -> None: #method used in dataclasses that goes after the init which is done automatically
        """validate intervalfter initialization
        
            Parameters:
                none
                
            Returns:
                none
        """
        if self.left >= self.right: #interval has to be ascendent
            raise ValidationError("we need left < right.")

    def width(self) -> float:
        """returns the interval width
        
            Parameters:
                none
                
            Returns:
                interval width
        """
        return self.right - self.left

    def midpoint(self) -> float:
        """returns the midpoint
        
            Parameters:
                none
                
            Returns:
                midpoint of the interval
        """
        return (self.left + self.right) / 2.0

    def contains(self, value: float) -> bool:
        """checks if a value is inside the interval
        
            Parameters:
                value: value to check
                
            Returns:
                true if inside, faslse if not
        """
        return self.left <= value <= self.right

    def as_tuple(self) -> tuple[float, float]: #we were getting an error when importing Interval somewhere as 
                                            #the endpoints were not a tuple so we designed this and the error 
                                            #stopped appearing
        """Returns endpoints as tuple
        
            Parameters:
                none
                
            Returns:
                tuple with endpoints
        """
        return (self.left, self.right)


@dataclass
class IterationRecord: 
    """returns records of an algorithm"""
    iteration: int
    x: float
    fx: float #f(x)
    error: float | None = None #there can be an error but there can also not be an error
    text: str = ""
    extrainfo: dict[str, float] = field(default_factory = dict) #we had to add field(default_factory = dict) 
                                                                #because all the instantiations were sharing the
                                                                #same dict and everything got messy 

    def to_row(self) -> dict[str, Any]: #key has to be a string and the value can be any datatype
        """turn record into a dictionary
        
            Parameters:
                none
                
            Returns:
                dict represejntation of the record
        """

        row: dict[str, Any] = {
            "iteration": self.iteration,
            "x": self.x,
            "fx": self.fx,
            "error": self.error,
            "text": self.text,
        }
        row.update(self.extrainfo) #we had to put this outside because it was not adding the info when putting it inside row
        return row


@dataclass
class RootResult: #summary of the process basically
    """result of the algorithm to find the roots"""
    solver_name: str #name of method
    root: float #rooot found
    converged: bool #did the algorithm work
    iterations: int
    final_error: float
    time_taken: float
    history: list[IterationRecord] #saves all the iterations as a list
    message: str = ""

    @property
    def elapsed_seconds(self) -> float:
        """compatibility alias for older code."""
        return self.time_taken

    def history_rows(self) -> list[dict[str, Any]]:
        """returns history as list of rows
        
            Parameters:
                none
                
            Returns:
                list of dicts
        """
        rows = []
        for record in self.history:
            rows.append(record.to_row())
        return rows

    def to_dict(self) -> dict[str, Any]:
        """turns result into a dict
        
            Parameters:
                none
                
            Returns:
                dictionaty w result data
        """
        return {
            "solver_name": self.solver_name,
            "root": self.root,
            "converged": self.converged,
            "iterations": self.iterations,
            "final_error": self.final_error,
            "time_taken": self.time_taken,
            "message": self.message,
        }


@dataclass(frozen = True) #we make the object immutable so the path is not changed after being generated
class ReportArtifacts:
    """path of the files generated"""

    output_directory: Path
    summary_markdown: Path
    summary_json: Path
    function_plot: Path
    convergence_plot: Path
    history_files: dict[str, Path]

    @property
    def summary_report(self) -> Path:
        """compatibility alias for older code."""
        return self.summary_markdown
