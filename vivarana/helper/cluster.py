import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

from vivarana.constants import *


def apply_clustering(state_map, current_data_frame, selected_ids):
    columns = state_map[CLUSTER_COLUMNS_LST]
    # only the user selected rows and columns will be used to cluster
    new_data = current_data_frame.ix[selected_ids, columns]

    pandas2ri.activate()
    file_path = "media" + os.path.sep + "dataframe.csv"
    new_data.to_csv(file_path)
    r_dataframe = ro.r['read.csv'](file_path)

    cluster_id = []
    cluster_method = state_map[CLUSTERING_METHOD]
    number_of_clusters = state_map[NUMBER_OF_CLUSTERS]
    if cluster_method == K_MEANS_CLUSTERING:
        klaR = importr("klaR")
        KMC = klaR.kmodes(r_dataframe, number_of_clusters)
        cluster_id = KMC[0]

    elif cluster_method == HIERARCHICAL_CLUSTERING:
        cluster = importr("cluster")
        distances = cluster.daisy(r_dataframe, metric="gower")
        cluster_input = ro.r.hclust(distances, method="complete")
        cluster_groups = ro.r.cutree(cluster_input, k=number_of_clusters)  # specify the number of clusters
        cluster_id = cluster_groups

    elif cluster_method == FUZZY_CLUSTERING:
        cluster = importr("cluster")
        fuzzy_clustered = cluster.fanny(r_dataframe, number_of_clusters)
        cluster_id = fuzzy_clustered[3]

    del r_dataframe
    clustered_dict = {}

    for i in xrange(len(selected_ids)):
        current_data_frame.ix[selected_ids[i], 'clusterID'] = cluster_id[i]
        clustered_dict[selected_ids[i]] = cluster_id[i]
    return clustered_dict