from graph_vis.graph import *
import networkx as nx

class GraphVisualizer:
    """
    Визуализирует Graph
    """
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
    
    def visualize(self, node_id: int) -> nx.Graph:
        """
        Возвращает networkx.Graph c заданными позициями вершин в окрестности вершины с node_id
        """
        if node_id not in self.graph.nodes:
            raise RuntimeError("Unknown node id")
        nxgraph = nx.Graph()
        nxgraph.add_node(node_id, pos=(0, 0), **self.graph.nodes[node_id].get_info())
        
        count = len(self.graph.nodes[node_id].in_ids)
        y = (count - 1) / 2
        for from_id in self.graph.nodes[node_id].in_ids:
            nxgraph.add_node(from_id, pos=(-count/2, y), **self.graph.nodes[from_id].get_info())
            nxgraph.add_edge(from_id, node_id)
            y -= 1
        
        count = len(self.graph.nodes[node_id].out_ids)
        y = (count - 1) / 2
        for to_id in self.graph.nodes[node_id].out_ids:
            nxgraph.add_node(to_id, pos=(count/2, y), **self.graph.nodes[to_id].get_info())
            nxgraph.add_edge(node_id, to_id)
            y -= 1
    
        return nxgraph
        
