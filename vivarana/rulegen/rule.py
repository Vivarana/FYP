__author__ = 'Vimuth'


class Rule:

    filters = []
    groupby = []
    window = None

    # Only filers in disjunctive normal form are accepted
    def __init__(self, filters):
        self.filters = filters

    def apply_rule(dataframe):

        print dataframe

