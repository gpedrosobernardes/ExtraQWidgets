from PySide6.QtGui import QAbstractTextDocumentLayout, QPalette
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle, QApplication

from qextrawidgets import QTwemojiTextDocument

# Deprected
class QStandardTwemojiTextDocumentDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()

        options = QStyleOptionViewItem(option)
        style = options.widget.style() if options.widget else QApplication.style()

        # Documento
        doc = QTwemojiTextDocument()
        doc.setPlainText(index.data(Qt.ItemDataRole.EditRole))
        doc.setTextWidth(option.rect.width())
        doc.setDevicePixelRatio(painter.device().devicePixelRatio())

        # Desenha fundo padrão
        options.features &= ~QStyleOptionViewItem.HasDisplay
        style.drawControl(QStyle.CE_ItemViewItem, options, painter, options.widget)

        # Desenha o HTML
        painter.translate(option.rect.topLeft())
        ctx = QAbstractTextDocumentLayout.PaintContext()

        if option.state & QStyle.State_Selected:
            ctx.palette.setColor(
                QPalette.Text,
                option.palette.color(QPalette.HighlightedText)
            )

        doc.documentLayout().draw(painter, ctx)

        painter.restore()