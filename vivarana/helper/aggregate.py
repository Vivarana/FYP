from pandas import rolling_sum, rolling_mean, rolling_max


def sum_of_window(attribute, windows_size, data_frame):
    aggregated_sum = rolling_sum(data_frame, windows_size)
    aggregated_attribute = aggregated_sum.pop(attribute)

    return get_modified_df(aggregated_attribute, attribute, data_frame)


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