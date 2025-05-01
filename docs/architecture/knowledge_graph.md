# AeroLearn AI Knowledge Graph Architecture

## Overview

The AeroLearn AI knowledge graph serves as the semantic backbone of the platform, enabling advanced relationship mapping, navigation, and inference across all educational content. This interconnected structure powers content discovery, personalized learning paths, and intelligent recommendations throughout the platform.

## Core Components

### Node Types

- **Content Nodes:** Represent educational materials such as lessons, modules, quizzes, and assessments. Each content node has a unique ID derived from the underlying content object.
- **Concept Nodes:** Represent domain-specific concepts, terms, skills, or scientific phenomena that are extracted from content (e.g., "quantum mechanics", "kinetic energy", "wave function").
- **Composite Nodes:** Represent aggregated knowledge areas or skill clusters that encompass multiple related concepts.

_All nodes are instances of the `Node` class defined in `/app/core/relationships/knowledge_graph.py`._

### Edge/Relationship Types

- **covers:** Indicates that content thoroughly explains or teaches a concept (e.g., "Lesson 1 covers kinetic energy").
- **mentions:** Indicates that content references a concept without deep coverage (lighter association than "covers").
- **related:** Connects two concepts that are semantically or thematically linked but not in a hierarchical relationship.
- **prerequisite:** Indicates that understanding one concept is necessary before learning another.

_Edges are instances of the `Edge` class, which tracks `source`, `target`, `relation`, and optional metadata._

## Implementation Architecture

### Core Classes

- **`KnowledgeGraph`** (`/app/core/relationships/knowledge_graph.py`)
  - Central data structure that stores all nodes and edges
  - Maintains a dictionary of node IDs and a list of edges
  - Provides methods for:
    - Adding/removing nodes and relationships
    - Querying neighbors and relationships
    - Traversing the graph
    - Exporting to DOT format or NetworkX for visualization and analysis

- **`Node`** (`/app/core/relationships/knowledge_graph.py`)
  - Represents a vertex in the graph
  - Contains ID, type (content/concept/composite), and metadata

- **`Edge`** (`/app/core/relationships/knowledge_graph.py`)
  - Represents a directed relationship between nodes
  - Contains source, target, relationship type, and optional weight/metadata

- **`ConceptRelationship`** (`/app/core/relationships/relationship_extractor.py`)
  - Represents a specific relationship between content and concepts
  - Used during the extraction and graph construction process

### Construction Process

1. **Concept Extraction:**
   - Concepts are extracted from content using NLP techniques
   - See `/app/core/ai/concept_extraction.py` for implementation details

2. **Relationship Mapping:**
   - Extracted concepts are linked to their source content
   - Initial relationships are typically of type "covers"
   - Additional relationship types can be inferred through analysis

3. **Graph Building:**
   - Nodes and edges are created and added to the KnowledgeGraph instance
   - The graph is incrementally built as content is processed

## API Usage Examples

```python
from app.core.relationships.knowledge_graph import KnowledgeGraph
from app.core.relationships.relationship_extractor import ConceptRelationship

# Initialize the knowledge graph
kg = KnowledgeGraph()

# Add content-concept relationships
lesson = ... # Content object
concepts = [...] # List of extracted concepts
for concept in concepts:
    kg.add_relationship(ConceptRelationship(lesson, concept, "covers"))

# Query the graph
related_concepts = kg.get_related(lesson)
prerequisites = kg.get_relationships(concept, relation_type="prerequisite")

# Export for visualization
dot_representation = kg.to_dot()
networkx_graph = kg.to_networkx()
```

## Advanced Relationships and Extensions

### Current Implementation

- The current system primarily extracts and models "covers" relationships between content and concepts.

### Extension Workflow

1. **Adding New Relationship Types:**
   - Update the relationship extraction logic in `/app/core/relationships/relationship_extractor.py`
   - Modify the graph construction code to handle the new relationship type
   - Update any visualization or query code to recognize the new relationship

2. **Implementing Advanced Relationship Detection:**
   - Enhance the NLP pipeline to detect prerequisite relationships between concepts
   - Add machine learning models to infer related concepts based on semantic similarity
   - Implement algorithms to detect concept hierarchies and dependencies

3. **Extending Navigation and Recommendations:**
   - Create or extend the `RelationshipNavigator` class for specialized graph traversal
   - Implement recommendation algorithms that leverage the graph structure
   - Add path-finding algorithms for generating learning paths

## Visualization and Analysis

The knowledge graph supports multiple export formats:

- **DOT Format:** For visualization with Graphviz
- **NetworkX:** For advanced network analysis and algorithm application
- **JSON:** For API responses and frontend visualization

Example visualization workflow:
```python
# Generate DOT representation
dot_output = kg.to_dot()

# Write to file for Graphviz processing
with open("knowledge_graph.dot", "w") as f:
    f.write(dot_output)

# Or use NetworkX for analysis
import networkx as nx
import matplotlib.pyplot as plt

G = kg.to_networkx()
centrality = nx.betweenness_centrality(G)
nx.draw(G, with_labels=True, node_color='lightblue', 
        node_size=[v * 10000 for v in centrality.values()])
plt.savefig("knowledge_graph.png")
```

## File Organization

- `/app/core/relationships/knowledge_graph.py` - Core graph implementation
- `/app/core/relationships/relationship_extractor.py` - Relationship extraction logic
- `/app/core/ai/concept_extraction.py` - Concept extraction from content
- `/tests/core/relationships/` - Tests for graph functionality
- `/scripts/graphviz_export_example.py` - Example visualization script
