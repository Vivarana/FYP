import os

import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import rpy2.robjects as robjects
import pandas.rpy.common as com

from vivarana.extensions.log.log_constants import DATE
from vivarana.constants import ANOMALY_DETECT_COLUMN


def detect_anomalies(state_map, current_data_frame, selected_ids):
    columns = [DATE, state_map[ANOMALY_DETECT_COLUMN]]
    new_data = current_data_frame.ix[selected_ids, columns]
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
    #todo add a popup in webpage to get these data
    res = r_f(r_df, 0.1, 0.05, 4000)
    anoms = com.convert_robj(res)

    anom_lst = list(int(x) for x in anoms['index'])
    return anom_lst
