from typing import List, Dict, Optional, Set, Tuple

class Node:
    """
    Вершина ориентированного графа
    """
    def __init__(self, id: int, in_ids: List[int] = None, out_ids: List[int] = None) -> None:
        self.id = id
        self.in_ids = ([] if in_ids is None else in_ids)
        self.out_ids = ([] if out_ids is None else out_ids) 
    
    def get_info(self) -> Dict[str, str]:
        return {"id": self.id}

class Graph:
    """
    Ориентированный граф
    """
    def __init__(self, nodes: Dict[int, Node] = dict()) -> None:
        self.nodes = nodes
    
    def add_node(self, node: Node) -> None:
        """
        Добавляет вершину в ориентированный граф
        """
        if node.id in self.nodes:
            raise RuntimeError("Node with the same id found in the graph")
        self.nodes[node.id] = node

    def add_edge(self, node_from_id: int, node_to_id: int) -> None:
        """
        Добавляет ориентированное ребро между вершинами
        """
        if node_from_id not in self.nodes:
            raise RuntimeError("Source node is not found")
        if node_to_id not in self.nodes:
            raise RuntimeError("Reciever node is not found")
        self.nodes[node_from_id].out_ids.append(node_to_id)
        self.nodes[node_to_id].in_ids.append(node_from_id) 
