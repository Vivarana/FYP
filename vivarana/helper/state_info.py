from vivarana.constants import DATA_LST, CURRENT_PAGE_NUMBER


def get_current_page_no(state_map):
    return state_map[DATA_LST][-1][CURRENT_PAGE_NUMBER]


def set_current_page_no(state_map, num):
    data_lst = state_map[DATA_LST]
    if len(data_lst) == 0:
        data_lst = state_map[DATA_LST] = {}
        data_lst[CURRENT_PAGE_NUMBER] = num
    else:
        state_map[DATA_LST][-1][CURRENT_PAGE_NUMBER] = num


def increment_current_page_no(state_map):
    state_map[DATA_LST][-1][CURRENT_PAGE_NUMBER] += 1


def decrement_current_page_no(state_map):
    state_map[DATA_LST][-1][CURRENT_PAGE_NUMBER] -= 1