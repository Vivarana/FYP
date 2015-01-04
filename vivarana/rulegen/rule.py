class Rule:
    filters = []
    group_by = []
    window = None

    # Only filers in disjunctive normal form are accepted
    def __init__(self, stream_name, filters, groupby, window):
        self.stream_name = stream_name
        self.filters = filters
        self.group_by = groupby
        self.window = window

    def apply_rule(self, dataframe):
        print self.filters.apply_contraint(dataframe)

    def to_string(self):
        window_string = ''
        if self.window!=None:
            window_string = '#window.' + self.window[0] + '(' + self.window[1] + ')'

        return 'FROM ' + self.stream_name + window_string



class ConstraintSet:
    def __init__(self, operand, constraints):
        self.operand = operand
        self.constraints = constraints

    def apply_constraint(self, dataframe):
        if self.operand == 'AND':
            for constraint in self.constraints:
                dataframe = constraint.apply_constraint(dataframe)
            return dataframe
        else:
            selected_ids = set([])
            for constraint in self.constraints:
                selected_ids = selected_ids | set(constraint.apply_constraint(dataframe).index)
            return dataframe[dataframe.index.isin(list(selected_ids))]

    def to_string(self):
        return "( " + (" "+self.operand+" ").join([constraint.to_string() for constraint in self.constraints]) + " )"


class Constraint:
    def __init__(self, column, value, aggregate):
        self.column = column
        self.value = value
        if aggregate != '':
            aggregate += + '_'
        self.aggregate = aggregate


class EqualConstraint(Constraint):
    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] == self.value]

    def to_string(self):
        return self.aggregate + self.column + "=" + str(self.value)

    @staticmethod
    def from_list(column, value_list, aggregate):
        return ConstraintSet('OR', [EqualConstraint(column, value, aggregate) for value in value_list])


class LessConstraint(Constraint):

    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] < self.value]

    def to_string(self):
        return self.aggregate + self.column + "<" + str(self.value)


class LessEqualConstraint(Constraint):
    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] <= self.value]

    def to_string(self):
        return self.aggregate + self.column + "<=" + str(self.value)


class MoreConstraint(Constraint):
    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] > self.value]

    def to_string(self):
        return self.aggregate + self.column + ">" + str(self.value)


class MoreEqualConstraint(Constraint):
    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] >= self.value]

    def to_string(self):
        return self.aggregate + self.column + ">=" + str(self.value)


class MoreLessBetweenConstraint(Constraint):
    def apply_constraint(self, dataframe):
        return dataframe[(dataframe[self.column] > self.value[0]) & (dataframe[self.column] < self.value[1])]

    def to_string(self):
        return "(" + self.aggregate + self.column + ">" + str(self.value[0]) + " AND " + self.aggregate + self.column + "<" + str(self.value[1]) + ")"


class MoreEqualLessBetweenConstraint(Constraint):
    def apply_constraint(self, dataframe):
        return dataframe[(dataframe[self.column] > self.value[0]) & (dataframe[self.column] <= self.value[1])]

    def to_string(self):
        return "(" + self.aggregate + self.column + ">=" + str(self.value[0]) + " AND " + self.aggregate + self.column + "<" + str(self.value[1]) + ")"


class MoreLessEqualBetweenConstraint(Constraint):
    def apply_constraint(self, dataframe):
        return dataframe[(dataframe[self.column] >= self.value[0]) & (dataframe[self.column] < self.value[1])]

    def to_string(self):
        return "(" + self.aggregate + self.column + ">" + str(self.value[0]) + " AND " + self.aggregate + self.column + "<=" + str(self.value[1]) + ")"


class MoreEqualLessEqualBetweenConstraint(Constraint):
    def apply_constraint(self, dataframe):
        return dataframe[(dataframe[self.column] >= self.value[0]) & (dataframe[self.column] <= self.value[1])]

    def to_string(self):
        return "(" + self.aggregate + self.column + ">=" + str(self.value[0]) + " AND " + self.aggregate + self.column + "<=" + str(self.value[1]) + ")"


rules = {'=': EqualConstraint.from_list, '<': LessConstraint, '>': MoreConstraint, '<=': LessEqualConstraint,
         '>=': MoreEqualConstraint, '<>': MoreLessBetweenConstraint, '<>=': MoreEqualLessBetweenConstraint,
         '<=>': MoreLessEqualBetweenConstraint, '<=>=': MoreEqualLessEqualBetweenConstraint}