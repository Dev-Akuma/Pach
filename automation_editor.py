import sys
import time
import subprocess
import pyautogui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QWidget,
    QPushButton, QTextEdit, QCompleter
)
from PyQt5.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtCore import Qt, QRegExp


class ScriptExit(Exception):
    pass


class AutomationSyntaxHighlighter(QSyntaxHighlighter):
    # (Same as before - keep your syntax highlighter code here)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.keywordFormat = QTextCharFormat()
        self.keywordFormat.setForeground(QColor("#0000FF"))
        self.keywordFormat.setFontWeight(QFont.Bold)

        self.commentFormat = QTextCharFormat()
        self.commentFormat.setForeground(QColor("#008000"))
        self.commentFormat.setFontItalic(True)

        self.keywords = [
            "wait", "open", "close", "type", "press", "mouse",
            "if", "endif", "loop", "endloop", "exit"
        ]

        self.keywordPatterns = [QRegExp(f"\\b{word}\\b") for word in self.keywords]
        self.commentPattern = QRegExp("#[^\n]*")

    def highlightBlock(self, text):
        for pattern in self.keywordPatterns:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, self.keywordFormat)
                index = pattern.indexIn(text, index + length)

        index = self.commentPattern.indexIn(text)
        if index >= 0:
            length = self.commentPattern.matchedLength()
            self.setFormat(index, length, self.commentFormat)


class AutomationEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Automation Script Editor - PyQt5")
        self.resize(800, 600)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout()
        centralWidget.setLayout(layout)

        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Consolas", 11))
        layout.addWidget(self.editor)

        keywords = [
            "wait", "open", "close", "type", "press", "mouse",
            "if", "endif", "loop", "endloop", "exit"
        ]
        self.completer = QCompleter(keywords)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWrapAround(False)
        self.completer.setWidget(self.editor)
        self.completer.activated.connect(self.insert_completion)
        self.editor.keyPressEvent = self.editor_keyPressEvent

        self.highlighter = AutomationSyntaxHighlighter(self.editor.document())

        self.runButton = QPushButton("Run Script")
        layout.addWidget(self.runButton)
        self.runButton.clicked.connect(self.run_script)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        self.console.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.console)

    # Autocomplete methods (same as before)
    def editor_keyPressEvent(self, event):
        QPlainTextEdit.keyPressEvent(self.editor, event)
        ctrl_or_shift = event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if ctrl_or_shift and event.text() == '':
            return
        completion_prefix = self.get_current_word()
        if completion_prefix != '':
            self.completer.setCompletionPrefix(completion_prefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
            cr = self.editor.cursorRect()
            cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                        + self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)
        else:
            self.completer.popup().hide()

    def get_current_word(self):
        cursor = self.editor.textCursor()
        cursor.select(cursor.WordUnderCursor)
        return cursor.selectedText()

    def insert_completion(self, completion):
        tc = self.editor.textCursor()
        tc.movePosition(tc.Left, tc.MoveAnchor, len(self.completer.completionPrefix()))
        tc.movePosition(tc.Right, tc.KeepAnchor, len(self.completer.completionPrefix()))
        tc.insertText(completion)
        self.editor.setTextCursor(tc)

    # ----------- SCRIPT EXECUTION LOGIC -----------

    def run_script(self):
        script = self.editor.toPlainText().strip()
        self.console.append("=== Running script ===")
        lines = script.splitlines()

        try:
            for lineno, line in enumerate(lines, start=1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                self.console.append(f"> Line {lineno}: {line}")
                self.execute_line(line)
        except ScriptExit:
            self.console.append("=== Script exited by user command ===\n")
        except Exception as e:
            self.console.append(f"❌ Error on line {lineno}: {str(e)}")
        else:
            self.console.append("=== Script finished ===\n")


    def execute_line(self, line):
        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "wait":
            seconds = float(arg)
            self.console.append(f"⏳ Waiting for {seconds} seconds...")
            QApplication.processEvents()
            time.sleep(seconds)

        elif cmd == "open":
            self.console.append(f"🔓 Opening application: {arg}")
            # open app code here ...

        elif cmd == "type":
            self.console.append(f"⌨️ Typing: {arg}")
            QApplication.processEvents()
            pyautogui.write(arg)

        elif cmd == "exit":
            self.console.append("🚪 Exiting script execution.")
            raise ScriptExit()

        else:
            raise ValueError(f"Unknown command: {cmd}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutomationEditor()
    window.show()
    sys.exit(app.exec_())
