# ui/terminal.py

from PyQt5.QtWidgets import QPlainTextEdit

class DebugTerminal(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def log(self, text):
        self.appendPlainText(text)
