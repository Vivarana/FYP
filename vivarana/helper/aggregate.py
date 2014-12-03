import pandas as pd
import numpy as np
from datetime import timedelta


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


functions_dict = {0: sum_window, 1: avg_window, 2: min_window, 3: max_window, 4: count_window}


def aggregate_window(aggregate_function, time_window_value, time_granularity, attribute_name, current_data_frame):
    # todo prevent further sum
    # todo add method to reset axis
    # todo record this action
    df1 = current_data_frame.copy(deep=True)
    df = df1[['Date', attribute_name]]
    df['Date'] = pd.to_datetime(df['Date'])  # todo date column should be parsed earlier
    start_dates = ""
    if time_granularity == 'seconds':
        start_dates = df['Date'] - timedelta(seconds=int(time_window_value))
    elif time_granularity == 'minutes':
        start_dates = df['Date'] - timedelta(minutes=int(time_window_value))
    elif time_granularity == 'days':
        start_dates = df['Date'] - timedelta(days=int(time_window_value))

    df['start_index'] = df['Date'].values.searchsorted(start_dates, side='right')
    df['end_index'] = np.arange(len(df))

    new_row = df.apply(functions_dict[aggregate_function], axis=1, args=(df, attribute_name))

    df1.pop(attribute_name)
    df1[attribute_name] = new_row
    return df1


