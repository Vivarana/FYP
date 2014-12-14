import pandas as pd
import numpy as np
import time

path = 'C:\Users\Developer\Documents\FYP\FYP\media\logdata.csv'
frame = pd.read_csv(path, index_col='Time', parse_dates=True, encoding='latin1')

def convertdate(date):
    return time.strptime(date, u"[%d/%b/%Y:%H:%M:%S +0530]")
def reformatdate(date):
    return time.strftime("%Y-%m-%d %H:%M:%S",date)

hosts = frame['Remote host']
frame.index = pd.to_datetime(pd.Series([reformatdate(convertdate(date)) for date in frame.index]))

newframe = frame.copy()
newframe.columns
