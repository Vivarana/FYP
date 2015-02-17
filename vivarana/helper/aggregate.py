from datetime import timedelta

import numpy as np
import pandas as pd
from pandas import rolling_sum, rolling_mean, rolling_max, rolling_min, rolling_count


def sum_window(row, df, attribute):
    return df[attribute].iloc[row['start_index']:row['end_index'] + 1].sum()


def avg_window(row, df, attribute):
    return df[attribute].iloc[row['start_index']:row['end_index'] + 1].mean()


def min_window(row, df, attribute):
    return df[attribute].iloc[row['start_index']:row['end_index'] + 1].min()


def max_window(row, df, attribute):
    return df[attribute].iloc[row['start_index']:row['end_index'] + 1].max()


def count_window(row, df, attribute):
    return df[attribute].iloc[row['start_index']:row['end_index'] + 1].count()


def group_sum_window(row, df, attribute, groupby_attr):
    return \
        df[[attribute, groupby_attr]].iloc[row['start_index']:row['end_index'] + 1].groupby(groupby_attr)[
            attribute].sum()[row[groupby_attr]]


def group_avg_window(row, df, attribute, groupby_attr):
    return \
        df[[attribute, groupby_attr]].iloc[row['start_index']:row['end_index'] + 1].groupby(groupby_attr)[
            attribute].mean()[row[groupby_attr]]


def group_min_window(row, df, attribute, groupby_attr):
    return \
        df[[attribute, groupby_attr]].iloc[row['start_index']:row['end_index'] + 1].groupby(groupby_attr)[
            attribute].min()[row[groupby_attr]]


def group_max_window(row, df, attribute, groupby_attr):
    return \
        df[[attribute, groupby_attr]].iloc[row['start_index']:row['end_index'] + 1].groupby(groupby_attr)[
            attribute].max()[row[groupby_attr]]


def group_count_window(row, df, attribute, groupby_attr):
    return df[[attribute, groupby_attr]].iloc[row['start_index']:row['end_index'] + 1].groupby(groupby_attr)[
        attribute].count()[row[groupby_attr]]


def get_start_index(row_id, window_size):
    if row_id > window_size:
        return row_id - window_size
    else:
        return 0


def group_r_sum_window(row, df, attribute, window_size, groupby_attr):
    return df.iloc[get_start_index(row.name, window_size):row.name + 1].groupby(groupby_attr)[attribute].sum()[
        row[groupby_attr]]


def group_r_avg_window(row, df, attribute, window_size, groupby_attr):
    return df.iloc[get_start_index(row.name, window_size):row.name + 1].groupby(groupby_attr)[attribute].mean()[
        row[groupby_attr]]


def group_r_min_window(row, df, attribute, window_size, groupby_attr):
    return df.iloc[get_start_index(row.name, window_size):row.name + 1].groupby(groupby_attr)[attribute].min()[
        row[groupby_attr]]


def group_r_max_window(row, df, attribute, window_size, groupby_attr):
    return df.iloc[get_start_index(row.name, window_size):row.name + 1].groupby(groupby_attr)[attribute].max()[
        row[groupby_attr]]


def group_r_count_window(row, df, attribute, window_size, groupby_attr):
    return df.iloc[get_start_index(row.name, window_size):row.name + 1].groupby(groupby_attr)[attribute].count()[
        row[groupby_attr]]


def r_sum_window(df, windows_size):
    return rolling_sum(df, windows_size)


def r_avg_window(df, windows_size):
    return rolling_mean(df, windows_size)


def r_min_window(df, windows_size):
    return rolling_min(df, windows_size)


def r_max_window(df, windows_size):
    return rolling_max(df, windows_size)


def r_count_window(df, windows_size):
    return rolling_count(df, windows_size)


functions_dict = {0: sum_window, 1: avg_window, 2: min_window, 3: max_window, 4: count_window}

group_functions_dict = {0: group_sum_window, 1: group_avg_window, 2: group_min_window, 3: group_max_window,
                        4: group_count_window}

event_func_dict = {0: r_sum_window, 1: r_avg_window, 2: r_min_window, 3: r_max_window, 4: r_count_window}

group_event_func_dict = {0: group_r_sum_window, 1: group_r_avg_window, 2: group_r_min_window, 3: group_r_max_window,
                         4: group_r_count_window}


def aggregate_time_window(aggregate_function, time_window_value, time_granularity, attribute_name, original_data_frame,
                          current_data_frame, groupby_attr):
    if groupby_attr is None:
        df = original_data_frame.loc[:, ['Date', attribute_name]]
    else:
        df = original_data_frame.loc[:, ['Date', attribute_name, groupby_attr]]

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort(['Date'])
    start_dates = ""
    if time_granularity == 'seconds':
        start_dates = df['Date'] - timedelta(seconds=int(time_window_value))
    elif time_granularity == 'minutes':
        start_dates = df['Date'] - timedelta(minutes=int(time_window_value))
    elif time_granularity == 'days':
        start_dates = df['Date'] - timedelta(days=int(time_window_value))

    df['start_index'] = df['Date'].values.searchsorted(start_dates, side='right')
    df['end_index'] = np.arange(len(df))

    if groupby_attr is None:
        new_row = df.apply(functions_dict[aggregate_function], axis=1, args=(df, attribute_name))
    else:
        new_row = df.apply(group_functions_dict[aggregate_function], axis=1, args=(df, attribute_name, groupby_attr))

    current_data_frame[attribute_name] = new_row
    return current_data_frame


def aggregate_event_window(aggregate_function, attribute_name, event_window_value, original_data_frame,
                           current_data_frame, groupby_attr):
    if groupby_attr is None:
        df = original_data_frame.loc[:, [attribute_name]]
        aggregated_df = event_func_dict[aggregate_function](df, event_window_value)
    else:
        df = original_data_frame.loc[:, [attribute_name, groupby_attr]]
        aggregated_df = df.apply(group_event_func_dict[aggregate_function], axis=1,
                                 args=(df, attribute_name, event_window_value, groupby_attr))

    current_data_frame[attribute_name] = aggregated_df
    return current_data_frame