"""
File Location: /app/core/relationships/navigation.py

Provides relationship-based navigation (recommendation, path finding) over the knowledge graph.
"""

from typing import List, Set, Union
from .knowledge_graph import KnowledgeGraph, Node, Edge

class RelationshipNavigator:
    """
    Supports finding recommended next concepts/nodes based on relationships.
    Provides navigation and recommendation utilities over the knowledge graph.
    
    NOTE: All public methods consistently accept *either* Node or node id (str) as input,
    and always return Node objects (not ids), unless otherwise documented.
    """

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph
        
    def _get_node(self, node: Union[str, Node]) -> Node:
        """Helper to convert node id or Node to Node object."""
        if isinstance(node, Node):
            return node
        return self.graph.get_node(node)

    def recommend_next(self, current_node: Union[str, Node], max_count: int=3) -> List[Node]:
        """
        Returns up to max_count recommended nodes that are directly connected and ranked by relation/property.
        
        Args:
            current_node: Node object or node id string
            max_count: Max recommendations to return (default: 3)
            
        Returns:
            List of Node objects
        """
        node = self._get_node(current_node)
        neighbors = self.graph.get_neighbors(node.id)
        # Convert to Node objects if needed
        node_objs = [self._get_node(nbr) if isinstance(nbr, str) else nbr for nbr in neighbors]
        # TODO: Enhance ranking logic by edge type, node properties
        return node_objs[:max_count]

    def find_path(self, start: Union[str, Node], end: Union[str, Node], max_depth: int=5) -> List[str]:
        """
        Find a path between two nodes (breadth-first search, up to max_depth).
        
        Args:
            start: Node or node id
            end: Node or node id
            max_depth: Max allowable hops
            
        Returns:
            List of node ids representing the path from start to end.
        """
        from collections import deque
        start_node = self._get_node(start)
        end_node = self._get_node(end)
        visited = set()
        queue = deque([(start_node.id, [start_node.id])])
        while queue:
            node_id, path = queue.popleft()
            if node_id == end_node.id:
                return path
            if len(path) > max_depth:
                continue
            for neighbor in self.graph.get_neighbors(node_id):
                neighbor_id = neighbor.id if isinstance(neighbor, Node) else neighbor
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        return []
    
    def get_related_content(self, concept_node: Union[str, Node]) -> List[Node]:
        """
        Returns content nodes that 'cover' the given concept.
        
        Args:
            concept_node: The concept node or node id to find related content for
            
        Returns:
            List of content nodes that cover this concept
        """
        cnode = self._get_node(concept_node)
        return [
            rel.source if isinstance(rel.source, Node) else self._get_node(rel.source)
            for rel in self.graph.edges
            if (rel.target.id if isinstance(rel.target, Node) else rel.target) == cnode.id 
            and rel.relation == "covers"
        ]
    
    def get_recommendations_for_content(self, content_node: Union[str, Node]) -> List[Node]:
        """
        Recommends other content covering related concepts.
        
        Args:
            content_node: The content node or node id to find recommendations for
            
        Returns:
            List of recommended content nodes
        """
        cnode = self._get_node(content_node)
        # Get concepts covered by this content
        primary_concepts = [
            rel.target if isinstance(rel.target, Node) else self._get_node(rel.target)
            for rel in self.graph.edges
            if (rel.source.id if isinstance(rel.source, Node) else rel.source) == cnode.id 
            and rel.relation == "covers"
        ]
        
        # Find other content that covers these concepts
        recs = set()
        for concept in primary_concepts:
            for rel in self.graph.edges:
                source_id = rel.source.id if isinstance(rel.source, Node) else rel.source
                target_id = rel.target.id if isinstance(rel.target, Node) else rel.target
                if (
                    source_id != cnode.id
                    and rel.relation == "covers"
                    and target_id == concept.id
                ):
                    recs.add(rel.source if isinstance(rel.source, Node) else self._get_node(rel.source))
        return list(recs)
    
    def get_related_concepts(self, node: Union[str, Node], relation_types: List[str] = None) -> List[Node]:
        """
        Returns concepts related to the given node by specified relation types.
        
        Args:
            node: The node or node id to find related concepts for
            relation_types: Optional list of relation types to filter by
            
        Returns:
            List of related concept nodes
        """
        n = self._get_node(node)
        related = []
        for rel in self.graph.edges:
            if relation_types and rel.relation not in relation_types:
                continue
            
            source_id = rel.source.id if isinstance(rel.source, Node) else rel.source
            target_id = rel.target.id if isinstance(rel.target, Node) else rel.target
                
            if source_id == n.id:
                related.append(rel.target if isinstance(rel.target, Node) else self._get_node(rel.target))
            elif target_id == n.id:
                related.append(rel.source if isinstance(rel.source, Node) else self._get_node(rel.source))
                
        return related
