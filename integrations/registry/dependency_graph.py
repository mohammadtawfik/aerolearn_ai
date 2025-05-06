class DependencyGraph:
    """
    Internal dependency management for components with ordered traversal support
    """
    def __init__(self):
        from collections import OrderedDict, deque
        self._nodes = OrderedDict()  # node_id -> ordered list of dependency_ids
        self._deque = deque  # Store deque class for BFS traversals

    def add_node(self, node_id):
        """Add a node to the dependency graph"""
        if node_id not in self._nodes:
            self._nodes[node_id] = []
            
    # Alias for backward compatibility
    add_component = add_node

    def remove_node(self, node_id):
        """Remove a node and all its dependencies from the graph"""
        # Remove the node itself
        self._nodes.pop(node_id, None)
        # Remove as dependency from all other nodes
        for deps in self._nodes.values():
            if node_id in deps:
                deps.remove(node_id)
                
    # Alias for backward compatibility
    remove_component = remove_node

    def add_edge(self, from_node, to_node):
        """
        Add a dependency relationship (from_node depends on to_node)
        Returns True if successful, False if either node doesn't exist
        """
        if from_node not in self._nodes or to_node not in self._nodes:
            return False
        # Maintain insertion order and prevent duplicates
        if to_node not in self._nodes[from_node]:
            self._nodes[from_node].append(to_node)
        return True
        
    # Alias for backward compatibility
    add_dependency = add_edge

    def remove_edge(self, from_node, to_node):
        """Remove a dependency relationship if it exists"""
        if from_node in self._nodes and to_node in self._nodes[from_node]:
            self._nodes[from_node].remove(to_node)
            
    # Alias for backward compatibility
    remove_dependency = remove_edge

    def get_all_edges(self):
        """Get a dictionary representation of the entire dependency graph"""
        return {nid: list(deps) for nid, deps in self._nodes.items()}
        
    # Alias for backward compatibility
    get_dependency_graph = get_all_edges

    def has_node(self, node_id):
        """Check if a node exists in the graph"""
        return node_id in self._nodes
        
    # Alias for backward compatibility
    has_component = has_node
        
    def get_dependencies(self, node_id):
        """
        Return a list of dependencies for the specified node (direct only).
        """
        return list(self._nodes.get(node_id, []))
        
    def get_dependents(self, node_id):
        """
        Return a list of nodes that depend on the specified node.
        """
        dependents = []
        for nid, deps in self._nodes.items():
            if node_id in deps:
                dependents.append(nid)
        return dependents
    
    def has_edge(self, from_node, to_node):
        """Check if a direct dependency relationship exists"""
        return from_node in self._nodes and to_node in self._nodes[from_node]
        
    # Alias for backward compatibility
    has_dependency = has_edge
    
    def analyze_dependency_impact(self, node_id):
        """
        Return all nodes (direct & indirect) that would be impacted
        if the specified node changed, in breadth-first order.
        """
        impacted = []
        visited = set()
        queue = self._deque(self.get_dependents(node_id))
        
        while queue:
            dep = queue.popleft()
            if dep not in visited:
                impacted.append(dep)
                visited.add(dep)
                for parent in self.get_dependents(dep):
                    queue.append(parent)
        
        return impacted
        
    def clear(self):
        """
        Reset all internal state by clearing all dependencies.
        Used for protocol-compliant test reset by registry.
        """
        self._nodes.clear()
        
    def get_nodes(self):
        """Return a list of all nodes in the graph"""
        return list(self._nodes.keys())
