from PyQt5.QtWidgets import QPlainTextEdit, QCompleter
from PyQt5.QtGui import QFont, QTextCursor
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
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setWrapAround(False)
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        tc = self.textCursor()
        # Move cursor left to select current prefix and replace it
        prefix_len = len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, prefix_len)
        tc.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, prefix_len)
        tc.insertText(completion)
        self.setTextCursor(tc)

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        if self.completer.popup().isVisible():
            # Accept completion on Tab or Enter
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
                self.insert_completion(self.completer.currentCompletion())
                event.accept()
                return
            elif event.key() == Qt.Key_Escape:
                self.completer.popup().hide()
                event.accept()
                return

        super().keyPressEvent(event)

        ctrl_or_shift = event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if ctrl_or_shift and event.text() == '':
            return

        eow = "~!@#$%^&*()+{}|:\"<>?,./;'[]\\-="  # end of word characters
        completion_prefix = self.text_under_cursor()

        if (not ctrl_or_shift and completion_prefix != '' and
            len(completion_prefix) > 0 and event.text() not in eow):
            self.completer.setCompletionPrefix(completion_prefix)
            cr = self.cursorRect()
            cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                        self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)
        else:
            self.completer.popup().hide()
