import data_processor as sun_dp
import json_parser as sun_jp
import constants as sun_ct

import json


def initialize_database(cur_dataframe,groupby,coalesce):
    sun_dp.create_database(cur_dataframe,groupby,coalesce)


def give_tree_data_structure(cur_dataframe,coalesce):
    if len(cur_dataframe.columns) == 2:
        json_tree = sun_jp.build_json_hierarchy(cur_dataframe.values)
    else:
        json_tree = sun_jp.convert_to_d3_csv_parse_rows_input(sun_dp.strip_objects(coalesce))
    return json_tree


def give_unique_coalesce_strings(cur_dataframe,coalesce):
    return json.dumps(sun_dp.get_unique_coalesce_strings(cur_dataframe, coalesce))

