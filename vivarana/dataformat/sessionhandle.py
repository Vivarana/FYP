import pandas as pd
import numpy as np
import time
import copy
import json

def convertdate(date):
    return time.strptime(date, u"[%d/%b/%Y:%H:%M:%S +0530]")
def reformatdate(date):
    return time.strftime("%Y-%m-%d %H:%M:%S",date)

def parse_dataframe_date(dataframe):
    dataframe.index = pd.to_datetime(pd.Series([reformatdate(convertdate(date)) for date in dataframe.index]))
    return dataframe

def get_session_info(dataframe):
    paths = dataframe.groupby('Remote_host')['URL'].apply(lambda x: "%s" % '-'.join(x)) # .apply(lambda x: x.values)
    return paths.value_counts()

def get_unique_urls(dataframe,coalesce):
    urls = dataframe[coalesce].fillna('Null')
    uniqueurls = pd.Series(urls.values.ravel()).unique()
    return uniqueurls.tolist()

def get_sessions_data(frame,group_by,coalesce):
    dataframe = frame.copy(deep=True) #pd.read_csv(path, index_col='Time', parse_dates=True)
    dataframe[coalesce] = dataframe[coalesce].astype('string_') # need to be done for unicode conversion
    paths = dataframe.groupby(group_by)[coalesce].apply(lambda x: "%s" % '-'.join(x)) # .apply(lambda x: x.values)
    ## remove sequences longer than 10 todo:show these as well
    df = pd.DataFrame(paths)
    df["seq_len"] = df[coalesce].apply(lambda x: len(x.split("-")))
    sdf = df[df['seq_len'] <10]
    ## get count of unique sequences

    return sdf[coalesce].value_counts().astype(int)


def main():
    path = 'C:\Users\Developer\Documents\FYP\FYP\media\logdata.csv'
    frame = pd.read_csv(path, index_col='Date', parse_dates=True)
    frame['URL'] = frame['URL'].astype('string_') # need to be done for unicode conversion
    #frame = parse_dataframe_date(frame)
    frame1 = copy.copy(frame)
    frame2 = copy.copy(frame)
    #print get_session_info(frame1)
    print type(get_unique_urls(frame2))


if __name__ == '__main__':
    main()