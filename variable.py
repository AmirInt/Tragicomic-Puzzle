class Variable:
    """
    Class representing each piece of the board
    """

    def __init__(self, initial_value, row, column):
        """
        Initialises this variable
        :param initial_value: The initial value of this variable if given
        :param row: The row on which this variable is placed
        :param column: The column in which this variable is placed
        """
        self.value = initial_value
        self.domain = [0, 1]
        self.row = row
        self.column = column
        self.constrained_variables = []
