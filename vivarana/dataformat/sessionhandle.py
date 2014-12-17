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
    paths = dataframe.groupby('Remote host')['URL'].apply(lambda x: "%s" % '-'.join(x)) # .apply(lambda x: x.values)
    return paths.value_counts().to_json(orient='split')

def get_unique_urls(dataframe):
    urls = dataframe['URL']
    uniqueurls = pd.Series(urls.values.ravel()).unique()
    return json.dumps(uniqueurls.tolist())

def get_sessions_data(frame,type):
    dataframe = frame.copy(deep=True) #pd.read_csv(path, index_col='Time', parse_dates=True)
    dataframe['URL'] = dataframe['URL'].astype('string_') # need to be done for unicode conversion
    print dataframe
    #dataframe = parse_dataframe_date(dataframe)
    if type=='uniqueurls':
        return get_unique_urls(dataframe)
    elif type=='info':
        return get_session_info(dataframe)
    else:
        return "Please give data type you want"

def main():
    path = 'C:\Users\Developer\Documents\FYP\FYP\media\logdata.csv'
    frame = pd.read_csv(path, index_col='Time', parse_dates=True)
    frame['URL'] = frame['URL'].astype('string_') # need to be done for unicode conversion
    frame = parse_dataframe_date(frame)
    frame1 = copy.copy(frame)
    frame2 = copy.copy(frame)
    print get_session_info(frame1)
    print get_unique_urls(frame2)


if __name__ == '__main__':
    main()