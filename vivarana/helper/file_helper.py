import string

import pandas as pd

from vivarana.constants import EXT_CSV, EXT_LOG
from vivarana.extensions.csv.csv_handler import handle_csv
from vivarana.extensions.log.logfile_handler import handle_log
from vivarana.properties import CATEGORICAL_COLUMN_THRESHOLD

col_type_dict = {
    "int64": "number", "float64": "number",
    "int32": "number", "float32": "number", "object": "string"
}


def handle_uploaded_file(file_in, ):
    """ Handles the uploaded file.
    Do not include file type specific parsing code within this method.
    Call an external  method according to the file extension.
    
    IMPORTANT : the respective method should return a valid Pandas data frame
                containing the data of the parsed file.

    :param file_in: input file uploaded by the user
    :return: 'success', 'dataframe' if the file has been parsed successfully
            'error' if the file type is not supported
    """
    file_extension = file_in.split('.')[-1]
    if file_extension == EXT_CSV:
        return handle_csv(file_in)
    elif file_extension == EXT_LOG:
        return handle_log(file_in)
    else:
        return {'success': False,
                'error': 'Sorry. File type ' + file_extension + ' is not supported or parsing error occurred'}


def get_data_summary(dataframe):
    """
    Return the summary of given dataframe
    :param dataframe: Pandas Data frame
    :return: 'columns' a list tuples containing
            (column name, column type, [list of statistical information on attribute])
            'size' number of rows in the data frame
    """
    columns = list(dataframe.columns)
    data_types = list(dataframe.dtypes)

    column_data = [
        (columns[col], data_types[col], dataframe[columns[col]].describe().to_string().split('\n')) for
        col
        in xrange(len(columns))]

    return {"columns": column_data, "size": len(dataframe)}


def remove_columns(needed_columns, dataframe):
    """
    :param needed_columns: list of required columns
    :param dataframe: Pandas Dataframe
    :return:a new Pandas dataframe which contains only the given columns
    """
    new_dataframe = dataframe.copy(deep=True)
    column_list = [new_dataframe.columns[int(i) - 1] for i in needed_columns]
    return new_dataframe[column_list]


def get_compatible_column_types(dataframe):
    """
    :param dataframe: Parsed pandas dataframe
    :return: the column types in a format compatible with the paracoords library
    """
    columns = list(dataframe.columns)
    data_types = list(dataframe.dtypes)

    for i, col_type in enumerate(data_types):
        col_type = str(col_type)
        if col_type in col_type_dict:
            if len(pd.unique(dataframe[columns[i]])) <= CATEGORICAL_COLUMN_THRESHOLD:
                data_types[i] = 'string'
                dataframe[columns[i]] = dataframe[columns[i]].astype('object')
            else:
                data_types[i] = col_type_dict[col_type]
        else:
            data_types[i] = 'string'

    column_data = [(columns[col], data_types[col]) for col in xrange(len(columns))]
    return dict(column_data)


def get_html_friendly_names(columns):
    """
    Removes illegal characters in the column names (HTML escaping)
    """

    without_illegal_chars = [remove_illegal_characters(column_name) for column_name in columns]
    for i in xrange(0, len(without_illegal_chars)):
        if without_illegal_chars[i][0].isdigit():
            without_illegal_chars[i] = "COL_" + without_illegal_chars[i]

    return without_illegal_chars


def remove_illegal_characters(name):
    valid_chars = "_.%s%s" % (string.ascii_letters, string.digits)
    return ''.join([letter for letter in name if letter in valid_chars])