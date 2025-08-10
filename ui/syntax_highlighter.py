from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt, QRegExp

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document, keywords, applications):
        super().__init__(document)

        # Format for keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))  # Blue
        keyword_format.setFontWeight(QFont.Bold)

        # Format for applications
        app_format = QTextCharFormat()
        app_format.setForeground(QColor("#008000"))  # Dark Green

        # Format for comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # Gray
        comment_format.setFontItalic(True)

        self.highlighting_rules = []

        # Keywords
        for word in keywords:
            pattern = QRegExp(r'\b' + word + r'\b', Qt.CaseInsensitive)
            self.highlighting_rules.append((pattern, keyword_format))

        # Applications
        for app in applications:
            pattern = QRegExp(r'\b' + app + r'\b', Qt.CaseInsensitive)
            self.highlighting_rules.append((pattern, app_format))

        # Comments - any text after #
        self.highlighting_rules.append((QRegExp(r'#.*'), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)
        self.setCurrentBlockState(0)
