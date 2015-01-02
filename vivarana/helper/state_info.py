from vivarana.constants import DATA_LST, CURRENT_PAGE_NUMBER, AGGREGATE_FUNCTION_ON_ATTR, WINDOW_TYPE, TIME_GRANULARITY, \
    TIME_WINDOW_ENABLED, TIME_WINDOW_VALUE, EVENT_WINDOW_VALUE


def get_current_page_no(state_map):
    a = state_map[DATA_LST]
    b = a[-1]
    c = b[CURRENT_PAGE_NUMBER]
    return state_map[DATA_LST][-1][CURRENT_PAGE_NUMBER]


def set_current_page_no(state_map, num):
    data_lst = state_map[DATA_LST]
    if len(data_lst) == 0:
        state_map[DATA_LST].append({CURRENT_PAGE_NUMBER: num})
    else:
        state_map[DATA_LST][-1][CURRENT_PAGE_NUMBER] = num


def increment_current_page_no(state_map):
    state_map[DATA_LST][-1][CURRENT_PAGE_NUMBER] += 1


def decrement_current_page_no(state_map):
    state_map[DATA_LST][-1][CURRENT_PAGE_NUMBER] -= 1


def set_aggregate_state(state_map, aggregate_func, attribute_name):
    time_window_enabled = state_map[TIME_WINDOW_ENABLED]
    if time_window_enabled:
        state_map[AGGREGATE_FUNCTION_ON_ATTR][attribute_name] = (
            aggregate_func, state_map[WINDOW_TYPE], state_map[TIME_GRANULARITY], state_map[TIME_WINDOW_VALUE])
    else:
        state_map[AGGREGATE_FUNCTION_ON_ATTR][attribute_name] = (
            aggregate_func, state_map[WINDOW_TYPE], None, state_map[EVENT_WINDOW_VALUE])


def clear_aggregate_state(state_map, attribute_name):
    del state_map[AGGREGATE_FUNCTION_ON_ATTR][attribute_name]
