"""
File Location: /app/core/relationships/knowledge_graph.py

Defines KnowledgeGraph, Node, and Edge, used throughout the relationships subsystem.
"""

from typing import List, Dict, Set, Any, Optional, Union, Tuple

class Node:
    """
    Represents a concept or content item in the knowledge graph.
    """
    def __init__(self, identifier: str, label: str, data: Any=None):
        self.id = identifier
        self.label = label
        self.data = data

    def __repr__(self):
        return f"Node(id={self.id!r}, label={self.label!r})"

class Edge:
    """
    Represents a relationship between two nodes.
    """
    def __init__(self, source: str, target: str, relation: str, metadata: Dict[str, Any]=None):
        self.source = source  # Node ID
        self.target = target  # Node ID
        self.relation = relation  # e.g., "prerequisite", "mentions", "related"
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Edge({self.source!r} -> {self.target!r} : {self.relation!r})"

class KnowledgeGraph:
    """
    Simple in-memory representation of a knowledge graph.
    Nodes = concepts/content items; Edges = relationships.
    Supports visualization and navigation of relationships.
    
    -- API NOTE --
    Use add_relationship() as the canonical way to add relationships.
    add_edge() is also provided for generality and legacy support.
    
    `get_neighbors`, `get_related`, and similar will return node IDs (strings) by default,
    matching test expectations and typical graph API usage.
    Pass return_objects=True to get Node instances instead.
    """
    def __init__(self):
        self.nodes: Dict[str, Node] = {}  # id -> Node
        self.edges: List[Edge] = []

    def add_node(self, node: Union[Node, str, Any], label: str = None, data: Any = None):
        """
        Add a node to the graph. Can accept:
        - A Node object
        - A string ID (with optional label and data)
        - Any object (will be stored as data with its str representation as ID)
        """
        if isinstance(node, Node):
            node_id = node.id
            if node_id not in self.nodes:
                self.nodes[node_id] = node
        elif isinstance(node, str):
            node_id = node
            if node_id not in self.nodes:
                node_label = label or node_id
                self.nodes[node_id] = Node(node_id, node_label, data)
        else:
            # Object case - use str representation as ID
            node_id = str(node)
            if node_id not in self.nodes:
                node_label = label or node_id
                self.nodes[node_id] = Node(node_id, node_label, node)

    def add_edge(self, edge: Union[Edge, Tuple[str, str, str], Tuple[Any, Any, str]]):
        """
        Add an edge to the graph. Can accept:
        - An Edge object
        - A tuple of (source_id, target_id, relation)
        - A tuple of (source_obj, target_obj, relation)
        Ensures both source and target nodes exist.
        """
        if isinstance(edge, Edge):
            source_id = edge.source
            target_id = edge.target
            # Auto-add nodes if missing
            self.add_node(source_id)
            self.add_node(target_id)
            self.edges.append(edge)
        else:
            source, target, relation = edge
            
            # Convert objects to IDs if needed
            source_id = source if isinstance(source, str) else str(source)
            target_id = target if isinstance(target, str) else str(target)
            
            # Ensure nodes exist
            self.add_node(source)
            self.add_node(target)
                
            self.edges.append(Edge(source_id, target_id, relation))
    
    def add_relationship(self, relationship):
        """
        Canonical API: Add a ConceptRelationship, Edge, or equivalent tuple.

        This harmonizes with the rest of the platform (and test suite).
        Ensures both nodes are present.
        """
        # Accepts Edge or any object with .source, .target, .relation, or a tuple.
        # If a ConceptRelationship is passed, convert it to Edge.
        if hasattr(relationship, "source") and hasattr(relationship, "target") and hasattr(relationship, "rel_type"):
            # Convert ConceptRelationship to Edge
            source_id = str(getattr(relationship, "source"))
            target_id = str(getattr(relationship, "target"))
            relation = getattr(relationship, "rel_type")
            metadata = getattr(relationship, "metadata", None)
            # Auto-add nodes if missing
            self.add_node(source_id)
            self.add_node(target_id)
            self.add_edge(Edge(source_id, target_id, relation, metadata))
        elif isinstance(relationship, Edge):
            self.add_edge(relationship)
        elif isinstance(relationship, tuple) and len(relationship) == 3:
            self.add_edge(relationship)
        else:
            raise TypeError("Unsupported relationship type for add_relationship")
    
    def find_node(self, label: str) -> Optional[Node]:
        for node in self.nodes.values():
            if node.label == label:
                return node
        return None
        
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Retrieve the Node object for the given node_id, or None if not found.

        This method is used throughout the relationships subsystem and by
        RelationshipNavigator to obtain node objects given their string ID.
        """
        return self.nodes.get(node_id, None)

    def get_neighbors(self, node_id: str, return_objects: bool = False) -> List[Union[str, Node]]:
        """
        Get all nodes that are direct neighbors (outgoing targets) of node_id.
        By default, returns IDs (strings); set return_objects=True for Node instances.
        """
        if return_objects:
            return [self.nodes[e.target] for e in self.edges if e.source == node_id and e.target in self.nodes]
        else:
            return [e.target for e in self.edges if e.source == node_id and e.target in self.nodes]
    
    def get_related(self, node_id: str, relation_type: str = None, return_objects: bool = False) -> List[Union[str, Node]]:
        """
        Get all nodes related to the given node, optionally filtered by relation type.
        Returns node IDs by default, or Node objects if return_objects is True.
        """
        if relation_type:
            filtered = [e.target for e in self.edges 
                   if e.source == node_id and e.relation == relation_type and e.target in self.nodes]
        else:
            filtered = self.get_neighbors(node_id, return_objects=False)
        
        if return_objects:
            return [self.nodes[nid] for nid in filtered]
        else:
            return filtered
    
    def get_incoming(self, node_id: str, relation_type: str = None, return_objects: bool = False) -> List[Union[str, Node]]:
        """
        Get all nodes that point to the given node, optionally filtered by relation type.
        Returns node IDs by default, or Node objects if return_objects is True.
        """
        if relation_type:
            filtered = [e.source for e in self.edges 
                   if e.target == node_id and e.relation == relation_type and e.source in self.nodes]
        else:
            filtered = [e.source for e in self.edges 
                   if e.target == node_id and e.source in self.nodes]
        
        if return_objects:
            return [self.nodes[nid] for nid in filtered]
        else:
            return filtered
    
    def to_dot(self) -> str:
        """
        Export the graph in DOT format for visualization with Graphviz.
        """
        lines = ["digraph KnowledgeGraph {"]
        
        # Add nodes with labels
        for node_id, node in self.nodes.items():
            safe_id = node_id.replace('"', '\\"')
            safe_label = node.label.replace('"', '\\"')
            lines.append(f'    "{safe_id}" [label="{safe_label}"];')
        
        # Add edges with relation types as labels
        for edge in self.edges:
            src = edge.source.replace('"', '\\"')
            tgt = edge.target.replace('"', '\\"')
            rel = edge.relation.replace('"', '\\"')
            lines.append(f'    "{src}" -> "{tgt}" [label="{rel}"];')
        
        lines.append("}")
        return "\n".join(lines)
    
    def to_networkx(self):
        """
        Export the graph as a NetworkX graph for advanced analysis.
        Requires NetworkX to be installed.
        """
        try:
            import networkx as nx
            G = nx.DiGraph()
            
            # Add nodes with attributes
            for node_id, node in self.nodes.items():
                G.add_node(node_id, label=node.label, data=node.data)
            
            # Add edges with attributes
            for edge in self.edges:
                G.add_edge(edge.source, edge.target, 
                          relation=edge.relation, **edge.metadata)
            
            return G
        except ImportError:
            raise ImportError("NetworkX is required for this feature. Install with 'pip install networkx'")

    def __repr__(self):
        return f"KnowledgeGraph(nodes={len(self.nodes)}, edges={len(self.edges)})"
