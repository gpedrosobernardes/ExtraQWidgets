from PySide6.QtGui import QTextDocument, QFontMetricsF
from PySide6.QtWidgets import QTextEdit

from extra_qwidgets.documents.twemoji_text_document import QTwemojiTextDocument


class QExtraTextEdit(QTextEdit):
    def __init__(self, parent = None, twemoji = True, alias_replacement = True):
        super(QExtraTextEdit, self).__init__(parent)
        self.setDocument(QTwemojiTextDocument(self, twemoji, alias_replacement))
