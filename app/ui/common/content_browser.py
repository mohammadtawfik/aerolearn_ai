"""
AeroLearn AI - Content Browser Component
(Migrated to PyQt6)

This module provides the ContentBrowser UI widget for displaying lists and trees of
content items (documents, lessons, media, etc.), supporting filtering, search, selection,
and drag-and-drop integration.

Intended for use with a Qt UI stack (PyQt/PySide), but logic is separable.

Features:
- List and tree mode for content
- Icons/thumbnails per type
- Text search/filter
- Selection events (single, multiple)
- Drag-and-drop support (signals/hooks)
- EventBus integration for content selection

Extensible to work with actual content models/data sources.

"""

from typing import List, Callable, Optional, Any, Dict

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QLabel, QAbstractItemView, QTreeWidget, QTreeWidgetItem)
    from PyQt6.QtCore import Qt, pyqtSignal
except ImportError:
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QLabel, QAbstractItemView, QTreeWidget, QTreeWidgetItem, Qt, pyqtSignal = (object,) * 10

# EventBus integration placeholder
try:
    from integrations.events.event_bus import EventBus
except ImportError:
    EventBus = None

class ContentBrowser(QWidget):
    """Widget to browse, search, and select content items."""
    content_selected = pyqtSignal(dict)
    content_dragged = pyqtSignal(dict)

    def __init__(self, content_items: Optional[List[Dict[str, Any]]] = None, tree_mode: bool = False):
        super().__init__()
        self.content_items = content_items or []  # Each item: dict with keys: id, label, type, thumbnail, etc.
        self.tree_mode = tree_mode
        self._setup_ui()
        self._populate()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search content...")
        self.layout.addWidget(QLabel("Content Browser"))
        self.layout.addWidget(self.search_box)
        if self.tree_mode:
            self.list_widget = QTreeWidget()
            self.list_widget.setHeaderLabels(['Title', 'Type'])
        else:
            self.list_widget = QListWidget()
            self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)
        self.search_box.textChanged.connect(self._filter_content)

        # Drag-and-drop setup
        if hasattr(self.list_widget, 'setDragEnabled'):
            self.list_widget.setDragEnabled(True)
        if hasattr(self.list_widget, 'setAcceptDrops'):
            self.list_widget.setAcceptDrops(True)
        if hasattr(self.list_widget, "itemDoubleClicked"):
            self.list_widget.itemDoubleClicked.connect(self._item_selected)
        # For tree, would need separate signal with currentItemChanged

    def _populate(self):
        if self.tree_mode:
            self.list_widget.clear()
            for item in self.content_items:
                tree_item = QTreeWidgetItem([item.get("label", "Untitled"), item.get("type", "Unknown")])
                self.list_widget.addTopLevelItem(tree_item)
        else:
            self.list_widget.clear()
            for item in self.content_items:
                lw_item = QListWidgetItem(item.get("label", "Untitled"))
                # Optionally set icon/thumbnails
                self.list_widget.addItem(lw_item)

    def _filter_content(self, query):
        query = query.lower()
        # Simple filter: show/hide by label
        if self.tree_mode:
            for i in range(self.list_widget.topLevelItemCount()):
                item = self.list_widget.topLevelItem(i)
                text = item.text(0).lower()
                item.setHidden(query not in text)
        else:
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                item.setHidden(query not in item.text().lower())

    def _item_selected(self, item):
        label = item.text() if hasattr(item, 'text') else str(item)
        selected = next((c for c in self.content_items if c.get('label') == label), None)
        if selected:
            self.content_selected.emit(selected)
            if EventBus:
                EventBus.get().publish({
                    "type": "UIEvent.ContentSelected",
                    "content": selected
                })

    # Drag events - simplified placeholder hooks for actual logic
    def startDrag(self, event):
        # Hook for drag-out start
        current = self.list_widget.currentItem()
        if current:
            label = current.text()
            content = next((c for c in self.content_items if c.get('label') == label), None)
            if content:
                self.content_dragged.emit(content)
                if EventBus:
                    EventBus.get().publish({
                        "type": "UIEvent.ContentDragStart",
                        "content": content
                    })

    # There should be platform/Qt-specific dropEvent overrides.

# Example: Minimal test widget
def create_test_content_browser():
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ContentBrowser(content_items=[
        {'id': 1, 'label': 'Physics Lecture', 'type': 'Video'},
        {'id': 2, 'label': 'Intro to Aerodynamics', 'type': 'Document'},
        {'id': 3, 'label': 'Problem Set 1', 'type': 'PDF'},
    ])
    window.resize(400, 300)
    window.show()
    app.exec()

if __name__ == '__main__':
    create_test_content_browser()
