class Variable:

    def __init__(self, initial_value, row, column):
        self.value = initial_value
        self.domain = [0, 1]
        self.row = row
        self.column = column
        self.constrained_variables = []
