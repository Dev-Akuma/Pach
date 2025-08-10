from PyQt5.QtWidgets import QPlainTextEdit, QCompleter
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.syntax_highlighter import SyntaxHighlighter

class ScriptEditor(QPlainTextEdit):
    def __init__(self, keywords=None, applications=None):
        super().__init__()
        self.setFont(QFont("Consolas", 11))
        self.setPlaceholderText("Write your automation script here...")

        self.keywords = keywords or []
        self.applications = applications or []

        # Setup syntax highlighter
        self.highlighter = SyntaxHighlighter(self.document(), self.keywords, self.applications)

        # Setup autocomplete
        self.completer = QCompleter(self.keywords + self.applications)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(tc.Left, tc.MoveAnchor, len(self.completer.completionPrefix()))
        tc.insertText(completion)
        self.setTextCursor(tc)

    def keyPressEvent(self, event):
        if self.completer.popup().isVisible():
            # Let completer handle navigation keys
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape,
                               Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()
                return

        super().keyPressEvent(event)

        ctrl_or_shift = event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if ctrl_or_shift and event.text() == '':
            return

        eow = "~!@#$%^&*()+{}|:\"<>?,./;'[]\\-="  # end of word characters
        has_modifier = (event.modifiers() != Qt.NoModifier) and not ctrl_or_shift
        completion_prefix = self.text_under_cursor()

        if not has_modifier and completion_prefix != '' and (len(completion_prefix) > 0) and event.text()[-1] not in eow:
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.complete()
        else:
            self.completer.popup().hide()

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(tc.WordUnderCursor)
        return tc.selectedText()
