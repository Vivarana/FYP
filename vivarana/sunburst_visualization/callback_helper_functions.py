import json
from vivarana.constants import GROUPED_COL_NAME
from vivarana.sunburst_visualization.constants import *
import data_processor as sun_dp


maxDepth = 0
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


# further process and add some more values to create seq database structure
def event_seq_no(x):
    global maxDepth
    seq_database = {}
    seq_database["data"]=[]
    seq_database["projections"]=[]
    seq_database["counter"]= -1
    seq_list = seq_database["data"]
    for event_no in range(len(x)):
        dictr = json.loads(x.values[event_no],parse_float=None, parse_int=None, parse_constant=None)
        #add event no of the sequence to event object
        dictr["seq_no"]=event_no
        # get the maximum length of event
        if event_no> maxDepth:
            maxDepth = event_no
        seq_list.append(dictr)
    return json.dumps(seq_database)


# strip event objects to string
def format_string(x):
    seq_parsed = json.loads(x)
    event_string = []
    for event in seq_parsed["data"]:
        seq_object = event[sun_dp.get_columns()[1]]
        event_string.append(seq_object)
    event_string.append("end")
    event_string = COALESCE_SEPARATOR.join(event_string)
    return event_string


### Convert Date Strings #######################################
def convertdate(date):
    return time.strptime(date, u"[%d/%b/%Y:%H:%M:%S +0530]")


def reformatdate(date):
    return time.strftime("%Y-%m-%d %H:%M:%S", date)


def parse_dataframe_date(dataframe):
    dataframe.index = pd.to_datetime(pd.Series([reformatdate(convertdate(date)) for date in dataframe.index]))
    return dataframe


def return_max_depth():
    return maxDepth
###################################################################