import networkx as nx
import numpy as np
from scipy.spatial import Delaunay
from scipy import spatial


def build_delaunay(E, coord_sys: str = None, layer: str = None):
    """
    Build a graph representation of a tissue using Delaunay triangulation.

    Args:
        E : emobject.core.EMObject
        coord_sys : str, the coordinate system to use for the graph

    """
    dln = Delaunay(E[layer].pos[coord_sys].to_numpy())
    G = nx.Graph()
    # coords = list()

    for i in range(len(E[layer].pos[coord_sys])):
        coord = E[layer].pos[coord_sys].iloc[i, 0], E[layer].pos[coord_sys].iloc[i, 1]
        cell_id = E[layer].pos[coord_sys].index[i]
        G.add_node(i, center_coord=coord, cell_id=cell_id)

    for t in dln.simplices:
        edges = [(t[0], t[1]), (t[1], t[2]), (t[0], t[2])]
        for e in edges:
            G.add_edge(min(e), max(e))
    return G


def build_distance_graph(coord_arr, r=100):
    """
    Build a graph representation of a tissue using a distance threshold.

    Args:
        coord_arr : np array, array of (x,y) cell positions.
        r : the distance threshold

    Returns:
        Constructed NetworkX graph.
    """

    tree = spatial.KDTree(coord_arr)
    neighbors = tree.query_ball_point(coord_arr, r=r)

    # Initialize a graph
    G = nx.Graph()
    # Add nodes
    G.add_nodes_from(np.arange(0, neighbors.shape[0]))

    # Add edges
    for source_cell in range(neighbors.shape[0]):
        edges_to_add = neighbors[source_cell]
        for sink_cell in edges_to_add:
            if source_cell == sink_cell:
                pass  # add self loops in the lin alg steps
            else:
                G.add_edge(source_cell, sink_cell)

    return G


def prune_graph_by_distance(G, r, coord_arr):
    """
    Prunes a graph's edges based on a distance threshold.
    For example, if distance threshold is 100px, and Deluanay triangulation
    yields edges between nodes that exceed distance threshold, they will be
    removed from G. This ensures a planar graph.

    Args:
        G : NetworkX graph
        r : float, distance threshold
        coord_arr : numpy arr, the coordinates of each cell in G, same index.

    Returns:
        Pruned nx.Graph()
    """

    # First calculate what the acceptable edges are given distance threshold
    tree = spatial.KDTree(coord_arr)
    neighbors = tree.query_ball_point(coord_arr, r=r)
    edges_to_remove = list()
    for source_cell in range(0, neighbors.shape[0]):
        for sink_cell in G[source_cell]:
            # traversing the neighbors of source cell in the graph
            # Check if the sink cell is within the distance threshold
            if sink_cell not in neighbors[source_cell]:
                # remove the edge
                edges_to_remove.append((source_cell, sink_cell))

    G.remove_edges_from(edges_to_remove)

    return G


def build_graph(E, mode="delaunay", r=None, threshold=None):
    """
    Build a graph representation of a tissue using a distance threshold.

    Args:
        E : emobject.core.EMObject
        mode : str, 'delaunay' or 'distance'
        r : the distance threshold

    Returns:
        Constructed NetworkX graph.
    """

    if mode == "delaunay":
        G = build_delaunay(E)
    elif mode == "distance":
        G = build_distance_graph(E.pos.to_numpy(), r=r)
    else:
        raise ValueError('mode must be either "delaunay" or "distance"')

    if threshold is not None:
        G = prune_graph_by_distance(G, threshold, E.pos.to_numpy())

    return G
