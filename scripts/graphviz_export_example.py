"""
Quick Example: Export AeroLearn AI KnowledgeGraph to Graphviz DOT

Where to save: /scripts/graphviz_export_example.py

Usage:
    python scripts/graphviz_export_example.py

This script will create a mini content/concept graph and export it to DOT format for visualization via Graphviz tools.
"""

from app.core.relationships.knowledge_graph import KnowledgeGraph, Node, Edge

def build_example_graph():
    graph = KnowledgeGraph()
    # Example content and concepts
    graph.add_node(Node("lesson1", "Intro to Quantum Physics"))
    graph.add_node(Node("lesson2", "Thermodynamics Basics"))

    concepts = [
        ("quantum", "Quantum"),
        ("energy", "Energy"),
        ("entropy", "Entropy"),
    ]

    # Add concept nodes and edges
    for cid, label in concepts:
        graph.add_node(Node(cid, label))
    
    # 'lesson1' covers quantum and energy; 'lesson2' covers energy and entropy
    graph.add_edge(Edge("lesson1", "quantum", "covers"))
    graph.add_edge(Edge("lesson1", "energy", "covers"))
    graph.add_edge(Edge("lesson2", "energy", "covers"))
    graph.add_edge(Edge("lesson2", "entropy", "covers"))

    return graph

if __name__ == "__main__":
    graph = build_example_graph()
    dot = graph.to_dot()
    with open("mini_knowledge_graph.dot", "w", encoding="utf-8") as f:
        f.write(dot)
    print("DOT file 'mini_knowledge_graph.dot' written. You can visualize it with Graphviz, e.g.:")
    print("  dot -Tpng mini_knowledge_graph.dot -o mini_knowledge_graph.png")
    print("  (or upload to web Graphviz viewers)")