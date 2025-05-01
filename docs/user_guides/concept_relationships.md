# AeroLearn AI User Guide: Concept Relationship Mapping

This guide explains how to extract concepts from educational content, build relationship graphs, and use the navigation features for recommendations.

## 1. Extracting Concepts and Relationships

The system automatically analyzes content to identify key domain concepts:

```python
from app.core.ai.concept_extraction import DomainConceptExtractor

# Initialize with domain-specific terms
extractor = DomainConceptExtractor(domain_terms=["force", "gravity", "energy"])

# Extract concepts from lesson content
lesson_text = "This lesson covers gravitational force and potential energy."
concepts = extractor.extract(lesson_text)
# Returns: [Concept('gravity'), Concept('force'), Concept('energy')]
```

## 2. Building the Knowledge Graph

Concepts and content are organized in a knowledge graph:

```python
from app.core.relationships.knowledge_graph import KnowledgeGraph, Node, Edge

# Create a new graph
graph = KnowledgeGraph()

# Add a lesson node
graph.add_node(Node("lesson1", "Introduction to Forces"))

# Add concept nodes and relationships
for concept in concepts:
    concept_id = concept.name.lower()
    graph.add_node(Node(concept_id, concept.name))
    
    # Create "covers" relationship between lesson and concept
    graph.add_edge(Edge("lesson1", concept_id, "covers"))
```

## 3. Visualizing the Knowledge Graph

Generate visual representations of your knowledge graph:

```python
# Export to DOT format for Graphviz
dot_representation = graph.to_dot()

# Save to file
with open("knowledge_graph.dot", "w") as f:
    f.write(dot_representation)

# Render with Graphviz (requires graphviz installation)
# $ dot -Tpng knowledge_graph.dot -o knowledge_graph.png
```

## 4. Navigating & Getting Recommendations

Use the navigator to explore relationships and get recommendations:

```python
from app.core.relationships.navigation import RelationshipNavigator

navigator = RelationshipNavigator(graph)

# Find all concepts covered in a lesson
related_concepts = navigator.get_related_concepts("lesson1")

# Find other content covering similar concepts
recommendations = navigator.get_recommendations_for_content("lesson1")
```

## 5. Relationship Types

The system currently supports these relationship types:

- **covers**: Content → Concept (primary relationship)
- **related**: Concept → Concept (concepts that are related)
- **prerequisite**: Concept → Concept (concepts that should be learned first)

## Example Workflow

1. Instructor uploads new lesson on "Newton's Laws of Motion"
2. System extracts: `"Force"`, `"Motion"`, `"Acceleration"`
3. These concepts are linked to the lesson with "covers" relationships
4. System identifies that `"Force"` and `"Acceleration"` are related
5. When students view this lesson, they can see:
   - Related concepts
   - Other lessons covering the same concepts
   - Prerequisite concepts they should understand first

## Troubleshooting

- **Missing concepts?** Check if your terms are in the domain_terms list
- **Incorrect relationships?** Review the extraction logic and edge creation
- **Visualization issues?** Ensure Graphviz is properly installed

---

For technical implementation details, see: `/docs/architecture/knowledge_graph.md`
