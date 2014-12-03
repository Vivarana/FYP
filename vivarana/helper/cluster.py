import pandas.rpy.common as com

import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

from vivarana.constants import *


def apply_clustering(cluster_method, number_of_clusters, current_data_frame, data_frame):
    pandas2ri.activate()
    r_dataframe = com.convert_to_r_dataframe(data_frame)

    if cluster_method == K_MEANS_CLUSTERING:
        klaR = importr("klaR")
        KMC = klaR.kmodes(r_dataframe, number_of_clusters)
        current_data_frame['clusterID'] = KMC[0]

    elif cluster_method == HIERARCHICAL_CLUSTERING:
        distances = ro.r.dist(r_dataframe,
                              method="euclidean")  # specify the distance todo add dropdownbox to get user input
        cluster_input = ro.r.hclust(distances, method="ward.D")
        cluster_groups = ro.r.cutree(cluster_input, k=number_of_clusters)  # specify the number of clusters
        current_data_frame['clusterID'] = cluster_groups

    elif cluster_method == FUZZY_CLUSTERING:
        cluster = importr("cluster")
        fuzzy_clustered = cluster.fanny(r_dataframe, number_of_clusters)
        current_data_frame['clusterID'] = fuzzy_clustered[3]