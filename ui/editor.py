from PyQt5.QtWidgets import QPlainTextEdit, QCompleter, QWidget, QTextEdit
from PyQt5.QtGui import QFont, QTextCursor, QColor, QPainter, QTextFormat
from PyQt5.QtCore import Qt, QRect, QSize
from ui.syntax_highlighter import SyntaxHighlighter

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class ScriptEditor(QPlainTextEdit):

    def __init__(self, keywords=None, applications=None):
        super().__init__()
        self.setFont(QFont("Consolas", 11))
        self.setPlaceholderText("Write your automation script here...")
        self.just_completed = False

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

        # Line number area widget
        self.lineNumberArea = LineNumberArea(self)

        # Connect signals for updating line numbers
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    # --- Line Number related methods ---
    def lineNumberAreaWidth(self):
        digits = 1
        max_block = max(1, self.blockCount())
        while max_block >= 10:
            max_block //= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width()-2, self.fontMetrics().height(),
                                 Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()


            lineColor = QColor(Qt.yellow).lighter(160)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    # --- Autocomplete and other existing methods ---
    def insert_completion(self, completion):
        tc = self.textCursor()
        prefix_len = len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, prefix_len)
        tc.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, prefix_len)
        tc.insertText(completion + ' ')
        self.setTextCursor(tc)
        self.just_completed = True  # Mark completion done

        # Hide the popup immediately after inserting completion
        self.completer.popup().hide()


    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        if self.just_completed:
            # Skip autocomplete logic for the immediate next keypress after completion insert
            self.just_completed = False
            super().keyPressEvent(event)
            return

        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
                self.insert_completion(self.completer.currentCompletion())
                event.accept()
                # Hide popup to prevent it showing again
                self.completer.popup().hide()
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

