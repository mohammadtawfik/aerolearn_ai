# /app/ui/common/course_organization_search.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt

class CourseOrganizationSearch(QWidget):
    """
    Search/filter control for courses, modules, or lessons by tag or category.
    """
    def __init__(self, on_search=None, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.input_layout = QHBoxLayout()
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Category (optional)")
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Tag (optional)")
        self.search_btn = QPushButton("Search")
        self.input_layout.addWidget(QLabel("Search/filter:"))
        self.input_layout.addWidget(self.category_input)
        self.input_layout.addWidget(self.tag_input)
        self.input_layout.addWidget(self.search_btn)
        self.layout.addLayout(self.input_layout)
        self.results = QListWidget()
        self.layout.addWidget(self.results)
        self.on_search = on_search
        self.search_btn.clicked.connect(self._search)

    def _search(self):
        # Placeholder: In production, call a backend service or filter data.
        c = self.category_input.text().strip()
        t = self.tag_input.text().strip()
        results = []
        if self.on_search:
            results = self.on_search(category=c, tag=t)
        self.results.clear()
        for r in results or []:
            self.results.addItem(QListWidgetItem(str(r)))