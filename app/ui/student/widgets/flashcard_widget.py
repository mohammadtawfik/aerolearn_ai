"""
File location: /app/ui/student/widgets/flashcard_widget.py

Purpose:
    Provides an interactive flashcard widget for spaced repetition and rapid concept review in the AeroLearn AI student interface.
    Students flip cards, mark as 'known' (easy) or 'unknown' (review), and summary is provided for progress tracking.

Context:
    Fulfills the "flashcard component" subtask in Task 3.2.3 Interactive Content Elements (/docs/development/day16_plan.md).

Integration:
    Can be embedded in the student dashboard, module/lesson views, or called with a set of flashcards tied to a content unit.

Author:
    AeroLearn AI Development
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

class FlashcardWidget(QWidget):
    flashcard_reviewed = pyqtSignal(dict)  # Emits {index, known, total, stats}

    def __init__(self, cards, parent=None):
        """
        :param cards: list of dicts with 'front' and 'back' keys
        """
        super().__init__(parent)
        self.cards = cards or []
        self.current = 0
        self.known_count = 0
        self.reviews = [None] * len(self.cards)  # 'known', 'unknown'

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.card_label = QLabel("")
        self.card_label.setWordWrap(True)
        self.layout.addWidget(self.card_label)

        btn_layout = QHBoxLayout()
        self.flip_button = QPushButton("Flip")
        self.flip_button.clicked.connect(self.flip_card)
        self.known_button = QPushButton("Known")
        self.known_button.clicked.connect(lambda: self.mark_card('known'))
        self.unknown_button = QPushButton("Review Again")
        self.unknown_button.clicked.connect(lambda: self.mark_card('unknown'))
        btn_layout.addWidget(self.flip_button)
        btn_layout.addWidget(self.known_button)
        btn_layout.addWidget(self.unknown_button)
        self.layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        self.flipped = False
        self.update_ui()

    def update_ui(self):
        if not self.cards:
            self.card_label.setText("No cards to review.")
            self.flip_button.setEnabled(False)
            self.known_button.setEnabled(False)
            self.unknown_button.setEnabled(False)
            self.status_label.setText("")
            return

        card = self.cards[self.current]
        self.card_label.setText(card['back'] if self.flipped else card['front'])
        self.status_label.setText(
            f"Card {self.current + 1}/{len(self.cards)} | Known: {self.known_count}"
        )
        self.flip_button.setEnabled(True)
        self.known_button.setEnabled(not self.flipped)
        self.unknown_button.setEnabled(not self.flipped)

    def flip_card(self):
        self.flipped = not self.flipped
        self.update_ui()

    def mark_card(self, status):
        self.reviews[self.current] = status
        if status == 'known':
            self.known_count += 1
        self.next_card()

    def next_card(self):
        if self.current < len(self.cards) - 1:
            self.current += 1
            self.flipped = False
            self.update_ui()
        else:
            stats = {
                'total': len(self.cards),
                'known': self.known_count,
                'reviews': self.reviews
            }
            self.flashcard_reviewed.emit(stats)
            QMessageBox.information(
                self, "Review Complete",
                f"Session finished. Known: {self.known_count}/{len(self.cards)}"
            )
            self.close()