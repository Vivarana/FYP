from vivarana.constants import *
from vivarana.helper.state_info import set_current_data


def process_pagination(state_map, current_data_frame):
    page_number = state_map[ACTIVE_PAGE_NUMBER]
    # minus one to convert zero based to one based
    is_last_page = state_map[NUMBER_PAGES] - 1 == page_number
    data_start = page_number * state_map[PAGE_SIZE]
    data_end = (page_number + 1) * state_map[PAGE_SIZE]

    set_current_data(state_map, data_start, data_end, page_number)

    if state_map[NUMBER_PAGES] > 1:
        if is_last_page:
            json_output = (current_data_frame[data_start:]).to_json(orient='records', date_format='iso')
        else:
            json_output = (current_data_frame[data_start:data_end]).to_json(orient='records', date_format='iso')
    else:
        json_output = current_data_frame.to_json(orient='records', date_format='iso')

    return data_start, is_last_page, json_output