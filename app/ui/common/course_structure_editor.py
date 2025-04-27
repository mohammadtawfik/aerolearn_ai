# /app/ui/common/course_structure_editor.py

"""
CourseStructureEditor: UI component for hierarchical editing and sequencing
of courses, modules, lessons, supporting drag-and-drop, order changes,
and prerequisite assignment.

Intended for PyQt5/PySide2, but UI toolkit can be swapped.
"""

from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QMimeData, QByteArray

from app.ui.common.category_multiselect import CategoryMultiSelect
from app.ui.common.tag_autocomplete import TagAutocomplete

class CourseStructureEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Course Structure Editor")
        self.layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Title", "Type", "Order"])
        self.tree.setDragDropMode(QTreeWidget.InternalMove)
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
        
        self.save_button = QPushButton("Save Structure")
        self.layout.addWidget(self.save_button)
        # TODO: Connect signals, update model with selected categories/tags.

    def load_course_structure(self, course_data):
        """
        Loads the hierarchical structure from provided course data.
        course_data: list/dict object matching Course > Module > Lesson hierarchy.
        """
        self.tree.clear()
        for module in course_data.get('modules', []):
            m_item = QTreeWidgetItem([module['title'], "Module", str(module['order'])])
            for lesson in module.get('lessons', []):
                l_item = QTreeWidgetItem([lesson['title'], "Lesson", str(lesson['order'])])
                m_item.addChild(l_item)
            self.tree.addTopLevelItem(m_item)
        # TODO: Implement event handlers for selection to update cat/tag editors.

    def get_selected_categories(self):
        return self.category_selector.get_selected_category_ids()

    def get_selected_tags(self):
        return self.tag_editor.get_selected_tags()

    # Placeholder for prerequisite UI, etc.
    def set_prerequisites_enabled(self, enabled: bool):
        pass
