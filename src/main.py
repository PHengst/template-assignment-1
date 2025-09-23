"""
Placeholder for main function to execute the model runner. This function creates a single/multiple instance of the Runner class, prepares input data,
and runs a single/multiple simulation.

Suggested structure:
- Import necessary modules and functions.
- Define a main function to encapsulate the workflow (e.g. Create an instance of your the Runner class, Run a single simulation or multiple simulations, Save results and generate plots if necessary.)
- Prepare input data for a single simulation or multiple simulations.
- Execute main function when the script is run directly.
"""
import data_ops
import opt_model
import runner

# This corresponds to the main function
input_data = InputData(
    VARIABLES = ['x1', 'x2'],
    objective_coeff = {'x1': 30, 'x2': 20},
    constraints_coeff = {'x1': [0.6, 0.4], 'x2': [0.2, 0.8]},
    constraints_rhs = [60, 100],
    constraints_sense =  [GRB.GREATER_EQUAL, GRB.GREATER_EQUAL],
)

problem = opt_model.OptModel(input_data)
problem.run()
problem.display_results()


class InputData:

    def __init__(
        self, 
        VARIABLES: list,
        objective_coeff: list[str, int],    # Coefficients in objective function
        constraints_coeff: list[str, int],  # Linear coefficients of constraints
        constraints_rhs: list[str, int],    # Right hand side coefficients of constraints
        constraints_sense: list[str, int],  # Direction of constraints
    ):
        self.VARIABLES = VARIABLES
        self.objective_coeff = objective_coeff
        self.constraints_coeff = constraints_coeff
        self.constraints_rhs = constraints_rhs
        self.constraints_sense = constraints_sense