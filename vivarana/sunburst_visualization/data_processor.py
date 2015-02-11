import pandas as pd
import numpy as np
import time
import copy
import json
import ipdb
from vivarana.sunburst_visualization.constants import *
from vivarana.sunburst_visualization.callback_helper_functions import *

sequence_database = None
stripped_database = None
grouping_column = None
grouped_column = None

### deprecated but still used Functions
def get_session_info(dataframe, group_by, coalesce):
    paths = dataframe.groupby(group_by)[coalesce].apply(
        lambda x: "%s" % COALESCE_SEPARATOR.join(x))  # .apply(lambda x: x.values)
    return paths.value_counts()

def get_unique_coalesce_strings(dataframe, coalesce):
    urls = dataframe[coalesce].fillna('Null')
    unique_strings = pd.Series(urls.values.ravel()).unique()
    return unique_strings.tolist()

def get_sessions_data(frame, group_by, coalesce):
    """
    This function groups data from from one column and gets the result
    :param frame: dataframe
    :param group_by: grouping column name
    :param coalesce: grouped column name
    :return: grouping result
    """
    dataframe = frame.copy(deep=True)  # pd.read_csv(path, index_col='Time', parse_dates=True)
    dataframe[coalesce] = dataframe[coalesce].astype('string')  # need to be done for unicode conversion
    # # % is string format function it's deprecated, "%s" will capture any string after % operater
    paths = dataframe.groupby(group_by)[coalesce].apply(
        lambda x: "%s" % COALESCE_SEPARATOR.join(x))  #"%s" % COALESCE_SEPARATOR.join(x)) # .apply(lambda x: x.values)
    ## truncate sequences longer than limit add end tag for shorter sequences
    df = pd.DataFrame(paths)
    df.columns = [coalesce]

    df[SEQ_LENGTH_NAME] = df[coalesce].apply(lambda x: len(x.split(COALESCE_SEPARATOR)))
    df[coalesce] = df.apply(
        lambda x: x[0] + COALESCE_SEPARATOR + SEQ_END_TAG if x[1] < SEQ_LIMIT else COALESCE_SEPARATOR.join(
            x[0].split(COALESCE_SEPARATOR)[:SEQ_LIMIT]), axis=1)
    #get count of unique sequences
    #print df
    #pd.DataFrame(df[coalesce].value_counts().astype(int)).to_csv("D:\out.csv")
    return df[coalesce].value_counts().astype(int)

########################################################
def create_database(data_frame, group_by, coalesce):
    global sequence_database,grouping_column,grouped_column
    grouping_column = group_by
    grouped_column = coalesce
    data_frame = data_frame.copy(deep=True)
    # need to be done for unicode conversion
    for col in data_frame.columns:
        if isinstance(data_frame[col][1], pd.tslib.Timestamp):
            data_frame[col] = pd.Series([str(date) for date in data_frame[col]])
        else:
            data_frame[col] = data_frame[col].astype('string_')
    #print type(data_frame["Date"][1]),data_frame['Date'][1]
    # splits groups given frame by given separator
    paths = data_frame.groupby([group_by])
    #view grouped dataframes
    #for path in paths:
    #    print path
    ## combine by making each row a dict in the new dataframe
    dictised_frame = paths.apply(lambda x: x.apply(event_dict, axis=1))
    # further group returned multiindex representation
    reduced_frame = dictised_frame.groupby(level=0).apply(event_seq_no)
    database = pd.DataFrame(reduced_frame, columns=["sequence_objects"])
    sequence_database = database.copy(deep=True)
    #ipdb.set_trace();

def strip_objects(coalesce):
    global sequence_database
    global stripped_database
    stripped_database = sequence_database.copy(deep = True)
    stripped_database["sequence_objects"] = stripped_database["sequence_objects"].apply(format_string)
    return stripped_database["sequence_objects"].value_counts().astype(int)

def get_columns():
    return [grouping_column,grouped_column]
def main():
    path = 'C:\Users\Developer\Documents\FYP\FYP\media\logdata.csv'
    frame = pd.read_csv(path, index_col='Date', parse_dates=True)
    frame['URL'] = frame['URL'].astype('string_')  # need to be done for unicode conversion
    #frame = parse_dataframe_date(frame,"URL")
    frame1 = copy.copy(frame)
    frame2 = copy.copy(frame)
    #print get_session_info(frame1)
    get_sessions_data(frame2, "Remote_host", "URL")


if __name__ == '__main__':
    main()