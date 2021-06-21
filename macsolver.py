import numpy
from GUI import Interface


class Solver:
    """
    Class Solver is the agent that attempts to do this puzzle, using the backtracking
    algorithm. This class uses forward checking method to propagate constraints.
    """

    def __init__(self, n):
        """
        Initialises this class
        :param n: The size of the board
        """
        self.board = None
        self.board_size = int(n)
        self.variable_queue = []
        self.variable_stack = []
        self.arcs_queue = []
        self.filled_rows = numpy.empty(self.board_size, dtype=object)
        self.filled_columns = numpy.empty(self.board_size, dtype=object)
        self.row_zeros_counter = 0
        self.row_ones_counter = 0
        self.column_zeros_counter = 0
        self.column_ones_counter = 0
        self.row_string_zero = ''
        self.row_string_one = ''
        self.column_string_zero = ''
        self.column_string_one = ''
        self.gui = Interface(self.board_size)

    def set_board(self, board):
        """
        Sets up the playing board
        :param board: The puzzle board
        """
        self.board = board.board

    def next_to_evaluate(self):
        """
        :return: Returns the next variable on the queue to be evaluated
        """
        if len(self.variable_queue) > 0:
            most_restricted = 0
            for variable in range(len(self.variable_queue)):
                if len(self.variable_queue[variable].domain) < len(self.variable_queue[most_restricted].domain):
                    most_restricted = variable
            return self.variable_queue.pop(most_restricted)
        return None

    def previously_evaluated(self):
        """
        :return: The previously (recently) evaluated variable, in case of a backtrack.
        """
        return self.variable_stack.pop(len(self.variable_stack) - 1)

    def add_neighbours(self, constraint_target, constraining_variable):

        for i in range(self.board_size):
            if self.board[i, constraint_target.column].value == -1:
                if i != constraint_target.row and constraining_variable is not self.board[i, constraint_target.column]:
                    self.arcs_queue.append([self.board[i, constraint_target.column], constraint_target])
            if self.board[constraint_target.row, i].value == -1:
                if i != constraint_target.column and constraining_variable is not self.board[constraint_target.row, i]:
                    self.arcs_queue.append([self.board[constraint_target.row, i], constraint_target])

    def check_arc_consistency_for(self, variable, subject, side_variable, constraint_target):
        """
        Sets up the arc-consistency for ternary relation of the recently
        evaluated variable, the target and a side variable that's selected
        on purpose.
        :param variable: The recently evaluated variable
        :param subject: Either the value of "variable" of the sole alternative value
        in its domain
        :param side_variable: A third variable playing a role in the arc consistency
        :param constraint_target: The target variable
        :return: True if it comes across no issue, false if a backtrack is needed
        """
        if 0 == side_variable.value == subject:
            if 0 in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    variable.constrained_variables.append(constraint_target)
                    constraint_target.domain.pop(0)
                    self.add_neighbours(constraint_target, variable)
                    self.add_to_gui(constraint_target)
                else:
                    return False
        elif 1 == side_variable.value == subject:
            if 1 in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    variable.constrained_variables.append(constraint_target)
                    value_index = constraint_target.domain.index(1)
                    constraint_target.domain.pop(value_index)
                    self.add_neighbours(constraint_target, variable)
                    self.add_to_gui(constraint_target)
                else:
                    return False
        return True

    def is_row_or_column_filled(self, variable):
        row_filled = True
        column_filled = True
        row_string = ''
        column_string = ''
        for i in range(self.board_size):
            if self.board[variable.row, i].value == -1:
                if len(self.board[variable.row, i].domain) > 1:
                    row_filled = False
                else:
                    row_string = row_string + str(self.board[variable.row, i].domain[0])
            else:
                row_string = row_string + str(self.board[variable.row, i].value)

            if self.board[i, variable.column].value == -1:
                if len(self.board[i, variable.column].domain) > 1:
                    column_filled = False
                else:
                    column_string = column_string + str(self.board[i, variable.column].domain[0])
            else:
                column_string = column_string + str(self.board[i, variable.column].value)

        if column_filled:
            self.filled_columns[variable.column] = column_string
        if row_filled:
            self.filled_rows[variable.row] = row_string

    def check_row(self, variable):
        self.row_zeros_counter = 0
        self.row_ones_counter = 0
        self.row_string_zero = ''
        self.row_string_one = ''

        subject = variable.value if variable.value != -1 else variable.domain[0]

        for i in range(self.board_size):
            if i == variable.column:
                self.row_string_zero = self.row_string_zero + str(subject)
                self.row_string_one = self.row_string_one + str(subject)
                if subject == 0:
                    self.row_zeros_counter += 1
                else:
                    self.row_ones_counter += 1
            else:
                if self.board[variable.row, i].value == -1:
                    self.row_string_zero = self.row_string_zero + '0'
                    self.row_string_one = self.row_string_one + '1'
                elif self.board[variable.row, i].value == 1:
                    self.row_string_zero = self.row_string_zero + str(self.board[variable.row, i].value)
                    self.row_string_one = self.row_string_one + str(self.board[variable.row, i].value)
                    self.row_ones_counter += 1
                else:
                    self.row_string_zero = self.row_string_zero + str(self.board[variable.row, i].value)
                    self.row_string_one = self.row_string_one + str(self.board[variable.row, i].value)
                    self.row_zeros_counter += 1

    def check_column(self, variable):
        self.column_zeros_counter = 0
        self.column_ones_counter = 0
        self.column_string_zero = ''
        self.column_string_one = ''

        subject = variable.value if variable.value != -1 else variable.domain[0]

        for i in range(self.board_size):
            if i == variable.row:
                self.column_string_zero = self.column_string_zero + str(subject)
                self.column_string_one = self.column_string_one + str(subject)
                if subject == 1:
                    self.column_ones_counter += 1
                else:
                    self.column_zeros_counter += 1
            else:
                if self.board[i, variable.column].value == -1:
                    self.column_string_zero = self.column_string_zero + '0'
                    self.column_string_one = self.column_string_one + '1'
                elif self.board[i, variable.column].value == 1:
                    self.column_string_zero = self.column_string_zero + str(self.board[i, variable.column].value)
                    self.column_string_one = self.column_string_one + str(self.board[i, variable.column].value)
                    self.column_ones_counter += 1
                else:
                    self.column_string_zero = self.column_string_zero + str(self.board[i, variable.column].value)
                    self.column_string_one = self.column_string_one + str(self.board[i, variable.column].value)
                    self.column_zeros_counter += 1

    def lift_constraints(self, variable):
        """
        Lift the wrongly applied constraints in case of a backtrack.
        :param variable: The last evaluated variable, from which backtracking occurs
        """
        queue = [variable]
        while len(queue) > 0:
            next_element = queue.pop(0)
            next_element.domain = [0, 1]

            if next_element in self.variable_stack:
                next_element.value = -1
                self.add_to_queue(self.variable_stack.pop(self.variable_stack.index(next_element)))

            self.add_to_gui(next_element)
            for v in next_element.constrained_variables:
                queue.append(v)
            next_element.constrained_variables = []

    def propagate_horizontal_constraints(self, variable, constraint_target):
        """
        Applies constraints on a row
        :param variable: The recently evaluated variable
        :param constraint_target: The target of the constraints
        :return: True if this constraint is applicable, false otherwise
        """
        subject = variable.value if variable.value != -1 else variable.domain[0]

        # Checking for three consecutive variables:
        if constraint_target.column == variable.column - 2:
            if self.board[variable.row, variable.column - 1].value != -1:
                if not self.check_arc_consistency_for(variable, subject,
                                                      self.board[variable.row, variable.column - 1],
                                                      constraint_target):
                    return False

        elif constraint_target.column == variable.column - 1:
            if variable.column > 1:
                if self.board[variable.row, variable.column - 2].value != -1:
                    if not self.check_arc_consistency_for(variable, subject,
                                                          self.board[variable.row, variable.column - 2],
                                                          constraint_target):
                        return False
            if variable.column < self.board_size - 1:
                if self.board[variable.row, variable.column + 1].value != -1:
                    if not self.check_arc_consistency_for(variable, subject,
                                                          self.board[variable.row, variable.column + 1],
                                                          constraint_target):
                        return False

        elif constraint_target.column == variable.column + 1:
            if variable.column > 0:
                if self.board[variable.row, variable.column - 1].value != -1:
                    if not self.check_arc_consistency_for(variable, subject,
                                                          self.board[variable.row, variable.column - 1],
                                                          constraint_target):
                        return False
            if variable.column < self.board_size - 2:
                if self.board[variable.row, variable.column + 2].value != -1:
                    if not self.check_arc_consistency_for(variable, subject,
                                                          self.board[variable.row, variable.column + 2],
                                                          constraint_target):
                        return False

        elif constraint_target.column == variable.column + 2:
            if self.board[variable.row, variable.column + 1].value != -1:
                if not self.check_arc_consistency_for(variable, subject,
                                                      self.board[variable.row, variable.column + 1],
                                                      constraint_target):
                    return False

        # Checking for row consistency:
        return self.propagate_row_constraints(variable, constraint_target)

    def propagate_vertical_constraints(self, variable, constraint_target):
        """
        Applies constraints in a column
        :param variable: The recently evaluated variable
        :param constraint_target: The target of the constraint
        :return: True if this constraint is applicable, false otherwise
        """
        subject = variable.value if variable.value != -1 else variable.domain[0]

        # Checking for three consecutive variables:
        if constraint_target.row == variable.row - 2:
            if self.board[variable.row - 1, variable.column].value != -1:
                if not self.check_arc_consistency_for(variable, subject,
                                                      self.board[variable.row - 1, variable.column],
                                                      constraint_target):
                    return False

        elif constraint_target.row == variable.row - 1:
            if variable.row > 1:
                if self.board[variable.row - 2, variable.column].value != -1:
                    if not self.check_arc_consistency_for(variable, subject,
                                                          self.board[variable.row - 2, variable.column],
                                                          constraint_target):
                        return False
            if variable.row < self.board_size - 1:
                if self.board[variable.row + 1, variable.column].value != -1:
                    if not self.check_arc_consistency_for(variable, subject,
                                                          self.board[variable.row + 1, variable.column],
                                                          constraint_target):
                        return False

        elif constraint_target.row == variable.row + 1:
            if variable.row > 0:
                if self.board[variable.row - 1, variable.column].value != -1:
                    if not self.check_arc_consistency_for(variable, subject,
                                                          self.board[variable.row - 1, variable.column],
                                                          constraint_target):
                        return False
            if variable.row < self.board_size - 2:
                if self.board[variable.row + 2, variable.column].value != -1:
                    if not self.check_arc_consistency_for(variable, subject,
                                                          self.board[variable.row + 2, variable.column],
                                                          constraint_target):
                        return False

        elif constraint_target.row == variable.row + 2:
            if self.board[variable.row + 1, variable.column].value != -1:
                if not self.check_arc_consistency_for(variable, subject,
                                                      self.board[variable.row + 1, variable.column],
                                                      constraint_target):
                    return False

        # Checking for row consistency:
        return self.propagate_column_constraints(variable, constraint_target)

    def propagate_row_constraints(self, variable, constraint_target):
        """
        Checks if the variable's row is filled properly, and propagating
        corresponding constraints, as well.
        :param variable: The recently evaluated variable.
        :param constraint_target: The target of the constraint
        :return: True if this row is properly arranged, false otherwise
        """
        eliminating_value = -1
        if self.row_zeros_counter == self.board_size / 2:
            eliminating_value = 0
        elif self.row_ones_counter == self.board_size / 2:
            eliminating_value = 1

        if self.row_zeros_counter == self.board_size / 2 or self.row_ones_counter == self.board_size / 2:
            if eliminating_value in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    value_index = constraint_target.domain.index(eliminating_value)
                    constraint_target.domain.pop(value_index)
                    variable.constrained_variables.append(constraint_target)
                    self.add_neighbours(constraint_target, variable)
                    self.add_to_gui(constraint_target)
                else:
                    return False

        if self.row_zeros_counter + self.row_ones_counter == self.board_size - 1:
            for i in range(self.board_size):
                if i != variable.row:
                    if self.filled_rows[i] == self.row_string_zero:
                        if 0 in constraint_target.domain:
                            if len(constraint_target.domain) > 1:
                                constraint_target.domain.pop(0)
                                variable.constrained_variables.append(constraint_target)
                                self.add_neighbours(constraint_target, variable)
                                self.add_to_gui(constraint_target)
                            else:
                                return False
                    elif self.filled_rows[i] == self.row_string_one:
                        if 1 in constraint_target.domain:
                            if len(constraint_target.domain) > 1:
                                value_index = constraint_target.domain.index(eliminating_value)
                                constraint_target.domain.pop(value_index)
                                variable.constrained_variables.append(constraint_target)
                                self.add_neighbours(constraint_target, variable)
                                self.add_to_gui(constraint_target)
                            else:
                                return False
        return True

    def propagate_column_constraints(self, variable, constraint_target):
        """
        Checks if the variable's column is filled properly, and propagating
        corresponding constraints, as well.
        :param variable: The recently evaluated variable.
        :param constraint_target: The target of the constraint
        :return: True if this column is properly arranged, false otherwise
        """
        eliminating_value = -1
        if self.column_zeros_counter == self.board_size / 2:
            eliminating_value = 0
        elif self.column_ones_counter == self.board_size / 2:
            eliminating_value = 1

        if self.column_zeros_counter == self.board_size / 2 or self.column_ones_counter == self.board_size / 2:
            if eliminating_value in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    value_index = constraint_target.domain.index(eliminating_value)
                    constraint_target.domain.pop(value_index)
                    variable.constrained_variables.append(constraint_target)
                    self.add_neighbours(constraint_target, variable)
                    self.add_to_gui(constraint_target)
                else:
                    return False

        if self.column_zeros_counter + self.column_ones_counter == self.board_size - 1:
            for i in range(self.board_size):
                if i != variable.column:
                    if self.filled_columns[i] == self.column_string_zero:
                        if 0 in constraint_target.domain:
                            if len(constraint_target.domain) > 1:
                                constraint_target.domain.pop(0)
                                variable.constrained_variables.append(constraint_target)
                                self.add_neighbours(constraint_target, variable)
                                self.add_to_gui(constraint_target)
                            else:
                                return False
                    elif self.filled_columns[i] == self.column_string_one:
                        if 1 in constraint_target.domain:
                            if len(constraint_target.domain) > 1:
                                value_index = constraint_target.domain.index(eliminating_value)
                                constraint_target.domain.pop(value_index)
                                variable.constrained_variables.append(constraint_target)
                                self.add_neighbours(constraint_target, variable)
                                self.add_to_gui(constraint_target)
                            else:
                                return False
        return True

    def propagate_constraints(self, variable):
        """
        Propagates constraints after evaluating this variable.
        :param variable: The recently evaluated variable
        :return: True if no issue is encountered, false if backtracking is required
        """
        self.add_neighbours(variable, None)
        while len(self.arcs_queue) > 0:
            arc = self.arcs_queue.pop(0)
            v1 = arc[0]
            v2 = arc[1]
            self.check_row(v2)
            self.check_column(v2)
            if v1.row == v2.row:
                successful = self.propagate_horizontal_constraints(v2, v1)
                if not successful:
                    self.arcs_queue.clear()
                    return False
            else:
                successful = self.propagate_vertical_constraints(v2, v1)
                if not successful:
                    self.arcs_queue.clear()
                    return False
        return True

    def add_to_gui(self, changed_variable):
        """
        Adds a trace of the solving procedure to the graphical interface object
        to hold track of what's been done.
        :param changed_variable: The variable that's undergone a change at the current level
        """
        board_values = []
        if changed_variable is not None:
            board_values.append(changed_variable.row)
            board_values.append(changed_variable.column)
        else:
            board_values.append(-1)
            board_values.append(-1)
        for i in self.board:
            for j in i:
                board_values.append(j.value)
                if len(j.domain) > 1:
                    board_values.append(j.domain[0])
                    board_values.append(j.domain[1])
                elif len(j.domain) > 0:
                    board_values.append(j.domain[0])
                    board_values.append(-1)
                else:
                    board_values.append(-1)
                    board_values.append(-1)
        self.gui.boards.append(board_values)

    def add_to_queue(self, variable):
        """
        An auxiliary method for returning the wrong-valued variable back
        into the variables queue of the class
        :param variable: The variable from which the algorithm backtracks to
        a previously evaluated variable
        """
        queue = [variable]
        for c in self.variable_queue:
            queue.append(c)
        self.variable_queue = queue

    def solve(self):
        """
        Performs the procedure of solving the puzzle holistically.
        :return: True if the puzzle is solved, false if it's an impossible puzzle
        """

        self.add_to_gui(None)

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i, j].value != -1:
                    successful = self.propagate_constraints(self.board[i, j])
                    if not successful:
                        return False

        next_variable = self.next_to_evaluate()
        previous_variable = None
        while True:
            # If the next variable's domain is non-empty:
            if len(next_variable.domain) > 0:
                # Evaluates the next variable to the first value present in its domain
                next_variable.value = next_variable.domain.pop(0)
                self.add_to_gui(next_variable)
                # self.print_board()
                # If it is to change value, it first needs to lift the applied constraints:
                if previous_variable is next_variable:
                    domain = next_variable.domain
                    self.lift_constraints(next_variable)
                    next_variable.domain = domain
                previous_variable = next_variable
                if self.propagate_constraints(next_variable):
                    # If constraints are propagated without any issues:
                    self.variable_stack.append(next_variable)
                    self.is_row_or_column_filled(next_variable)
                    next_variable = self.next_to_evaluate()
                    if next_variable is None:
                        self.gui.root.mainloop()
                        return True
                else:
                    # If it encounters a problem propagating the constraints:
                    self.filled_rows[next_variable.row] = None
                    self.filled_columns[next_variable.column] = None
                    next_variable = next_variable
            # If the next variable's domain runs out of values:
            else:
                # Devalues the next value:
                next_variable.value = -1
                # Lifts all the constraints applied by the next variable:
                self.lift_constraints(next_variable)
                self.add_to_gui(next_variable)
                # Returns the next variable back to queue:
                self.add_to_queue(next_variable)
                if len(self.variable_stack) > 0:
                    self.filled_rows[next_variable.row] = None
                    self.filled_columns[next_variable.column] = None
                    next_variable = self.previously_evaluated()
                    previous_variable = next_variable
                else:
                    self.gui.root.mainloop()
                    return False
