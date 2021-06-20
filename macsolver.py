import numpy


def lift_constraints(variable):
    for v in variable.constrained_variables:
        lift_constraints(v)
    variable.domain = [0, 1]
    variable.constrained_variables = []


class Solver:

    def __init__(self, n):
        self.board = None
        self.board_size = int(n)
        self.variable_queue = []
        self.variable_stack = []
        self.arcs_queue = []
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

    def add_neighbours(self, constraint_target):
        for i in range(self.board_size):
            if self.board[i, constraint_target.column].value == -1:
                if i != constraint_target.row:
                    self.arcs_queue.append([self.board[i, constraint_target.column], constraint_target])
            if self.board[constraint_target.row, i].value == -1:
                if i != constraint_target.column:
                    self.arcs_queue.append([self.board[constraint_target.row, i], constraint_target])

    def check_arc_consistency_for(self, variable, subject, side_variable, constraint_target):
        if 0 == side_variable.value == subject:
            if 0 in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    variable.constrained_variables.append(constraint_target)
                    constraint_target.domain.pop(0)
                    self.add_neighbours(constraint_target)
                else:
                    return False
        elif 1 == side_variable.value == subject:
            if 1 in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    variable.constrained_variables.append(constraint_target)
                    value_index = constraint_target.domain.index(1)
                    constraint_target.domain.pop(value_index)
                    self.add_neighbours(constraint_target)
                else:
                    return False
        return True

    def is_row_or_column_filled(self, variable):
        column_filled = True
        row_filled = True
        row_string = ''
        column_string = ''
        for i in range(self.board_size):
            row_string = row_string + str(self.board[variable.row, i].value)
            column_string = column_string + str(self.board[i, variable.column].value)
            if self.board[variable.row, i].value == -1:
                column_filled = False
            if self.board[i, variable.column].value == -1:
                row_filled = False
        if column_filled:
            self.filled_columns[variable.column] = column_string
        if row_filled:
            self.filled_rows[variable.row] = row_string

    def propagate_horizontal_constraints(self, variable, constraint_target):

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
        return self.propagate_row_constraints(variable, subject, constraint_target)

    def propagate_vertical_constraints(self, variable, constraint_target):

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
        return self.propagate_column_constraints(variable, subject, constraint_target)

    def propagate_row_constraints(self, variable, subject, constraint_target):
        zeros_counter = 0
        ones_counter = 0
        row_string_zero = ''
        row_string_one = ''

        for i in range(self.board_size):
            if i == variable.column:
                row_string_zero = row_string_zero + str(subject)
                row_string_one = row_string_one + str(subject)
                if subject == 0:
                    zeros_counter += 1
                else:
                    ones_counter += 1
            else:
                if self.board[variable.row, i].value == -1:
                    row_string_zero = row_string_zero + '0'
                    row_string_one = row_string_one + '1'
                elif self.board[variable.row, i].value == 1:
                    row_string_zero = row_string_zero + str(self.board[variable.row, i].value)
                    row_string_one = row_string_one + str(self.board[variable.row, i].value)
                    ones_counter += 1
                else:
                    row_string_zero = row_string_zero + str(self.board[variable.row, i].value)
                    row_string_one = row_string_one + str(self.board[variable.row, i].value)
                    zeros_counter += 1

        eliminating_value = -1
        if zeros_counter == self.board_size / 2:
            eliminating_value = 0
        elif ones_counter == self.board_size / 2:
            eliminating_value = 1

        if zeros_counter == self.board_size / 2 or ones_counter == self.board_size / 2:
            if eliminating_value in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    value_index = constraint_target.domain.index(eliminating_value)
                    constraint_target.domain.pop(value_index)
                    variable.constrained_variables.append(constraint_target)
                    self.add_neighbours(constraint_target)
                else:
                    return False

        if zeros_counter + ones_counter == self.board_size - 1:
            for row in self.filled_rows:
                if row == row_string_zero:
                    if 0 in constraint_target.domain:
                        if len(constraint_target.domain) > 1:
                            constraint_target.domain.pop(0)
                            variable.constrained_variables.append(constraint_target)
                            self.add_neighbours(constraint_target)
                        else:
                            return False
                elif row == row_string_one:
                    if 1 in constraint_target.domain:
                        if len(constraint_target.domain) > 1:
                            value_index = constraint_target.domain.index(eliminating_value)
                            constraint_target.domain.pop(value_index)
                            variable.constrained_variables.append(constraint_target)
                            self.add_neighbours(constraint_target)
                        else:
                            return False
        return True

    def propagate_column_constraints(self, variable, subject, constraint_target):
        zeros_counter = 0
        ones_counter = 0
        column_string_zero = ''
        column_string_one = ''

        for i in range(self.board_size):
            if i == variable.row:
                column_string_zero = column_string_zero + str(subject)
                column_string_one = column_string_one + str(subject)
                if subject == 1:
                    ones_counter += 1
                else:
                    zeros_counter += 1
            else:
                if self.board[i, variable.column].value == -1:
                    column_string_zero = column_string_zero + '0'
                    column_string_one = column_string_one + '1'
                elif self.board[variable.row, i].value == 1:
                    column_string_zero = column_string_zero + str(self.board[i, variable.column].value)
                    column_string_one = column_string_one + str(self.board[i, variable.column].value)
                    ones_counter += 1
                else:
                    column_string_zero = column_string_zero + str(self.board[i, variable.column].value)
                    column_string_one = column_string_one + str(self.board[i, variable.column].value)
                    zeros_counter += 1

        eliminating_value = -1
        if zeros_counter == self.board_size / 2:
            eliminating_value = 0
        elif ones_counter == self.board_size / 2:
            eliminating_value = 1

        if zeros_counter == self.board_size / 2 or ones_counter == self.board_size / 2:
            if eliminating_value in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    value_index = constraint_target.domain.index(eliminating_value)
                    constraint_target.domain.pop(value_index)
                    variable.constrained_variables.append(constraint_target)
                    self.add_neighbours(constraint_target)
                else:
                    return False

        if zeros_counter + ones_counter == self.board_size - 1:
            for column in self.filled_columns:
                if column == column_string_zero:
                    if 0 in constraint_target.domain:
                        if len(constraint_target.domain) > 1:
                            constraint_target.domain.pop(0)
                            variable.constrained_variables.append(constraint_target)
                            self.add_neighbours(constraint_target)
                        else:
                            return False
                elif column == column_string_one:
                    if 1 in constraint_target.domain:
                        if len(constraint_target.domain) > 1:
                            value_index = constraint_target.domain.index(eliminating_value)
                            constraint_target.domain.pop(value_index)
                            variable.constrained_variables.append(constraint_target)
                            self.add_neighbours(constraint_target)
                        else:
                            return False
        return True

    def propagate_constraints(self, variable):
        self.add_neighbours(variable)
        while len(self.arcs_queue) > 0:
            arc = self.arcs_queue.pop(0)
            v1 = arc[0]
            v2 = arc[1]
            print(v1.row, v1.column)
            if v1.row == v2.row:
                successful = self.propagate_horizontal_constraints(v2, v1)
                if not successful:
                    return False
            else:
                successful = self.propagate_vertical_constraints(v2, v1)
                if not successful:
                    return False
        print()
        return True

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
                v = next_variable.domain.pop(0)
                print(next_variable.row, next_variable.column, v)
                next_variable.value = v
                domain = next_variable.domain
                # If it is to change value, it first needs to lift the applied constraints:
                lift_constraints(next_variable)
                next_variable.domain = domain
                if self.propagate_constraints(next_variable):
                    # If constraints are propagated without any issues:
                    self.variable_stack.append(next_variable)
                    next_variable = self.next_to_evaluate()
                    self.is_row_or_column_filled(next_variable)
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
