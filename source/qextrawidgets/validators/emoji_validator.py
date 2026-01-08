from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from qextrawidgets.emoji_utils import EmojiFinder


class QEmojiValidator(QRegularExpressionValidator):
    def __init__(self, parent=None):
        emoji_pattern = EmojiFinder.getEmojiPattern()

        regex = QRegularExpression(
            f"^(?:{emoji_pattern})+$",
            QRegularExpression.PatternOption.UseUnicodePropertiesOption
        )

        super().__init__(regex, parent)