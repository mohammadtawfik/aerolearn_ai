"""
Dependency tracking for the AeroLearn AI component system.

This module provides utilities for tracking, validating, and visualizing
component dependencies and ensuring proper component initialization order.
"""
import logging
from typing import Dict, List, Set, Tuple, Any, Optional
import networkx as nx  # You may need to install this package: pip install networkx
import semver

from .component_registry import ComponentRegistry, Component, ComponentState

logger = logging.getLogger(__name__)


class CircularDependencyError(Exception):
    """Exception raised when a circular dependency is detected."""
    pass


class DependencyTracker:
    """
    Utility for tracking and analyzing dependencies between components.
    
    This class provides methods for validating dependency relationships,
    detecting circular dependencies, and determining optimal initialization
    order for components.
    """
    
    def __init__(self):
        """Initialize the dependency tracker."""
        self._registry = ComponentRegistry()
    
    def validate_dependencies(self, component: Component) -> Dict[str, List[str]]:
        """
        Validate dependencies for a component.
        
        Args:
            component: The component to validate dependencies for
            
        Returns:
            Dictionary of validation issues, grouped by issue type
        """
        return self._registry.check_component_compatibility(component)
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies in the component registry.
        
        Returns:
            List of component ID lists, each representing a cycle
        """
        # Build directed graph of dependencies
        graph = nx.DiGraph()
        
        # Add all components as nodes
        for component_id, component in self._registry._components.items():
            graph.add_node(component_id)
        
        # Add edges for dependencies
        for component_id, component in self._registry._components.items():
            # Add component type dependencies
            for dep_type, dep_info in component.dependencies.items():
                for provider_id, provider in self._registry.get_components_by_type(dep_type).items():
                    try:
                        if semver.match(provider.version, dep_info["version_requirement"]):
                            graph.add_edge(component_id, provider_id)
                    except ValueError:
                        continue
            
            # Add interface dependencies
            for interface_name in component.required_interfaces:
                for provider_id in self._registry.get_interface_providers(interface_name):
                    graph.add_edge(component_id, provider_id)
        
        # Find cycles in the graph
        try:
            cycles = list(nx.simple_cycles(graph))
            return cycles
        except nx.NetworkXNoCycle:
            return []
    
    def get_initialization_order(self) -> List[str]:
        """
        Determine optimal initialization order for components.
        
        Returns:
            List of component IDs in initialization order
        
        Raises:
            CircularDependencyError: If circular dependencies prevent ordering
        """
        # Check for circular dependencies first
        cycles = self.detect_circular_dependencies()
        if cycles:
            cycle_str = ", ".join([" -> ".join(cycle) for cycle in cycles])
            raise CircularDependencyError(f"Circular dependencies detected: {cycle_str}")
        
        # Build directed graph of dependencies
        graph = nx.DiGraph()
        
        # Add all components as nodes
        for component_id, component in self._registry._components.items():
            graph.add_node(component_id)
        
        # Add edges for dependencies (reversed for topological sort)
        for component_id, component in self._registry._components.items():
            # Add component type dependencies
            for dep_type, dep_info in component.dependencies.items():
                for provider_id, provider in self._registry.get_components_by_type(dep_type).items():
                    try:
                        if semver.match(provider.version, dep_info["version_requirement"]):
                            # Add edge from dependency to dependent (reversed for topo sort)
                            graph.add_edge(provider_id, component_id)
                    except ValueError:
                        continue
            
            # Add interface dependencies
            for interface_name in component.required_interfaces:
                for provider_id in self._registry.get_interface_providers(interface_name):
                    # Add edge from dependency to dependent (reversed for topo sort)
                    graph.add_edge(provider_id, component_id)
        
        # Perform topological sort to get initialization order
        try:
            init_order = list(nx.topological_sort(graph))
            return init_order
        except nx.NetworkXUnfeasible:
            # This shouldn't happen since we already checked for cycles
            raise CircularDependencyError("Unexpected circular dependencies detected")
    
    def get_dependency_tree(self, component_id: str) -> Dict[str, Any]:
        """
        Build a tree representation of dependencies for a component.
        
        Args:
            component_id: ID of the component to build tree for
            
        Returns:
            Nested dictionary representing the dependency tree
        """
        component = self._registry.get_component(component_id)
        if not component:
            return {}
        
        tree = {
            "id": component_id,
            "type": component.component_type,
            "version": component.version,
            "state": component.state,
            "dependencies": []
        }
        
        # Add component type dependencies
        visited = set([component_id])  # Track visited components to prevent cycles
        
        self._build_dependency_subtree(component, tree, visited)
        
        return tree
    
    def _build_dependency_subtree(self, component: Component, node: Dict[str, Any], visited: Set[str]) -> None:
        """
        Helper function to recursively build a dependency subtree.
        
        Args:
            component: Component to build subtree for
            node: Tree node to add dependencies to
            visited: Set of already visited component IDs
        """
        # Add component type dependencies
        for dep_type, dep_info in component.dependencies.items():
            dep_node = {
                "type": dep_type,
                "requirement": dep_info["version_requirement"],
                "optional": dep_info["optional"],
                "satisfied": False,
                "providers": []
            }
            
            providers = self._registry.get_components_by_type(dep_type)
            for provider_id, provider in providers.items():
                try:
                    compatible = semver.match(provider.version, dep_info["version_requirement"])
                    provider_node = {
                        "id": provider_id,
                        "version": provider.version,
                        "state": provider.state,
                        "compatible": compatible
                    }
                    
                    dep_node["providers"].append(provider_node)
                    if compatible:
                        dep_node["satisfied"] = True
                        
                        # Recursively add dependencies of this provider
                        if provider_id not in visited:
                            provider_full_node = {
                                "id": provider_id,
                                "type": provider.component_type,
                                "version": provider.version,
                                "state": provider.state,
                                "dependencies": []
                            }
                            visited.add(provider_id)
                            self._build_dependency_subtree(provider, provider_full_node, visited)
                            provider_node["dependencies"] = provider_full_node["dependencies"]
                except ValueError:
                    continue
            
            node["dependencies"].append(dep_node)
        
        # Add interface dependencies
        for interface_name in component.required_interfaces:
            interface_node = {
                "interface": interface_name,
                "satisfied": False,
                "providers": []
            }
            
            providers = self._registry.get_interface_providers(interface_name)
            for provider_id, provider in providers.items():
                provider_node = {
                    "id": provider_id,
                    "version": provider.version,
                    "state": provider.state
                }
                
                interface_node["providers"].append(provider_node)
                interface_node["satisfied"] = True
                
                # Recursively add dependencies of this provider
                if provider_id not in visited:
                    provider_full_node = {
                        "id": provider_id,
                        "type": provider.component_type,
                        "version": provider.version,
                        "state": provider.state,
                        "dependencies": []
                    }
                    visited.add(provider_id)
                    self._build_dependency_subtree(provider, provider_full_node, visited)
                    provider_node["dependencies"] = provider_full_node["dependencies"]
            
            node["dependencies"].append(interface_node)
    
    def generate_dependency_graph(self) -> str:
        """
        Generate a DOT representation of the dependency graph.
        
        Returns:
            DOT format string for visualization with GraphViz
        """
        graph = [
            "digraph Dependencies {",
            "    rankdir=LR;",
            "    node [shape=box, style=filled, fontname=Arial];",
        ]
        
        # Add nodes for components
        for component_id, component in self._registry._components.items():
            # Choose color based on component state
            color = "white"
            if component.state == ComponentState.STARTED:
                color = "lightgreen"
            elif component.state == ComponentState.INITIALIZED:
                color = "lightblue"
            elif component.state == ComponentState.ERROR:
                color = "salmon"
            
            # Escape any quotes in component_id
            escaped_id = component_id.replace('"', '\\"')
            
            graph.append(f'    "{escaped_id}" [label="{escaped_id}\\nType: {component.component_type}\\nVersion: {component.version}\\nState: {component.state}", fillcolor="{color}"];')
        
        # Add edges for dependencies
        for component_id, component in self._registry._components.items():
            # Add component type dependencies
            for dep_type, dep_info in component.dependencies.items():
                providers = self._registry.get_components_by_type(dep_type)
                
                for provider_id, provider in providers.items():
                    try:
                        if semver.match(provider.version, dep_info["version_requirement"]):
                            style = "solid"
                        else:
                            style = "dashed"
                        
                        # Escape any quotes in IDs
                        escaped_component_id = component_id.replace('"', '\\"')
                        escaped_provider_id = provider_id.replace('"', '\\"')
                        
                        graph.append(f'    "{escaped_component_id}" -> "{escaped_provider_id}" [style="{style}", label="requires {dep_type}"];')
                    except ValueError:
                        continue
            
            # Add interface dependencies
            for interface_name in component.required_interfaces:
                providers = self._registry.get_interface_providers(interface_name)
                
                for provider_id in providers:
                    # Escape any quotes in IDs
                    escaped_component_id = component_id.replace('"', '\\"')
                    escaped_provider_id = provider_id.replace('"', '\\"')
                    
                    graph.append(f'    "{escaped_component_id}" -> "{escaped_provider_id}" [style="dotted", label="requires {interface_name}"];')
        
        graph.append("}")
        return "\n".join(graph)
    
    def validate_all_dependencies(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Validate dependencies for all registered components.
        
        Returns:
            Dictionary mapping issue types to lists of issues
        """
        all_issues = {}
        
        for component_id, component in self._registry._components.items():
            issues = self.validate_dependencies(component)
            
            for issue_type, issue_list in issues.items():
                if issue_type not in all_issues:
                    all_issues[issue_type] = []
                
                for issue in issue_list:
                    all_issues[issue_type].append({
                        "component_id": component_id,
                        "issue": issue
                    })
        
        return all_issues
    
    def suggest_missing_components(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze dependencies to suggest missing components.
        
        Returns:
            Dictionary mapping component types to requirement information
        """
        missing_components = {}
        
        for component_id, component in self._registry._components.items():
            issues = self.validate_dependencies(component)
            
            if "missing_dependencies" in issues:
                for issue in issues["missing_dependencies"]:
                    # Extract component type and version requirement from issue
                    # Format: "Missing required dependency: {type} {req}"
                    parts = issue.split(": ")[1].split(" ")
                    dep_type = parts[0]
                    req = " ".join(parts[1:])
                    
                    if dep_type not in missing_components:
                        missing_components[dep_type] = {
                            "required_by": [],
                            "version_requirements": set()
                        }
                    
                    missing_components[dep_type]["required_by"].append(component_id)
                    missing_components[dep_type]["version_requirements"].add(req)
        
        # Convert sets to lists for JSON serialization
        for dep_type in missing_components:
            missing_components[dep_type]["version_requirements"] = list(missing_components[dep_type]["version_requirements"])
        
        return missing_components
