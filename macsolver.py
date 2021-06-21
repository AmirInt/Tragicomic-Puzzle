import numpy


def lift_constraints(variable):
    queue = [variable]
    while len(queue) > 0:
        next_element = queue.pop(0)
        next_element.domain = [0, 1]
        for v in next_element.constrained_variables:
            queue.append(v)
        next_element.constrained_variables = []


class Solver:

    def __init__(self, n):
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

    def add_neighbours(self, constraint_target, constraining_variable):
        for i in range(self.board_size):
            if self.board[i, constraint_target.column].value == -1:
                if i != constraint_target.row and constraining_variable is not self.board[i, constraint_target.column]:
                    self.arcs_queue.append([self.board[i, constraint_target.column], constraint_target])
            if self.board[constraint_target.row, i].value == -1:
                if i != constraint_target.column and constraining_variable is not self.board[constraint_target.row, i]:
                    self.arcs_queue.append([self.board[constraint_target.row, i], constraint_target])

    def check_arc_consistency_for(self, variable, subject, side_variable, constraint_target):
        if 0 == side_variable.value == subject:
            if 0 in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    variable.constrained_variables.append(constraint_target)
                    constraint_target.domain.pop(0)
                    self.add_neighbours(constraint_target, variable)
                else:
                    return False
        elif 1 == side_variable.value == subject:
            if 1 in constraint_target.domain:
                if len(constraint_target.domain) > 1:
                    variable.constrained_variables.append(constraint_target)
                    value_index = constraint_target.domain.index(1)
                    constraint_target.domain.pop(value_index)
                    self.add_neighbours(constraint_target, variable)
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
                row_filled = False
            if self.board[i, variable.column].value == -1:
                column_filled = False
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
        return self.propagate_row_constraints(variable, constraint_target)

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
        return self.propagate_column_constraints(variable, constraint_target)

    def propagate_row_constraints(self, variable, constraint_target):
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
                else:
                    return False

        if self.row_zeros_counter + self.row_ones_counter == self.board_size - 1:
            for row in self.filled_rows:
                if row == self.row_string_zero:
                    if 0 in constraint_target.domain:
                        if len(constraint_target.domain) > 1:
                            constraint_target.domain.pop(0)
                            variable.constrained_variables.append(constraint_target)
                            self.add_neighbours(constraint_target, variable)
                        else:
                            return False
                elif row == self.row_string_one:
                    if 1 in constraint_target.domain:
                        if len(constraint_target.domain) > 1:
                            value_index = constraint_target.domain.index(eliminating_value)
                            constraint_target.domain.pop(value_index)
                            variable.constrained_variables.append(constraint_target)
                            self.add_neighbours(constraint_target, variable)
                        else:
                            return False
        return True

    def propagate_column_constraints(self, variable, constraint_target):
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
                else:
                    return False

        if self.column_zeros_counter + self.column_ones_counter == self.board_size - 1:
            for column in self.filled_columns:
                if column == self.column_string_zero:
                    if 0 in constraint_target.domain:
                        if len(constraint_target.domain) > 1:
                            constraint_target.domain.pop(0)
                            variable.constrained_variables.append(constraint_target)
                            self.add_neighbours(constraint_target, variable)
                        else:
                            return False
                elif column == self.column_string_one:
                    if 1 in constraint_target.domain:
                        if len(constraint_target.domain) > 1:
                            value_index = constraint_target.domain.index(eliminating_value)
                            constraint_target.domain.pop(value_index)
                            variable.constrained_variables.append(constraint_target)
                            self.add_neighbours(constraint_target, variable)
                        else:
                            return False
        return True

    def propagate_constraints(self, variable):
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

    def solve(self):

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
                # If it is to change value, it first needs to lift the applied constraints:
                if previous_variable is next_variable:
                    domain = next_variable.domain
                    lift_constraints(next_variable)
                    next_variable.domain = domain
                previous_variable = next_variable
                if self.propagate_constraints(next_variable):
                    # If constraints are propagated without any issues:
                    self.variable_stack.append(next_variable)
                    self.is_row_or_column_filled(next_variable)
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
                domain = [next_variable.value]
                # Devalues the next value:
                next_variable.value = -1
                # Lifts all the constraints applied by the next variable:
                lift_constraints(next_variable)
                next_variable.domain = domain
                # Returns the next variable back to queue:
                queue = [next_variable]
                for c in self.variable_queue:
                    queue.append(c)
                self.variable_queue = queue
                if len(self.variable_stack) > 0:
                    self.filled_rows[next_variable.row] = None
                    self.filled_columns[next_variable.column] = None
                    next_variable = self.previously_evaluated()
                    previous_variable = next_variable
                else:
                    return False
