from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QLineEdit


class CustomComboBox(QComboBox):

    def __init__(self):
        super().__init__()
        self.setEditable(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            event.accept()
        else:
            super().keyPressEvent(event)


class CustomLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            event.accept()
        else:
            super().keyPressEvent(event)
