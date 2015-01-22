import pandas as pd
import numpy as np
import time
import copy
import json
from vivarana.sunburst_visualization.constants import *

sequence_database = None

def convertdate(date):
    return time.strptime(date, u"[%d/%b/%Y:%H:%M:%S +0530]")
def reformatdate(date):
    return time.strftime("%Y-%m-%d %H:%M:%S",date)

def parse_dataframe_date(dataframe):
    dataframe.index = pd.to_datetime(pd.Series([reformatdate(convertdate(date)) for date in dataframe.index]))
    return dataframe

def get_session_info(dataframe, group_by, coalesce):
   paths = dataframe.groupby(group_by)[coalesce].apply(lambda x: "%s" % COALESCE_SEPARATOR.join(x)) # .apply(lambda x: x.values)
   return paths.value_counts()

def get_unique_urls(dataframe,coalesce):
    urls = dataframe[coalesce].fillna('Null')
    uniqueurls = pd.Series(urls.values.ravel()).unique()
    return uniqueurls.tolist()

def get_sessions_data(frame,group_by,coalesce):
    """
    This function groups datafrom from one column and gets the result
    :param frame: dataframe
    :param group_by: grouping column name
    :param coalesce: grouped column name
    :return: grouping result
    """
    dataframe = frame.copy(deep=True) #pd.read_csv(path, index_col='Time', parse_dates=True)
    dataframe[coalesce] = dataframe[coalesce].astype('string') # need to be done for unicode conversion
    ## % is string format function it's deprecated, "%s" will capture any string after % operater
    paths = dataframe.groupby(group_by)[coalesce].apply(lambda x: "%s" % COALESCE_SEPARATOR.join(x))#"%s" % COALESCE_SEPARATOR.join(x)) # .apply(lambda x: x.values)
    ## truncate sequences longer than limit add end tag for shorter sequences
    df = pd.DataFrame(paths)
    df[SEQ_LENGTH_NAME] = df[coalesce].apply(lambda x: len(x.split(COALESCE_SEPARATOR)))
    df[coalesce] = df.apply(lambda x: x[0]+COALESCE_SEPARATOR+SEQ_END_TAG if x[1]<SEQ_LIMIT else COALESCE_SEPARATOR.join(x[0].split(COALESCE_SEPARATOR)[:SEQ_LIMIT]), axis=1)
    #get count of unique sequences
    #print df
    #pd.DataFrame(df[coalesce].value_counts().astype(int)).to_csv("D:\out.csv")
    return df[coalesce].value_counts().astype(int)

#def windowing(frame,windowtype,*length){

#}
#creates dict from every row of split dataframe by grouping
def event_dict(x):
    y = {}
    #put index value to dict (grouped column element)
    y["tuple_no"] = str(x.name)
    #put other columns to dict
    for l in range(len(x)):
        y[x.index[l]] = x.values[l]
    # return stringified representation
    return json.dumps(y)
# group events together to form a sequence
def event_seq_no(x):
    seq_list=[]
    for event_no in range(len(x)):
        dictr = json.loads(x.values[event_no])
        #add event no of the sequence to event object
        dictr["seq_no"]=event_no
        seq_list.append(dictr)
    return json.dumps(seq_list)

def create_sequence_database(frame,group_by,coalesce):
    dataframe = frame.copy(deep=True)
    dataframe[coalesce] = dataframe[coalesce].astype('string')
    paths = dataframe.groupby(group_by)
    dt = paths.apply(lambda x:x.apply(event_dict,axis=1))
    # further group returned multiindex representation
    # further group returned multiindex representation
    rr =  dt.groupby(level=0).apply(event_seq_no)
    ss = pd.DataFrame(rr,columns = ["sequence_objects"])
    sequence_database = ss;
    #ss[SEQ_LENGTH_NAME] = ss["sequence_objects"].apply(lambda x: len(x.split(COALESCE_SEPARATOR)))
    #ss["sequence_objects"] = ss.apply(lambda x: x[0]+COALESCE_SEPARATOR+SEQ_END_TAG if x[1]<SEQ_LIMIT else COALESCE_SEPARATOR.join(x[0].split(COALESCE_SEPARATOR)[:SEQ_LIMIT]), axis=1)
    #get count of unique sequences
    #print df
    #pd.DataFrame(df[coalesce].value_counts().astype(int)).to_csv("D:\out.csv")
    #return df["sequence_objects"].value_counts().astype(int)

def filter_events(coalesce,event):


def main():
    path = 'C:\Users\Developer\Documents\FYP\FYP\media\logdata.csv'
    frame = pd.read_csv(path, index_col='Date', parse_dates=True)
    frame['URL'] = frame['URL'].astype('string_') # need to be done for unicode conversion
    #frame = parse_dataframe_date(frame,"URL")
    frame1 = copy.copy(frame)
    frame2 = copy.copy(frame)
    #print get_session_info(frame1)
    get_sessions_data(frame2,"Remote_host","URL")


if __name__ == '__main__':
    main()