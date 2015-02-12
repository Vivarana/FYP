import json
import copy
from vivarana.constants import *


def get_state_info(state_map):
    state = copy.deepcopy(state_map)
    del state[DATA_LST]
    return state


def set_current_data_lst(state_map, selected_id_lst):
    new_data_dict = {CURRENT_ROW_IDS_LST: selected_id_lst, CURRENT_PAGE_NUMBER: state_map[ACTIVE_PAGE_NUMBER]}
    state_map[DATA_LST].append(new_data_dict)


def set_current_data(state_map, start_id, end_id, current_page_no):
    data_lst = state_map[DATA_LST]
    if len(data_lst) == 0:
        data_lst.append(
            {CURRENT_ROW_IDS_LST: range(start_id, end_id), CLUSTER_IDS_DICT: {}, CURRENT_PAGE_NUMBER: current_page_no})
    else:
        new_data = {CURRENT_ROW_IDS_LST: range(start_id, end_id), CLUSTER_IDS_DICT: {},
                    CURRENT_PAGE_NUMBER: current_page_no}
        if data_lst[-1] != new_data:
            data_lst.append(new_data)
    write_state_to_file(state_map)


def set_current_data_on_clustering(state_map, selected_ids, clustered_dict):
    data_lst = state_map[DATA_LST]
    data_lst.append({CURRENT_ROW_IDS_LST: selected_ids, CLUSTER_IDS_DICT: clustered_dict,
                     CURRENT_PAGE_NUMBER: state_map[ACTIVE_PAGE_NUMBER]})
    write_state_to_file(state_map)


def set_aggregate_state(state_map, aggregate_func, attribute_name):
    time_window_enabled = state_map[TIME_WINDOW_ENABLED]
    if time_window_enabled:
        state_map[AGGREGATE_FUNCTION_ON_ATTR][attribute_name] = (
            aggregate_func, state_map[WINDOW_TYPE], state_map[TIME_GRANULARITY], state_map[TIME_WINDOW_VALUE],
            state_map[AGGREGATE_GROUP_BY_ATTR])
    else:
        state_map[AGGREGATE_FUNCTION_ON_ATTR][attribute_name] = (
            aggregate_func, state_map[WINDOW_TYPE], None, state_map[EVENT_WINDOW_VALUE],
            state_map[AGGREGATE_GROUP_BY_ATTR])
    write_state_to_file(state_map)


def clear_aggregate_state(state_map, attribute_name):
    del state_map[AGGREGATE_FUNCTION_ON_ATTR][attribute_name]
    write_state_to_file(state_map)


def update_kept_attribute(state_map, kept_attributes):
    removed_attr = state_map[REMOVED_ATTRIBUTE_LST]
    all_attr = state_map[ALL_ATTRIBUTE_LST]
    newly_removed_attr = list(set(all_attr).difference(set(kept_attributes)))
    state_map[REMOVED_ATTRIBUTE_LST] = list(set(removed_attr + newly_removed_attr))
    write_state_to_file(state_map)


def remove_attribute(attribute_name, state_map, current_data_frame):
    state_map[REMOVED_ATTRIBUTE_LST].append(attribute_name)
    current_data_frame.drop(attribute_name, axis=1, inplace=True)
    write_state_to_file(state_map)


def get_current_attribute_list(state_map):
    return list(set(state_map[ALL_ATTRIBUTE_LST]).difference(set(state_map[REMOVED_ATTRIBUTE_LST])))


def write_state_to_file(state_map):
    a = 1
    # with open('state.json', 'a') as fp:
    # json.dump(state_map, fp)
    # fp.write("\n")