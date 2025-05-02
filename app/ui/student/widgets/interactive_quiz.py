"""
File location: /app/ui/student/widgets/interactive_quiz.py

Purpose:
    Provides an interactive quiz widget for student content interaction in the AeroLearn AI platform.

Context:
    This code fulfills Task 3.2.3 (first subtask) as described in /docs/development/day16_plan.md.

Usage:
    Integrated into the student dashboard/module page for quiz delivery within course content.

Author:
    AeroLearn AI Development

"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QMessageBox, QGroupBox
)
from PyQt6.QtCore import pyqtSignal

class InteractiveQuizWidget(QWidget):
    # Signal emitted when a quiz is completed (can be persisted or analyzed)
    quiz_completed = pyqtSignal(dict)

    def __init__(self, quiz_data, parent=None):
        """
        :param quiz_data: dict with keys 'questions' (list of dicts with 'question', 'options', 'answer')
        """
        super().__init__(parent)
        self.quiz_data = quiz_data
        self.current_question_index = 0
        self.score = 0
        self.selected_option = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.create_quiz_ui()
        self.show_question(self.current_question_index)

    def create_quiz_ui(self):
        self.question_label = QLabel("")
        self.options_group_box = QGroupBox("Options")
        self.options_layout = QVBoxLayout()
        self.options_group = QButtonGroup()
        self.options_group.setExclusive(True)
        self.options_group_box.setLayout(self.options_layout)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.on_next_clicked)

        self.layout.addWidget(self.question_label)
        self.layout.addWidget(self.options_group_box)
        self.layout.addWidget(self.next_button)

    def show_question(self, index):
        question_data = self.quiz_data['questions'][index]
        self.question_label.setText(f"Q{index+1}: {question_data['question']}")
        # Clear previous options
        for btn in self.options_group.buttons():
            self.options_group.removeButton(btn)
            btn.setParent(None)
        for i, option in enumerate(question_data['options']):
            radio = QRadioButton(option)
            self.options_group.addButton(radio, i)
            self.options_layout.addWidget(radio)
        self.selected_option = None
        self.options_group.buttonClicked.connect(self.option_selected)

    def option_selected(self, button):
        self.selected_option = self.options_group.id(button)

    def on_next_clicked(self):
        if self.selected_option is None:
            QMessageBox.warning(self, "No Selection", "Please select an option before proceeding.")
            return
        correct = (
            self.selected_option == 
            self.quiz_data['questions'][self.current_question_index]['answer']
        )
        if correct:
            self.score += 1
        self.current_question_index += 1
        if self.current_question_index < len(self.quiz_data['questions']):
            self.show_question(self.current_question_index)
        else:
            result = {
                'score': self.score,
                'total': len(self.quiz_data['questions']),
                'details': [
                    {
                        'question': q['question'],
                        'correct_answer': q['options'][q['answer']],
                        'selected_answer': q['options'][self.selected_option]
                    }
                    for i, q in enumerate(self.quiz_data['questions'])
                ]
            }
            self.quiz_completed.emit(result)
            QMessageBox.information(
                self, "Quiz Completed",
                f"You scored {self.score}/{len(self.quiz_data['questions'])}!"
            )
            self.close()