from pandas import rolling_mean, rolling_max
import pandas as pd
import numpy as np
from datetime import timedelta

df = ""
attribute = ""


def sum_window(row):
    return df[attribute].iloc[row['start_index']:row['end_index'] + 1].sum()


def sum_of_window(time_window_value, time_granularity, attribute_name, current_data_frame):
    # todo prevent further sum
    # todo add method to reset axix
    global df, attribute
    attribute = attribute_name
    df = current_data_frame[['Date', attribute]]
    df['Date'] = pd.to_datetime(df['Date'])
    start_dates = df['Date'] - timedelta(minutes=int(time_window_value))
    df['start_index'] = df['Date'].values.searchsorted(start_dates, side='right')
    df['end_index'] = np.arange(len(df))
    new_row = df.apply(sum_window, axis=1)

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