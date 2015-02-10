"""
Log file parsing Handler

It is important to note that if the log file contains a datetime attribute
the respective pandas column name should be named as 'Date'

"""

import logging

import pandas as pd
import os
import ConfigParser
from vivarana.constants import TEMP_FILE_PATH
from vivarana.extensions.log import apachelog
from vivarana.extensions.log.log_constants import *

logger = logging.getLogger(__name__)


def handle_log(file_in):
    """
    Parse the Apache Common log format files
    :param file_in: file uploaded by the user
    :return:  'success' True if parsing is successful and False if parsing failed
            'dataframe' Pandas dataframe containing parsed data only when parsing is successful
    """

    print os.path.dirname(__file__)
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "../../settings.ini"))

    log_format = config.get('parser', 'format')
    print log_format
    parser = apachelog.parser(log_format)

    log_list = []

    try:
        with open(TEMP_FILE_PATH, 'r') as log_file:
            for line in log_file.readlines():
                log_list.append(parser.parse(line))

    except apachelog.ApacheLogParserError, e:
        logger.error("Could not parse " + file_in + "using apache parser", e)
        return {'success': False, 'error': {'type': 'APACHE_LOG_PARSE_ERROR', 'format': log_format}}

    original_data_frame = pd.DataFrame(log_list)

    # Convert the size column to integer from string
    if SIZE in original_data_frame.columns:
        original_data_frame[SIZE] = original_data_frame[SIZE].replace('-', 0)
        original_data_frame[SIZE].apply(int)
        original_data_frame[SIZE] = original_data_frame[SIZE].astype(int)

    if DATE in original_data_frame.columns:
        original_data_frame[DATE] = pd.to_datetime(original_data_frame[DATE], format="[%d/%b/%Y:%H:%M:%S +0530]")

    # Splitting the request line. todo : Fix the errors when the format doesnt match
    if REQUEST in original_data_frame.columns:
        temp = original_data_frame.request.str.split(' ')
        original_data_frame[METHOD] = temp.str[0]
        original_data_frame[URL] = temp.str[1]
        original_data_frame[PROTOCOL] = temp.str[-1]
        original_data_frame = original_data_frame.drop(REQUEST, 1)

    return {'success': True, 'dataframe': original_data_frame}