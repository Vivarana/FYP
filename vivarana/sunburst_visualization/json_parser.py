import os
import json
from django.core.files import File
import logging
import vivarana.extensions.log.apachelog as apachelog
import vivarana.sunburst_visualization.data_processor as sh
from vivarana.sunburst_visualization.constants import COALESCE_SEPARATOR
from vivarana.sunburst_visualization.constants import NAME_ATTRIB,SIZE_ATTRIB,ROOT_NAME,CHILDREN_ATTRIB
import pandas as pd
import json
import ipdb
logger = logging.getLogger(__name__)

# Commented code is needed for testing purposes

# def handle_log(file_in):
#     # Set the log format to common
#     log_format = apachelog.formats['common']
#     parser = apachelog.parser(log_format)
#
#     script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
#     rel_path = "../../media/temp.log"
#     abs_temp_log_file_path = os.path.join(script_dir, rel_path)
#     with open(abs_temp_log_file_path, 'wb+') as destination:
#         for chunk in file_in.chunks():
#             destination.write(chunk)
#
#     log_list = []
#
#     try:
#         with open(abs_temp_log_file_path, 'r') as log_file:
#             for line in log_file.readlines():
#                 log_list.append(parser.parse(line))
#     except apachelog.ApacheLogParserError, e:
#         print e
#         return {'success': False, 'error': 'PARSE-ERROR'}
#
#     original_data_frame = pd.DataFrame(log_list)
#
#     # Convert the size column to integer from string
#     if 'Size(bytes)' in original_data_frame.columns:
#         original_data_frame['Size(bytes)'] = original_data_frame['Size(bytes)'].replace('-', 0)
#         original_data_frame['Size(bytes)'].apply(int)
#         original_data_frame['Size(bytes)'] = original_data_frame['Size(bytes)'].astype(int)
#
#     # Splitting the request line. todo : Fix the errors when the format doesnt match
#     if 'request' in original_data_frame.columns:
#         temp = original_data_frame.request.str.split(' ')
#         original_data_frame['Method'] = temp.str[0]
#         original_data_frame['URL'] = temp.str[1]
#         original_data_frame['Protocol'] = temp.str[-1]
#
#     return {'success': True, 'dataframe': original_data_frame}


def build_json_hierarchy(ndarray_data):
    """

    :rtype : object
    Builds json tree from csv: csv format = account-account-product 2009
    :param ndarray_data:
    :return:
    """
    root = {NAME_ATTRIB: ROOT_NAME, CHILDREN_ATTRIB: []}
    for x in ndarray_data:
        sequence = x[0]
        if isinstance(x[1], long) == False:
            continue
        size = x[1]
        parts = sequence.split(COALESCE_SEPARATOR)
        current_node = root
        for index in range(len(parts)):
            # print sequence, size,type(parts)
            children = current_node[CHILDREN_ATTRIB]
            nodename = parts[index]
            child_node = []
            if index + 1 < len(parts):
                found_child = False
                for k in range(len(children)):
                    if children[k][NAME_ATTRIB] == nodename:
                        child_node = children[k]
                        found_child = True
                        break
                if found_child is False:
                    child_node = {NAME_ATTRIB: nodename, CHILDREN_ATTRIB: []}
                    children.append(child_node)
                current_node = child_node
            else:
                child_node = {NAME_ATTRIB: nodename, SIZE_ATTRIB: size}
                children.append(child_node)
    return json.dumps(root)

def build_json_hierarchy_log(series_data):

    """
    Builds the json hierarchy from the dataframe created by log files
    :param series_data: grouped rows with sizes
    :return:            json structure that is used by d3 partition layout
    """
    root = {NAME_ATTRIB: ROOT_NAME, CHILDREN_ATTRIB: []}
    print root,series_data

    for x in range(len(series_data)):
        sequence = series_data.index[x]
        size = series_data[x]
        parts = sequence.split(COALESCE_SEPARATOR)
        current_node = root
        for index in range(len(parts)):
            #print parts,index,len(parts),current_node#sequence, size,type(parts)
            children = current_node[CHILDREN_ATTRIB]
            nodename = parts[index]
            child_node = []
            if index + 1 < len(parts): #Not yet at the end of the sequence; move down the tree.
                found_child = False
                for k in range(len(children)):
                    if children[k][NAME_ATTRIB] == nodename:
                        child_node = children[k]
                        found_child = True
                        break
                if found_child is False:
                    child_node = {NAME_ATTRIB: nodename, CHILDREN_ATTRIB: []}
                    children.append(child_node)
                current_node = child_node
            else:
                child_node = {NAME_ATTRIB: nodename, SIZE_ATTRIB: size}
                children.append(child_node)
    return json.dumps(root)

def convert_to_d3_csv_parse_rows_input(series_data):
    dataframe = pd.DataFrame(series_data,columns = ["amount"])
    dataframe["total"] = dataframe.index
    return dataframe.to_json(orient ='values')



def main():
    # file_in = File(open("C:\Users\Developer\Documents\FYP\ssl_access_log.log", "rb"))
    # result = handle_log(file_in)
    # if result['success']:
    #     result['dataframe'].to_csv('../../media/logdata.csv')
    ndarray_data = pd.read_csv('C:/Users/Developer/Documents/FYP/FYP/media/logdata.csv')
    tree = build_json_hierarchy_log(sh.get_sessions_data(ndarray_data))
    print json.dumps(tree)

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()


def categorize_frame(dataframe):
    print new_frame['dataframe']
