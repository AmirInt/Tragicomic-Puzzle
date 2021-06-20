import numpy


def lift_constraints(variable):
    for v in variable.constrained_variables:
        v.domain = [0, 1]
    variable.domain = [0, 1]
    variable.constrained_variables = []


def apply_constraint(variable, constraint_target):
    if constraint_target.value == -1:
        if variable.value in constraint_target.domain:
            value_index = constraint_target.domain.index(variable.value)
            if len(constraint_target.domain) > 1:
                constraint_target.domain.pop(value_index)
                variable.constrained_variables.append(constraint_target)
            else:
                return False
    return True


class Solver:

    def __init__(self, n):
        self.board = None
        self.board_size = int(n)
        self.variable_queue = []
        self.variable_stack = []
        self.filled_rows = numpy.empty(self.board_size, dtype=object)
        self.filled_columns = numpy.empty(self.board_size, dtype=object)

    def set_board(self, board):
        self.board = board.board

    def next_to_evaluate(self):
        if len(self.variable_queue) > 0:
            most_restricted = 0
            for variable in range(len(self.variable_queue)):
                if len(self.variable_queue[variable].domain) < len(self.variable_queue[most_restricted].domain):
                    most_restricted = variable
            return self.variable_queue.pop(most_restricted)
        return None

    def previously_evaluated(self):
        return self.variable_stack.pop(len(self.variable_stack) - 1)

    def propagate_horizontal_constraints(self, variable):

        # Checking if the variable to the left of this variable has the same value as this variable
        if variable.column > 0 and \
                self.board[variable.row, variable.column - 1].value == variable.value:
            if variable.column > 1:
                constraint_target = self.board[variable.row, variable.column - 2]
                if not apply_constraint(variable, constraint_target):
                    return False
            if variable.column < self.board_size - 1:
                constraint_target = self.board[variable.row, variable.column + 1]
                if not apply_constraint(variable, constraint_target):
                    return False

        # Checking if the variable to the right of this variable has the same value as this variable
        if variable.column < self.board_size - 1 and \
                self.board[variable.row, variable.column + 1].value == variable.value:
            if variable.column > 0:
                constraint_target = self.board[variable.row, variable.column - 1]
                if not apply_constraint(variable, constraint_target):
                    return False
            if variable.column < self.board_size - 2:
                constraint_target = self.board[variable.row, variable.column + 2]
                if not apply_constraint(variable, constraint_target):
                    return False

        # Checking if this variable encloses a variable in between itself and another identically evaluated variable
        if variable.column > 1 and \
                self.board[variable.row, variable.column - 2].value == variable.value:
            constraint_target = self.board[variable.row, variable.column - 1]
            if not apply_constraint(variable, constraint_target):
                return False
        if variable.column < self.board_size - 2 and \
                self.board[variable.row, variable.column + 2].value == variable.value:
            constraint_target = self.board[variable.row, variable.column + 1]
            if not apply_constraint(variable, constraint_target):
                return False
        return True

    def propagate_vertical_constraints(self, variable):

        # Checking if the variable above this variable has the same value as this variable
        if variable.row > 0 and \
                self.board[variable.row - 1, variable.column].value == variable.value:
            if variable.row > 1:
                constraint_target = self.board[variable.row - 2, variable.column]
                if not apply_constraint(variable, constraint_target):
                    return False
            if variable.row < self.board_size - 1:
                constraint_target = self.board[variable.row + 1, variable.column]
                if not apply_constraint(variable, constraint_target):
                    return False

        # Checking if the variable below this variable has the same value as this variable
        if variable.row < self.board_size - 1 and \
                self.board[variable.row + 1, variable.column].value == variable.value:
            if variable.row > 0:
                constraint_target = self.board[variable.row - 1, variable.column]
                if not apply_constraint(variable, constraint_target):
                    return False
            if variable.row < self.board_size - 2:
                constraint_target = self.board[variable.row + 2, variable.column]
                if not apply_constraint(variable, constraint_target):
                    return False

        # Checking if this variable encloses a variable in between itself and another identically evaluated variable
        if variable.row > 1 and \
                self.board[variable.row - 2, variable.column].value == variable.value:
            constraint_target = self.board[variable.row - 1, variable.column]
            if not apply_constraint(variable, constraint_target):
                return False
        if variable.row < self.board_size - 2 and \
                self.board[variable.row + 2, variable.column].value == variable.value:
            constraint_target = self.board[variable.row + 1, variable.column]
            if not apply_constraint(variable, constraint_target):
                return False
        return True

    def is_row_filled_properly(self, variable):
        zeros_counter = 0
        ones_counter = 0
        non_evaluated_variable = -1
        row_string = ''

        for i in range(self.board_size):
            row_string = row_string + str(self.board[variable.row, i].value)
            if self.board[variable.row, i].value == -1:
                non_evaluated_variable = i
            elif self.board[variable.row, i].value == 1:
                ones_counter += 1
            else:
                zeros_counter += 1

        if zeros_counter + ones_counter == self.board_size:
            self.filled_rows[variable.row] = row_string

        else:
            eliminating_value = -1
            if zeros_counter == self.board_size / 2:
                eliminating_value = 0
            elif ones_counter == self.board_size / 2:
                eliminating_value = 1

            if zeros_counter == self.board_size / 2 or ones_counter == self.board_size / 2:
                for i in range(self.board_size):
                    constraint_target = self.board[variable.row, i]
                    if constraint_target.value == -1:
                        value_index = -1
                        if eliminating_value in constraint_target.domain:
                            value_index = constraint_target.domain.index(eliminating_value)
                        if value_index >= 0:
                            if len(constraint_target.domain) > 1:
                                constraint_target.domain.pop(value_index)
                                variable.constrained_variables.append(constraint_target)
                            else:
                                return False

            if zeros_counter + ones_counter == self.board_size - 1:
                for row in self.filled_rows:
                    if row is not None:
                        identical = True
                        for j in range(self.board_size):
                            if j != non_evaluated_variable and int(row[j]) != self.board[variable.row, j].value:
                                identical = False
                                break
                        if identical:
                            eliminating_value = int(row[non_evaluated_variable])
                            constraint_target = self.board[variable.row, non_evaluated_variable]
                            if eliminating_value in constraint_target.domain:
                                value_index = constraint_target.domain.index(eliminating_value)
                                if len(constraint_target.domain) > 1:
                                    constraint_target.domain.pop(value_index)
                                    variable.constrained_variables.append(constraint_target)
                                else:
                                    return False

        return True

    def is_column_filled_properly(self, variable):
        zeros_counter = 0
        ones_counter = 0
        non_evaluated_variable = -1
        column_string = ''

        for i in range(self.board_size):
            column_string = column_string + str(self.board[i, variable.column].value)
            if self.board[i, variable.column].value == -1:
                non_evaluated_variable = i
            elif self.board[i, variable.column].value == 1:
                ones_counter += 1
            else:
                zeros_counter += 1

        if zeros_counter + ones_counter == self.board_size:
            self.filled_columns[variable.column] = column_string

        else:
            eliminating_value = -1
            if zeros_counter == self.board_size / 2:
                eliminating_value = 0
            elif ones_counter == self.board_size / 2:
                eliminating_value = 1

            if zeros_counter == self.board_size / 2 or ones_counter == self.board_size / 2:
                for i in range(self.board_size):
                    if self.board[i, variable.column].value == -1:
                        constraint_target = self.board[i, variable.column]
                        value_index = -1
                        if eliminating_value in constraint_target.domain:
                            value_index = constraint_target.domain.index(eliminating_value)
                        if value_index >= 0:
                            if len(constraint_target.domain) > 1:
                                constraint_target.domain.pop(value_index)
                                variable.constrained_variables.append(constraint_target)
                            else:
                                return False

            if zeros_counter + ones_counter == self.board_size - 1:
                for column in self.filled_columns:
                    if column is not None:
                        identical = True
                        for j in range(self.board_size):
                            if j != non_evaluated_variable and int(column[j]) != self.board[j, variable.column].value:
                                identical = False
                                break
                        if identical:
                            eliminating_value = int(column[non_evaluated_variable])
                            constraint_target = self.board[non_evaluated_variable, variable.column]
                            if eliminating_value in constraint_target.domain:
                                value_index = constraint_target.domain.index(eliminating_value)
                                if len(constraint_target.domain) > 1:
                                    constraint_target.domain.pop(value_index)
                                    variable.constrained_variables.append(constraint_target)
                                else:
                                    return False
        return True

    def propagate_constraints(self, variable):
        if self.propagate_horizontal_constraints(variable) and \
                self.propagate_vertical_constraints(variable) and \
                self.is_row_filled_properly(variable) and \
                self.is_column_filled_properly(variable):
            return True
        return False

    def solve(self):

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i, j].value != -1:
                    successful = self.propagate_constraints(self.board[i, j])
                    if not successful:
                        return False

        next_variable = self.next_to_evaluate()
        while True:
            # If the next variable's domain is non-empty:
            if len(next_variable.domain) > 0:
                # Evaluates the next variable to the first value present in its domain
                next_variable.value = next_variable.domain.pop(0)
                domain = next_variable.domain
                # If it is to change value, it first needs to lift the applied constraints:
                lift_constraints(next_variable)
                next_variable.domain = domain
                if self.propagate_constraints(next_variable):
                    # If constraints are propagated without any issues:
                    self.variable_stack.append(next_variable)
                    next_variable = self.next_to_evaluate()
                    if next_variable is None:
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
                lift_constraints(next_variable)
                # Returns the next variable back to queue:
                queue = [next_variable]
                for c in self.variable_queue:
                    queue.append(c)
                self.variable_queue = queue
                if len(self.variable_stack) > 0:
                    self.filled_rows[next_variable.row] = None
                    self.filled_columns[next_variable.column] = None
                    next_variable = self.previously_evaluated()
                else:
                    return False
