import logging

import pandas as pd

from vivarana.constants import TEMP_FILE_PATH

logger = logging.getLogger(__name__)


def handle_csv(file_in):
    """
    Parse the CSV file using Pandas in-build read_csv method
    :param file_in: CSV file uploaded by the user
    :return: 'success' True if parsing is successful and False if parsing failed
            'dataframe' Pandas dataframe containing parsed data only when parsing is successful

    """
    try:
        with open(TEMP_FILE_PATH, 'r') as csv_file:
            original_data_frame = pd.read_csv(csv_file)
        return {'success': True, 'dataframe': original_data_frame}

    except Exception, e:
        logger.error("Error parsing file : " + file_in , e)
        return {'success': False, 'error': {'type': 'Parse Error', 'message': 'Error while parsing file.'}}