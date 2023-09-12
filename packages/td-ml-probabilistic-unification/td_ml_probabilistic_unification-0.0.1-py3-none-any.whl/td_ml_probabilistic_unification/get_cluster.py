import networkx as nx
from scipy.cluster import hierarchy
import scipy.spatial.distance as ssd
import pandas as pd
import numpy as np
from fancyimpute import SoftImpute


def fill_missing_links(matrix, convergence_threshold=0.01):
    """
    Fill missing values in adjacency matrix using SoftImpute. Missing values are considered to be zero,
    as this is the default of the `nx.to_numpy_matrix` function when there is no edge between two nodes.
    Args:
        matrix: adjacency matrix
        convergence_threshold: convergence threshold for SoftImpute algorithm
    Returns:
        Numpy adjacency matrix with imputed missing values
    """
    matrix_ = matrix.copy()
    np.fill_diagonal(matrix_, 1)
    matrix_[matrix_ == 0] = np.nan
    if not np.isnan(matrix_).any():
        return matrix

    imputer = SoftImpute(min_value=0, max_value=1, verbose=False, convergence_threshold=convergence_threshold,
                         init_fill_method='mean')  # init_fill_method='mean' significantly improves speed
    matrix_ = imputer.fit_transform(matrix_)
    # the adjacency matrix needs to have zeros on the diagonal
    np.fill_diagonal(matrix_, 0)

    # force symmetry
    matrix_ = np.tril(matrix_) + np.triu(matrix_.T, 1)
    return matrix_


def clusters(data,ROW_ID,DEDUPLICATION_ID_NAME,cluster_threshold,convergence_threshold,col_names,fill_missing):
    graph = nx.Graph()
    for j, row in data.iterrows():
        graph.add_node(row[f'{ROW_ID}_1'], **{col: row[f'{col}_1'] for col in col_names})
        graph.add_node(row[f'{ROW_ID}_2'], **{col: row[f'{col}_2'] for col in col_names})
        graph.add_edge(row[f'{ROW_ID}_1'], row[f'{ROW_ID}_2'], score=row['score'])

    components = nx.connected_components(graph)

    clustering = {}
    cluster_counter = 0
    for component in components:
        subgraph = graph.subgraph(component)
        if len(subgraph.nodes) > 1:
            adjacency = nx.to_numpy_array(subgraph, weight='score')
            if fill_missing:
                adjacency = fill_missing_links(adjacency,convergence_threshold)
            distances = (np.ones_like(adjacency) - np.eye(len(adjacency))) - adjacency
            
            condensed_distance = ssd.squareform(distances)
            linkage = hierarchy.linkage(condensed_distance, method='centroid')
            clusters = hierarchy.fcluster(linkage, t=1 - cluster_threshold, criterion='distance')
            
        else:
            clusters = np.array([1])
        clustering.update(dict(zip(subgraph.nodes(), clusters + cluster_counter)))
        cluster_counter += len(component)
    df_clusters = pd.DataFrame.from_dict(clustering, orient='index', columns=[DEDUPLICATION_ID_NAME])
    
    df_clusters.sort_values(DEDUPLICATION_ID_NAME, inplace=True)
    #df_clusters[DEDUPLICATION_ID_NAME]=str(range_index) + '_' + df_clusters[DEDUPLICATION_ID_NAME].astype('str')

    df_clusters[ROW_ID]= df_clusters.index
    #df_clusters['block_key']=block_id
    #df_clusters[DEDUPLICATION_ID_NAME]=str(block_id) + '_'+  df_clusters[DEDUPLICATION_ID_NAME].astype('str') 
    return df_clusters