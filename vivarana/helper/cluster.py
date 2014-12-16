import pandas.rpy.common as com

import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

from vivarana.constants import *


def apply_clustering(cluster_method, number_of_clusters, current_data_frame, data_frame):
    pandas2ri.activate()
    data_frame.to_csv('media\dataframe.csv')
    r_dataframe = ro.r['read.csv']('media\dataframe.csv')

    if cluster_method == K_MEANS_CLUSTERING:
        klaR = importr("klaR")
        KMC = klaR.kmodes(r_dataframe, number_of_clusters)
        current_data_frame['clusterID'] = KMC[0]

    elif cluster_method == HIERARCHICAL_CLUSTERING:
        cluster = importr("cluster")
        distances = cluster.daisy(r_dataframe, metric="gower")
        cluster_input = ro.r.hclust(distances, method="complete")
        cluster_groups = ro.r.cutree(cluster_input, k=number_of_clusters)  # specify the number of clusters
        current_data_frame['clusterID'] = cluster_groups

    elif cluster_method == FUZZY_CLUSTERING:
        cluster = importr("cluster")
        fuzzy_clustered = cluster.fanny(r_dataframe, number_of_clusters)
        current_data_frame['clusterID'] = fuzzy_clustered[3]