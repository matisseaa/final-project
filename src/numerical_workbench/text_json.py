from __future__ import annotations
import csv #allows to read and write csv
import json
from pathlib import Path
from typing import Any, Mapping
from .exceptions import ConfigurationError
from .functions import ExpressionFunction, MathFunction
from .parsers import parse_polynomial

def ensure_directory(path: str | Path) -> Path: #avoid file not found or errors like that
    """ensures a dict exists and return it as path
    
        Parameters:
            path: mdirectory path

        Return:
            path object
    """
    target = Path(path) #turns the string or path into a Path object
    target.mkdir(parents = True, exist_ok = True) #parents makes intermmediate folders if needed and 
                                                    #exist_ok makes that the code does not provide an error 
                                                    #if the folder already exists
    return target


def load_json(path: str | Path) -> dict[str, Any]: #turn a json into a dict
    """load json file into dictionary
    
        Parameters:
            path: path to json file

        Return:
            dict with the contents of file
    """

    with Path(path).open("r", encoding = "utf-8") as handle: #opens the file in lecture mode. utf8 is the standard
                                                            #text format which we had to put since without the 
                                                            #encoding=utf8 the function was ot working and handle
                                                            #is the file opened of course
        return json.load(handle)


def save_json(data: Mapping[str, Any], path: str | Path) -> Path: #put data in an appealing way 
    """ssaves data as json file
    
        Parameters:
            data: data 2 save
            path: output file path

        Return:
            path to saved file
    """
    target = Path(path)
    with target.open("w", encoding = "utf-8") as handle: #open file in writing mode
        json.dump(dict(data), handle, indent = 2) #save data in json format ensuring it is a dict. we added hthe indent because without it when the text too together 
    return target

def save_rows_to_csv(rows: list[dict[str, Any]], path: str | Path) -> Path:
    """save rows as csv table format
    
        Parameters:
            rows: list of dicts
            path: output file path

        Return:
            path to saved file
    """

    target = Path(path)
    if not rows: #if there is no data we craete a basic csv because we were having an error when writing on 
                #an empty csv
        fieldnames = ["message"]
        rows = [{"message": "no rows available"}]
    else: #there is data
        fieldnames = list(rows[0].keys()) #columns are the keys of the first dict
    with target.open("w", encoding = "utf-8", newline = "") as handle:
        writer = csv.DictWriter(handle, fieldnames = fieldnames) #we had t create a csv writerthat works w dicts
        writer.writeheader() #write name of columns
        writer.writerows(rows) #write all the rows
    return target

def save_text(text: str, path: str | Path) -> Path:
    """saves ant yext to a file
    
       Parameters:
           text: content to save
           path: output file path

       Return:
           path to saved file 
    """
    target = Path(path)
    with target.open("w", encoding="utf-8") as handle:
        handle.write(text)
    return target

def build_function_from_spec(spec: Mapping[str, Any]) -> MathFunction:
    """create function object from specification
    
        Parameters:
            spec: dict with data

        Return:
            mathfunction instance 
    """

    kind = str(spec.get("kind", "")).strip().lower() #we try to obtain the key "kind" and if not we just use ""
    expression = spec.get("expression") #obtain expression from the dict
    if not expression:
        raise ConfigurationError("expression missing")
    if kind == "polynomial":
        return parse_polynomial(str(expression)) #parsed polynomial
    if kind == "expression":
        return ExpressionFunction(str(expression)) #expression
    raise ConfigurationError("kind must be polynomial or expression") #if not polyomial nor expression
