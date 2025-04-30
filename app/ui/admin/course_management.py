# Admin UI for Course Management (PyQt6)
# Save as: /app/ui/admin/course_management.py

from PyQt6 import QtWidgets, QtCore
# Import in a way that allows for mock implementations in testing
from app.core.db.course_admin import CourseAdminService

class CourseManagementWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, db_url="sqlite:///app_database.db"):
        super().__init__(parent)
        self.setWindowTitle("Course Management")
        
        # Use the DBClient singleton to obtain the SQLAlchemy engine
        self.db = DBClient(db_url)
        self.session = sessionmaker(bind=self.db.engine)()
        self.service = CourseAdminService(self.session)
        self.setup_ui()
        self.load_courses()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.course_list = QtWidgets.QListWidget()
        self.btn_refresh = QtWidgets.QPushButton("Refresh")
        self.btn_create = QtWidgets.QPushButton("Create Course")
        self.btn_archive = QtWidgets.QPushButton("Archive Selected")
        self.btn_restore = QtWidgets.QPushButton("Restore Archived")
        self.btn_enroll_bulk = QtWidgets.QPushButton("Bulk Enroll...")

        layout.addWidget(self.course_list)
        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.btn_create)
        layout.addWidget(self.btn_archive)
        layout.addWidget(self.btn_restore)
        layout.addWidget(self.btn_enroll_bulk)

        self.btn_refresh.clicked.connect(self.load_courses)
        self.btn_create.clicked.connect(self.create_course)
        self.btn_archive.clicked.connect(self.archive_selected)
        self.btn_restore.clicked.connect(self.restore_selected)
        self.btn_enroll_bulk.clicked.connect(self.bulk_enroll_dialog)

    def load_courses(self):
        self.course_list.clear()
        for course in self.service.list_courses(include_archived=True):
            status = "[Archived]" if course.is_archived else ""
            item = QtWidgets.QListWidgetItem(f"{course.title} {status}")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, course.id)
            self.course_list.addItem(item)

    def get_selected_course_id(self):
        item = self.course_list.currentItem()
        if item:
            return item.data(QtCore.Qt.ItemDataRole.UserRole)
        return None

    def create_course(self):
        title, ok = QtWidgets.QInputDialog.getText(self, "Create Course", "Course Title:")
        if ok and title:
            self.service.create_course(title=title)
            self.load_courses()

    def archive_selected(self):
        course_id = self.get_selected_course_id()
        if course_id:
            self.service.archive_course(course_id)
            self.load_courses()

    def restore_selected(self):
        course_id = self.get_selected_course_id()
        if course_id:
            self.service.restore_course(course_id)
            self.load_courses()

    def bulk_enroll_dialog(self):
        # Simple dialog example for bulk enrollment by comma-separated user IDs
        text, ok = QtWidgets.QInputDialog.getText(self, "Bulk Enroll", "User IDs (comma-separated):")
        if ok and text:
            ids = [int(i.strip()) for i in text.split(',') if i.strip().isdigit()]
            course_id = self.get_selected_course_id()
            if course_id and ids:
                self.service.enroll_users_bulk(course_id, ids)

# Usage:
# Add to admin panel launcher or instantiate in tests.
