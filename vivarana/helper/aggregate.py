from pandas import rolling_mean, rolling_max
import numpy as np
from datetime import timedelta

df = ""
attribute = ""


def sum_window(row):
    return df[attribute].iloc[row['start_index']:row['end_index'] + 1].sum()


def sum_of_window(time_window_value, time_granularity, attribute_name, current_data_frame):
    global df, attribute
    df = current_data_frame
    attribute = attribute_name
    print current_data_frame['Date']
    start_dates = current_data_frame['Date'] - timedelta(minutes=int(time_window_value))
    current_data_frame['start_index'] = current_data_frame['Date'].values.searchsorted(start_dates, side='right')
    current_data_frame['end_index'] = np.arange(len(current_data_frame))
    new_row = current_data_frame.apply(sum_window, axis=1)
    current_data_frame.pop(attribute_name)
    current_data_frame[attribute_name] = new_row
    return current_data_frame


# aggregated_sum = rolling_sum(data_frame, windows_size)
# aggregated_attribute = aggregated_sum.pop(attribute)

# return get_modified_df(aggregated_attribute, attribute, data_frame)


def average_of_window(attribute, windows_size, data_frame):
    aggregated_average = rolling_mean(data_frame, windows_size)
    aggregated_attribute = aggregated_average.pop(attribute)

    return get_modified_df(aggregated_attribute, attribute, data_frame)


def max_of_window(attribute, windows_size, data_frame):
    aggregated_max = rolling_max(data_frame, windows_size)
    aggregated_attribute = aggregated_max.pop(attribute)

    return get_modified_df(aggregated_attribute, attribute, data_frame)


def get_modified_df(aggregated_attribute, attribute, data_frame):
    data_frame.pop(attribute)
    data_frame[attribute] = aggregated_attribute
    return data_frame