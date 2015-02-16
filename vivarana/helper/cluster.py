import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

from vivarana.constants import *


def apply_clustering(state_map, current_data_frame, selected_ids):
    columns = state_map[CLUSTER_COLUMNS_LST]
    # only the user selected rows and columns will be used to cluster
    new_data = current_data_frame.ix[selected_ids, columns]

    pandas2ri.activate() #converts pandas data frames to R data frames on the fly
    #Datafile should be read as a r dataframe or else Factor variable type won't recognized by R
    file_path = "media" + os.path.sep + "dataframe.csv" #Specifying the file Path to media/dataframe.csv
    new_data.to_csv(file_path, index=False) #writing the data frame to the file_path
    r_dataframe = ro.r['read.csv'](file_path) #reading it through rpy2

    cluster_id = []
    cluster_method = state_map[CLUSTERING_METHOD]
    number_of_clusters = state_map[NUMBER_OF_CLUSTERS]
    if cluster_method == K_MEANS_CLUSTERING: #Performs K modes clustering
        klaR = importr("klaR")
        KMC = klaR.kmodes(r_dataframe, number_of_clusters)
        cluster_id = KMC[0] #cluster ID contains on the 1st column of the data frame - referring to that

    elif cluster_method == HIERARCHICAL_CLUSTERING: #performs hierarchical clustering
        cluster = importr("cluster")
        distances = cluster.daisy(r_dataframe, metric="gower") #specifying the distance metrice as gower to calculate distance matrice to non-numeric values
        cluster_input = ro.r.hclust(distances, method="complete")
        cluster_groups = ro.r.cutree(cluster_input, k=number_of_clusters)  # specify the number of clusters
        cluster_id = cluster_groups

    elif cluster_method == FUZZY_CLUSTERING: #performs fuzzy c means clustering
        cluster = importr("cluster")
        fuzzy_clustered = cluster.fanny(r_dataframe, number_of_clusters)
        cluster_id = fuzzy_clustered[3] #cluster ID contains on the 3rd column of the data frame - referring to that

    del r_dataframe
    clustered_dict = {}

    for i in xrange(len(selected_ids)):
        current_data_frame.ix[selected_ids[i], 'clusterID'] = cluster_id[i]
        clustered_dict[selected_ids[i]] = cluster_id[i]
    return clustered_dict