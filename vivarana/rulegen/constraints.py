import pandas as pd
from sklearn import tree
from sklearn.metrics import confusion_matrix

SELECTED_COLUMN = 'selected_for_rulegen'

def get_positive_traces(input_data):
    return input_data[input_data[SELECTED_COLUMN] == 1]

def identify_constraints(input_traces):
    constraints = []

    for column in input_traces.columns - [SELECTED_COLUMN]:
        unique_values = pd.unique(input_traces[column])
        if len(unique_values) == 1:
            constraints.append(('EQUAL',column, unique_values[0]))
        elif input_traces.dtypes[column] == 'object':
            constraints.append(('SET',column, unique_values))
        else:
            constraints.append(('MINMAX',column, (input_traces[column].min(axis=1),input_traces[column].max(axis=1))))

    return constraints


def identify_equality_constraints(input_traces):
    equality_constraints = []
    for column in input_traces.columns - [SELECTED_COLUMN]:
        unique_values = pd.unique(input_traces[column])
        if len(unique_values) == 1:
            equality_constraints.append((column, unique_values[0]))

    return equality_constraints

def apply_constraints(row):
    for constraint,value in equality_constraints_list:
        if row[constraint] != value:
            return False
    return True

# def get_tree(dataframe):
#     clf = tree.DecisionTreeClassifier()
#     clf = clf.fit(dataframe.drop(SELECTED_COLUMN,1), dataframe[SELECTED_COLUMN])
#     print clf

def get_precision(confusion_matrix):
    return (confusion_matrix[1][1])/float(confusion_matrix[0][1] + confusion_matrix[1][1])

def get_recall(confusion_matrix):
    return (confusion_matrix[1][1])/float( confusion_matrix[1][1]+confusion_matrix[1][0])


with open("output.csv", 'r') as csv_file:
    dataframe = pd.read_csv(csv_file)

    get_tree(dataframe)

    # positive_traces = get_positive_traces(dataframe)
    # equality_constraints_list = identify_constraints(positive_traces)
    #
    # print equality_constraints_list
    # for column, value in equality_constraints_list:
    #     print column

    # filtered_columns = dataframe.apply(apply_constraints, axis=1)
    # confusion_mat = confusion_matrix(dataframe[SELECTED_COLUMN], filtered_columns)

    # print confusion_mat
    # print get_precision(confusion_mat), get_recall(confusion_mat)