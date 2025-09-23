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