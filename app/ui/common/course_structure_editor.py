# /app/ui/common/course_structure_editor.py

"""
CourseStructureEditor: UI component for hierarchical editing and sequencing
of courses, modules, lessons, supporting drag-and-drop, order changes,
and prerequisite assignment.

Intended for PyQt5/PySide2, but UI toolkit can be swapped.
"""

from PyQt6.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, QMimeData, QByteArray

from app.ui.common.category_multiselect import CategoryMultiSelect
from app.ui.common.tag_autocomplete import TagAutocomplete

class CourseStructureEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Course Structure Editor")
        self.layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Title", "Type", "Order"])
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.viewport().setAcceptDrops(True)
        self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.layout.addWidget(QLabel("Drag and drop modules/lessons to reorder or nest:"))
        self.layout.addWidget(self.tree)
        
        # Category & Tag editor integration UI
        self.editor_tools = QHBoxLayout()
        self.category_selector = CategoryMultiSelect(categories=[], selected_ids=[])
        self.tag_editor = TagAutocomplete(all_tags=[], selected_tags=[])
        self.editor_tools.addWidget(QLabel("Categories:"))
        self.editor_tools.addWidget(self.category_selector)
        self.editor_tools.addSpacing(12)
        self.editor_tools.addWidget(QLabel("Tags:"))
        self.editor_tools.addWidget(self.tag_editor)
        self.layout.addLayout(self.editor_tools)
        
        self.prereq_button = QPushButton("Edit Prerequisites")
        self.prereq_button.clicked.connect(self.show_prerequisites_dialog)
        
        self.save_button = QPushButton("Save Structure")
        self.save_button.clicked.connect(self.save_structure)
        
        self.layout.addWidget(self.prereq_button)
        self.layout.addWidget(self.save_button)
        
        # Internal: course_data holds the tree source (dict)
        self.course_data = {}
        self.tree.itemChanged.connect(self.on_item_changed)
        # Enable drag-drop reordering
        self.tree.dropEvent = self.on_drop_event

    def load_course_structure(self, course_data):
        """
        Loads the hierarchical structure from provided course data.
        course_data: dict matching Course > Module > Lesson hierarchy.
        """
        self.course_data = course_data
        self.tree.clear()
        for module in course_data.get('modules', []):
            m_item = QTreeWidgetItem([module['title'], "Module", str(module['order'])])
            m_item.setFlags(m_item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled)
            for lesson in module.get('lessons', []):
                l_item = QTreeWidgetItem([lesson['title'], "Lesson", str(lesson['order'])])
                l_item.setFlags(l_item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled)
                m_item.addChild(l_item)
            self.tree.addTopLevelItem(m_item)
        self.tree.expandAll()

    def on_drop_event(self, event):
        """Handles drag-drop within the tree to update in-memory order."""
        super(QTreeWidget, self.tree).dropEvent(event)
        self.recalculate_orders()
    
    def recalculate_orders(self):
        """After drag-drop, update ordering based on current tree."""
        for i in range(self.tree.topLevelItemCount()):
            mod_item = self.tree.topLevelItem(i)
            mod_item.setText(2, str(i + 1))
            for j in range(mod_item.childCount()):
                les_item = mod_item.child(j)
                les_item.setText(2, str(j + 1))
        # Update course_data with new ordering
    
    def save_structure(self):
        """Persist structure changes to backend or emit signal."""
        structure = []
        for i in range(self.tree.topLevelItemCount()):
            mod_item = self.tree.topLevelItem(i)
            module = {
                "title": mod_item.text(0),
                "order": int(mod_item.text(2)),
                "lessons": [
                    {
                        "title": mod_item.child(j).text(0),
                        "order": int(mod_item.child(j).text(2))
                    }
                    for j in range(mod_item.childCount())
                ]
            }
            structure.append(module)
        QMessageBox.information(self, "Structure Saved", "Course structure saved. (Implement actual DB save)")
        
    def get_selected_categories(self):
        return self.category_selector.get_selected_category_ids()

    def get_selected_tags(self):
        return self.tag_editor.get_selected_tags()
    
    def on_item_changed(self, item, column):
        """Update category and tag editors for current selection."""
        # Implementation depends on backend, can pull/edit item categories/tags.
        pass
        
    def show_prerequisites_dialog(self):
        """Display dialog for managing prerequisites."""
        item = self.tree.currentItem()
        if item is None:
            QMessageBox.warning(self, "No item", "Select a module or lesson to edit prerequisites.")
            return
            
        # Implement multi-select dialog or simple input for prerequisites
        dlg = QInputDialog(self)
        dlg.setLabelText("Enter prerequisite (IDs or titles):")
        dlg.setInputMode(QInputDialog.InputMode.TextInput)
        dlg.exec_()
        prereq_val = dlg.textValue()
        # Actual implementation should allow multi-select/validation.
        QMessageBox.information(self, "Requirement", f"Prerequisite set: {prereq_val}")

    def set_prerequisites_enabled(self, enabled: bool):
        self.prereq_button.setEnabled(enabled)
