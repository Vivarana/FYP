import pandas as pd
import numpy as np
import apachelog


def handle_uploaded_file(file_in):
    file_extension = file_in.name.split('.')[-1]
    if file_extension == 'csv':
        return handle_csv(file_in)
    elif file_extension == 'log':
        return handle_log(file_in)
    else:
        return {'success': False, 'error': 'Sorry. File type '+file_extension+' is not supported'}


def handle_csv(file_in):
    try:
        with open("media/temp.csv", 'wb+') as destination:
            for chunk in file_in.chunks():
                destination.write(chunk)

        with open("media/temp.csv", 'r') as csv_file:
            original_data_frame = pd.read_csv(csv_file)

            print list(original_data_frame.columns)
            return {'success': True, 'dataframe' : original_data_frame}
    except Exception,e:
        print str(e)
        return {'success': False}


def handle_log(file_in):
    log_format = r'%h %l %u %t \"%r\" %>s %b'
    parser = apachelog.parser(log_format)

    with open("media/temp.log", 'wb+') as destination:
            for chunk in file_in.chunks():
                destination.write(chunk)

    log_list = []

    try:
        with open("media/temp.log", 'r') as log_file:
            for line in log_file.readlines():
                log_list.append(parser.parse(line))
    except apachelog.ApacheLogParserError,e:
        print e
        return {'success': False, 'error': 'PARSE-ERROR'}

    original_data_frame = pd.DataFrame(log_list)

    original_data_frame['%b'] = original_data_frame['%b'].replace('-', 0)
    original_data_frame['%b'].apply(int)
    original_data_frame['%b'] = original_data_frame['%b'].astype(int)

    print original_data_frame.info()
    return {'success': True, 'dataframe' : original_data_frame}


def load_data(filename, dataframe):
    columns = list(dataframe.columns)
    data_types = list(dataframe.dtypes)
    column_data = [(columns[col], data_types[col]) for col in xrange(len(columns))]
    return {"filename": filename, "columns": column_data}

def remove_columns(needed_columns, dataframe):
    column_list = [dataframe.columns[int(i)-1] for i in needed_columns]
    return  dataframe[column_list]