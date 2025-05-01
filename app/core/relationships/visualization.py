"""
File Location: /app/core/relationships/visualization.py

Stub for basic knowledge graph visualization data output.
"""

from .knowledge_graph import KnowledgeGraph

def export_graph_as_json(graph: KnowledgeGraph) -> dict:
    """
    Exports the graph to a dict structure ready for JSON serialization.
    UI/frontend can consume this for visualization.
    """
    return {
        "nodes": [
            {"id": n.id, "label": n.label}
            for n in graph.nodes.values()
        ],
        "edges": [
            {"from": e.source, "to": e.target, "relation": e.relation}
            for e in graph.edges
        ]
    }