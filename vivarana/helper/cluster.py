import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

from vivarana.constants import *


def apply_clustering(cluster_method, number_of_clusters, original_data_frame, selected_ids, columns):
    columns = [x.encode('UTF8') for x in columns]
    # only the user selected rows and columns will be used to cluster
    new_data = original_data_frame.ix[selected_ids, columns]

    pandas2ri.activate()
    file_path = "media" + os.path.sep + "dataframe.csv"
    new_data.to_csv(file_path)
    r_dataframe = ro.r['read.csv'](file_path)

    cluster_id = []
    if cluster_method == K_MEANS_CLUSTERING:
        klaR = importr("klaR")
        KMC = klaR.kmodes(r_dataframe, number_of_clusters)
        cluster_id = KMC[0]
        del r_dataframe

    elif cluster_method == HIERARCHICAL_CLUSTERING:
        cluster = importr("cluster")
        distances = cluster.daisy(r_dataframe, metric="gower")
        cluster_input = ro.r.hclust(distances, method="complete")
        cluster_groups = ro.r.cutree(cluster_input, k=number_of_clusters)  # specify the number of clusters
        cluster_id = cluster_groups
        del r_dataframe

    elif cluster_method == FUZZY_CLUSTERING:
        cluster = importr("cluster")
        fuzzy_clustered = cluster.fanny(r_dataframe, number_of_clusters)
        cluster_id = fuzzy_clustered[3]

    clustered_list = {}

    for i in xrange(len(selected_ids)):
        clustered_list[selected_ids[i]] = cluster_id[i]
    return clustered_list