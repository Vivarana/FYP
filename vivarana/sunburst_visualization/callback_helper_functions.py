import json
import re
from vivarana.sunburst_visualization.constants import *

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
def format_string(x,grouping,grouped):
    seq_parsed = json.loads(x)
    event_string = []
    for event in seq_parsed["data"]:
        seq_object = event[grouped]
        event_string.append(seq_object)
    event_string.append("end")
    event_string = COALESCE_SEPARATOR.join(event_string)
    return event_string

##pattern matching and give projected databases

def pattern_match_projection(x, coalesce, pattern):

    """
    this function projects the database from the first element of the sequence..
        Sequence is trimmed from the first index of the first element to be searched

        before running an element in 'sequence_objects' column looks like this
        ['data':[sequence],'projections':[each element in the array {'coalesce(attribute)':'value',
        'index':[index of the locations of element in the sequence]}]]
    """
    if coalesce != "" or pattern != "":
        # convert json string to object
        sequence = json.loads(x["sequence_objects"])
        # get values of the dict
        dict_arr = sequence["data"]
        projection_arr = sequence["projections"]
        counter = sequence["counter"]

        match = ""

        trimmed = True
        matchFound = False
        #print type(counter),counter
        # checking if any projection was done
        if counter == -1:
            trimmed = False
            seq_no=0
        else:
            seq_no=projection_arr[counter]

        while seq_no < len(dict_arr):
            #print dict_arr[seq_no]
            if str(dict_arr[seq_no][coalesce]) == str(pattern):
                matchFound = True
                match = str(dict_arr[seq_no][coalesce])
                #print match, seq_no
                if trimmed==False:
                    # if this is the first ever projection trim sequence and reset counter
                    dict_arr = dict_arr[seq_no:]
                    sequence["data"] = dict_arr
                    trimmed ==True
                    projection_arr.append(0)
                    break
                else:
                    projection_arr.append(seq_no)
                    break
            seq_no +=1
        if matchFound == True:
            #print match, pattern_data , dict_arr
            counter += 1
            sequence["counter"] = counter
            return json.dumps(sequence)
        else:
            return "blank"
    else:
        return x


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