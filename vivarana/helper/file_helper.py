from datetime import datetime
import re
import pandas as pd
import apachelog
import string

CATEGORICAL_COLUMN_THRESHOLD = 10

#extra parameters specifying header names in * headers
def handle_uploaded_file(file_in, *headers):
    file_extension = file_in.name.split('.')[-1]
    if file_extension == 'csv':
        return handle_csv(file_in,headers)
    elif file_extension == 'log':
        return handle_log(file_in)
    else:
        return {'success': False, 'error': 'Sorry. File type ' + file_extension + ' is not supported'}

def handle_csv(file_in, *headers):
    try:
        with open("media/temp.csv", 'wb+') as destination:
            for chunk in file_in.chunks():
                destination.write(chunk)

        with open("media/temp.csv", 'r') as csv_file:
            #check header parameters
            # print type(headers)
            # if headers[0][0] == 0:
            original_data_frame = pd.read_csv(csv_file)
            # elif headers[0][0] == 'none':
            #     original_data_frame = pd.read_csv(csv_file,header='None',names = headers [0][1])

        return {'success': True, 'dataframe': original_data_frame}
    except Exception, e:
        print str(e)
        return {'success': False}


def handle_log(file_in):
    # Set the log format to common
    log_format = apachelog.formats['common']
    parser = apachelog.parser(log_format)

    with open("media/temp.log", 'wb+') as destination:
        for chunk in file_in.chunks():
            destination.write(chunk)

    log_list = []

    try:
        with open("media/temp.log", 'r') as log_file:
            for line in log_file.readlines():
                log_list.append(parser.parse(line))
    except apachelog.ApacheLogParserError, e:
        print e
        return {'success': False, 'error': 'PARSE-ERROR'}

    original_data_frame = pd.DataFrame(log_list)

    # Convert the size column to integer from string todo : Set constants for these
    if 'Size' in original_data_frame.columns:
        original_data_frame['Size'] = original_data_frame['Size'].replace('-', 0)
        original_data_frame['Size'].apply(int)
        original_data_frame['Size'] = original_data_frame['Size'].astype(int)

    if 'Date' in original_data_frame.columns:
        original_data_frame['Date'] = pd.to_datetime(original_data_frame['Date'], format="[%d/%b/%Y:%H:%M:%S +0530]")

    # Splitting the request line. todo : Fix the errors when the format doesnt match
    if 'request' in original_data_frame.columns:
        temp = original_data_frame.request.str.split(' ')
        original_data_frame['Method'] = temp.str[0]
        original_data_frame['URL'] = temp.str[1]
        original_data_frame['Protocol'] = temp.str[-1]
        original_data_frame = original_data_frame.drop('request', 1)

    original_data_frame.to_csv('media/parsed_log.csv', index=False)
    return {'success': True, 'dataframe': original_data_frame}


def parse_date(date):
    return date.split(' ')[0]


def load_data(filename, dataframe):
    columns = list(dataframe.columns)
    data_types = list(dataframe.dtypes)
    descriptions = dataframe.describe()

    # todo:  Fix this hackish code
    column_data = [
        (columns[col], data_types[col], '</br>'.join(dataframe[columns[col]].describe().to_string().split('\n'))) for col
        in xrange(len(columns))]

    return {"filename": filename, "columns": column_data, "size": len(dataframe)}


def remove_columns(needed_columns, dataframe):
    new_dataframe = dataframe.copy(deep=True)
    column_list = [new_dataframe.columns[int(i) - 1] for i in needed_columns]
    return new_dataframe[column_list]


# return the column types in a format compatible with the paracoords library
def get_compatible_column_types(dataframe):
    columns = list(dataframe.columns)

    data_types = list(dataframe.dtypes)

    for i, col_type in enumerate(data_types):
        if col_type == 'object':
            data_types[i] = 'string'
        elif col_type == 'int64':
            if len(pd.unique(dataframe[columns[i]])) <= CATEGORICAL_COLUMN_THRESHOLD:
                data_types[i] = 'string'
                dataframe[columns[i]] = dataframe[columns[i]].astype('object')
            else:
                data_types[i] = 'number'
        elif col_type == 'float64':
            if len(pd.unique(dataframe[columns[i]])) <= CATEGORICAL_COLUMN_THRESHOLD:
                data_types[i] = 'string'
                dataframe[columns[i]] = dataframe[columns[i]].astype('object')
            else:
                data_types[i] = 'number'
        elif col_type == 'int32':
            if len(pd.unique(dataframe[columns[i]])) <= CATEGORICAL_COLUMN_THRESHOLD:
                data_types[i] = 'string'
                dataframe[columns[i]] = dataframe[columns[i]].astype('object')
            else:
                data_types[i] = 'number'
        elif col_type == 'float32':
            if len(pd.unique(dataframe[columns[i]])) <= CATEGORICAL_COLUMN_THRESHOLD:
                data_types[i] = 'string'
                dataframe[columns[i]] = dataframe[columns[i]].astype('object')
            else:
                data_types[i] = 'number'
        else:
            data_types[i] = 'string'  # todo : change this!

    column_data = [(columns[col], data_types[col]) for col in xrange(len(columns))]
    return dict(column_data)


def get_html_friendly_names(columns):
    return [remove_illegal_characters(column_name) for column_name in columns]


def remove_illegal_characters(name):
    valid_chars = "_.%s%s" % (string.ascii_letters, string.digits)
    return ''.join([letter for letter in name if letter in valid_chars])