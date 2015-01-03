class Rule:
    filters = []
    groupby = []
    window = None

    # Only filers in disjunctive normal form are accepted
    def __init__(self, filters):
        self.filters = filters

    def apply_rule(dataframe):
        print dataframe


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


class EqualConstraint:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] == self.value]

    def to_string(self):
        return self.column + "=" + str(self.value)

    @staticmethod
    def from_list(column, value_list):
        return ConstraintSet('OR', [EqualConstraint(column, value) for value in value_list])


class LessConstraint:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] < self.value]

    def to_string(self):
        return self.column + "<" + str(self.value)


class LessEqualConstraint:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] <= self.value]

    def to_string(self):
        return self.column + "<=" + str(self.value)


class MoreConstraint:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] > self.value]

    def to_string(self):
        return self.column + ">" + str(self.value)


class MoreEqualConstraint:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def apply_constraint(self, dataframe):
        return dataframe[dataframe[self.column] >= self.value]

    def to_string(self):
        return self.column + ">=" + str(self.value)


class MoreLessBetweenConstraint:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def apply_constraint(self, dataframe):
        return dataframe[(dataframe[self.column] > self.value[0]) & (dataframe[self.column] < self.value[1])]

    def to_string(self):
        return "(" + self.column + ">" + str(self.value[0]) + " AND " + self.column + "<" + str(self.value[1]) + ")"


class MoreEqualLessBetweenConstraint:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def apply_constraint(self, dataframe):
        return dataframe[(dataframe[self.column] > self.value[0]) & (dataframe[self.column] <= self.value[1])]

    def to_string(self):
        return "(" + self.column + ">=" + str(self.value[0]) + " AND " + self.column + "<" + str(self.value[1]) + ")"


class MoreLessEqualBetweenConstraint:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def apply_constraint(self, dataframe):
        return dataframe[(dataframe[self.column] >= self.value[0]) & (dataframe[self.column] < self.value[1])]

    def to_string(self):
        return "(" + self.column + ">" + str(self.value[0]) + " AND " + self.column + "<=" + str(self.value[1]) + ")"


class MoreEqualLessEqualBetweenConstraint:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def apply_constraint(self, dataframe):
        return dataframe[(dataframe[self.column] >= self.value[0]) & (dataframe[self.column] <= self.value[1])]

    def to_string(self):
        return "(" + self.column + ">=" + str(self.value[0]) + " AND " + self.column + "<=" + str(self.value[1]) + ")"


rules = {'=': EqualConstraint.from_list, '<': LessConstraint, '>': MoreConstraint, '<=': LessEqualConstraint,
         '>=': MoreEqualConstraint, '<>': MoreLessBetweenConstraint, '<>=': MoreEqualLessBetweenConstraint,
         '<=>': MoreLessEqualBetweenConstraint, '<=>=': MoreEqualLessEqualBetweenConstraint}