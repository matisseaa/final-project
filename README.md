# Numerical Workbench
A Python toolkit for numerical methods including root finding, integration, and function visualization.

## Description
This project implements a numerical computation toolkit in Python using an object-oriented design.

It supports:
- Root-finding algorithms (Bisection, Newton, Secant)
- Numerical differentiation and integration
- Function parsing from strings
- Visualization of functions and convergence
- Command-line interface (CLI)

---

## Features

### Root Finding
- Bisection method
- Newton method
- Secant method

### Calculus
- Central difference derivative approximation
- Trapezoidal rule integration
- Simpson’s rule integration

### Utilities
- Expression parsing (safe evaluation)
- Polynomial class with full operations
- Plotting of:
  - Functions
  - Convergence of methods

### CLI
Run computations directly from terminal.

---

## Project Structure
final-project/
│── src/
│ └── numerical_workbench/
│ ├── functions.py
│ ├── solvers.py
│ ├── plotting.py
│ └──workflow.py
│
│── tests/
│── README.md
│── setup.py
│── environment.yml


---

## Installation and how to run the code
Clone the repository:


```bash
git clone git@github.com:matisseaa/final-project.git
cd final-project
conda env create -f environment.yml
conda activate numerical-workbench
pip install -e .

---
## Example

Solving the equation:

f(x) = x^3 - x - 2

Using Newton’s method:

```bash
python -m numerical_workbench.cli solve-root \
  --function-kind polynomial \
  --expression "x^3 - x - 2" \
  --method newton \
  --interval 1:2
```

Output:
{
  "solver_name": "newton",
  "root": 1.5213797068045751,
  "converged": true,
  "iterations": 3,
  "final_error": 4.529709940470639e-14,
  "time_taken": 2.3125001462176442e-05,
  "message": "limit reached"
}
Plot saved to: outputs/cli/newton_x3-x-2.png

![Function Plot](functionplot.png)

## Testing
pytest -v
