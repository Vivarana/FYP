import os
from datetime import timedelta
import numpy as np

import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import rpy2.robjects as robjects
import pandas.rpy.common as com

from vivarana.extensions.log.log_constants import DATE
from vivarana.constants import ANOMALY_DETECT_COLUMN, ANOMALY_DETECT_MAX_SIZE, ANOMALY_DETECT_PERIOD_SIZE, \
    ANOMALY_DETECT_GRANULARITY


def detect_anomalies(state_map, current_data_frame, selected_ids):
    columns = [DATE, state_map[ANOMALY_DETECT_COLUMN]]
    new_data = current_data_frame.ix[selected_ids, columns]

    time_granularity = state_map[ANOMALY_DETECT_GRANULARITY]
    time_period = int(state_map[ANOMALY_DETECT_PERIOD_SIZE])

    if time_granularity != 'event':
        start_dates = ""
        if time_granularity == 'seconds':
            start_dates = new_data['Date'] - timedelta(seconds=int(time_period))
        elif time_granularity == 'minutes':
            start_dates = new_data['Date'] - timedelta(minutes=int(time_period))
        elif time_granularity == 'days':
            start_dates = new_data['Date'] - timedelta(days=int(time_period))

        new_data['start_index'] = new_data['Date'].values.searchsorted(start_dates, side='right')
        new_data['end_index'] = np.arange(len(new_data))

        new_data['diff'] = new_data['end_index'] - new_data['start_index']
        time_period = int(new_data['diff'].mean())

        del new_data['start_index'], new_data['end_index'], new_data['diff']

    file_path = "media" + os.path.sep + "anomaly.csv"
    new_data.to_csv(file_path, index=False)

    pandas2ri.activate()
    r_df = ro.r['read.csv'](file_path)
    robjects.r('''
        library(AnomalyDetection)
        f<- function(df, maxanom,alp,prd){
            res <- AnomalyDetectionVec(df[,2], max_anoms=maxanom,alpha=alp, period=prd, direction='both', only_last=FALSE)
            res$anoms
        }
        ''')
    r_f = robjects.r['f']
    res = r_f(r_df, float(state_map[ANOMALY_DETECT_MAX_SIZE]), 0.05, time_period)
    anoms = com.convert_robj(res)

    anom_lst = list(int(x) for x in anoms['index'])
    return anom_lst
