import re

from PySide6.QtCore import QModelIndex, Qt, QPoint, QSize
from PySide6.QtGui import QPainter, QPalette
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QApplication, QStyle
from emojis import emojis

from qextrawidgets.emoji_utils import EmojiImageProvider


class QStandardTwemojiDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()

        options = QStyleOptionViewItem(option)
        style = options.widget.style() if options.widget else QApplication.style()

        options.features &= ~QStyleOptionViewItem.HasDisplay
        style.drawControl(QStyle.CE_ItemViewItem, options, painter, options.widget)

        text = index.data(Qt.DisplayRole)
        fm = option.fontMetrics

        pen_color = option.palette.color(
            QPalette.HighlightedText
            if option.state & QStyle.State_Selected
            else QPalette.Text
        )
        painter.setPen(pen_color)

        # Dentro do paint()
        style = option.widget.style()

        # Pede o retângulo exato onde o texto deve ficar
        text_rect = style.subElementRect(QStyle.SE_ItemViewItemText, option, option.widget)

        # Calculate baseline
        text_cursor = QPoint(text_rect.left(), text_rect.top() + fm.ascent())
        image_cursor = QPoint(text_rect.left(), text_rect.top())

        text = index.data(Qt.ItemDataRole.EditRole)
        for block in self.get_text_blocks(text):
            emoji = emojis.db.get_emoji_by_code(block)
            if emoji:
                emoji_size = QSize(fm.height(), fm.height())
                pixmap = EmojiImageProvider.getPixmap(emoji, 0, emoji_size, painter.device().devicePixelRatio())
                painter.drawPixmap(image_cursor, pixmap)
                horizontal_advance = emoji_size.width()
            else:
                horizontal_advance = fm.horizontalAdvance(block)
                painter.drawText(text_cursor, block)
            text_cursor.setX(text_cursor.x() + horizontal_advance)
            image_cursor.setX(image_cursor.x() + horizontal_advance)

        painter.restore()

    @staticmethod
    def get_text_blocks(text: str):
        return [block for block in re.split(emojis.RE_EMOJI_TO_TEXT, text) if block]
