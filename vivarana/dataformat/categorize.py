import pandas as pd;
import numpy as np;

import sys
import os
from django.core.files import File
import vivarana.helper.apachelog as apachelog


def handle_log(file_in):
    # Set the log format to common
    log_format = apachelog.formats['common']
    parser = apachelog.parser(log_format)

    script_dir = os.path.dirname(__file__)  #<-- absolute dir the script is in
    rel_path = "../../media/temp.log"
    abs_temp_log_file_path = os.path.join(script_dir, rel_path)
    with open(abs_temp_log_file_path, 'wb+') as destination:
        for chunk in file_in.chunks():
            destination.write(chunk)

    log_list = []

    try:
        with open(abs_temp_log_file_path, 'r') as log_file:
            for line in log_file.readlines():
                log_list.append(parser.parse(line))
    except apachelog.ApacheLogParserError, e:
        print e
        return {'success': False, 'error': 'PARSE-ERROR'}

    original_data_frame = pd.DataFrame(log_list)

    #Convert the size column to integer from string
    if 'Size(bytes)' in original_data_frame.columns:
        original_data_frame['Size(bytes)'] = original_data_frame['Size(bytes)'].replace('-', 0)
        original_data_frame['Size(bytes)'].apply(int)
        original_data_frame['Size(bytes)'] = original_data_frame['Size(bytes)'].astype(int)

    #Splitting the request line. todo : Fix the errors when the format doesnt match
    if 'request' in original_data_frame.columns:
        temp = original_data_frame.request.str.split(' ')
        original_data_frame['Method'] = temp.str[0]
        original_data_frame['URL'] = temp.str[1]
        original_data_frame['Protocol'] = temp.str[-1]

    return {'success': True, 'dataframe': original_data_frame}


def main():
    file_in = File(open("C:\Users\Developer\Documents\FYP\ssl_access_log.log", "rb"))
    result = handle_log(file_in)
    if result['success']:
        result['dataframe'].to_csv('../../media/logdata.csv')

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()


def categorize_frame(dataframe):
    global new_frame
    new_frame = dataframe

    # print new_frame['dataframe']
