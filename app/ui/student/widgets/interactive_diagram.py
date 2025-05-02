"""
File location: /app/ui/student/widgets/interactive_diagram.py

Purpose:
    Provides an extensible interactive diagram widget for student engagement in AeroLearn AI content.
    Supports clickable/selectable elements (nodes), annotations, and provides hooks for integration with lessons or quizzes.

Context:
    Fulfills the Interactive Diagrams Framework aspect of Task 3.2.3, per day16_plan.md.

Usage:
    To be embedded in student content viewers or quizzes for diagram-based interaction.

Author:
    AeroLearn AI Development
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsTextItem, QInputDialog, QGraphicsItem
)
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import QRectF, Qt, pyqtSignal


class DiagramNode(QGraphicsEllipseItem):
    """
    Represents a diagram node (circle) that can be clicked, selected, and annotated.
    """
    def __init__(self, x, y, r, label, parent=None):
        super().__init__(-r, -r, 2*r, 2*r, parent)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#82b1ff")))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.default_color = QColor("#82b1ff")
        self.selected_color = QColor("#ffab40")
        self.text = QGraphicsTextItem(label, self)
        self.text.setPos(-r/2, -r/2)
        self.annotation = ""

    def mousePressEvent(self, event):
        selected = self.isSelected()
        self.setSelected(not selected)
        self.setBrush(QBrush(self.selected_color if not selected else self.default_color))
        super().mousePressEvent(event)


class InteractiveDiagramWidget(QWidget):
    annotation_added = pyqtSignal(dict)
    node_selected = pyqtSignal(str)

    def __init__(self, diagram_spec=None, parent=None):
        """
        :param diagram_spec: dict describing nodes/edges
            Example:
            {
                'nodes': [
                    {'id': 'A', 'x': 100, 'y': 100, 'r': 30, 'label': 'A'},
                    {'id': 'B', 'x': 250, 'y': 100, 'r': 30, 'label': 'B'},
                    {'id': 'C', 'x': 175, 'y': 200, 'r': 30, 'label': 'C'},
                ],
                'edges': [
                    ('A', 'B'),
                    ('A', 'C'),
                    ('B', 'C')
                ]
            }
        """
        super().__init__(parent)
        self.diagram_spec = diagram_spec or {'nodes': [], 'edges': []}
        self.node_map = {}
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)

        self.annotate_btn = QPushButton("Annotate Selected Node")
        self.annotate_btn.clicked.connect(self.annotate_selected_node)
        self.layout.addWidget(self.annotate_btn)

        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        self.populate_diagram()

    def populate_diagram(self):
        # Draw nodes
        for node in self.diagram_spec['nodes']:
            dn = DiagramNode(node['x'], node['y'], node['r'], node['label'])
            dn.setToolTip(node.get('tooltip', ""))
            dn.setZValue(1)
            self.scene.addItem(dn)
            self.node_map[node['id']] = dn
        # Draw edges (straight lines)
        for edge in self.diagram_spec['edges']:
            n1, n2 = self.node_map[edge[0]], self.node_map[edge[1]]
            line = self.scene.addLine(
                n1.x(), n1.y(), n2.x(), n2.y(),
                QPen(Qt.GlobalColor.darkGray, 2)
            )
            line.setZValue(0)
        # Connect signals for selection
        for node in self.node_map.values():
            node.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
            node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def annotate_selected_node(self):
        selected_nodes = [n for n in self.node_map.values() if n.isSelected()]
        if not selected_nodes:
            self.status_label.setText("No node selected.")
            return
        for node in selected_nodes:
            annotation, ok = QInputDialog.getText(self, "Annotate Node", f"Add annotation for node '{node.text.toPlainText()}':")
            if ok and annotation.strip():
                node.annotation = annotation
                node.setToolTip(annotation)
                self.annotation_added.emit({'label': node.text.toPlainText(), 'annotation': annotation})
                self.status_label.setText(f"Annotation added for node '{node.text.toPlainText()}'.")
            else:
                self.status_label.setText("Annotation canceled.")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        for nid, node in self.node_map.items():
            if node.isSelected():
                self.node_selected.emit(nid)