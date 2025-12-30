from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QApplication

from extra_qwidgets.widgets.accordion_item import QAccordionItem


class QAccordion(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.items = []

    def addSection(self, title, widget):
        item = QAccordionItem(title, widget)
        self.scroll_layout.addWidget(item)
        self.items.append(item)
        return item

    def setIconPosition(self, position):
        """Muda a posição do ícone (left/right) de TODOS os itens."""
        for item in self.items:
            item.setIconPosition(position)

    def setIconStyle(self, style):
        """Muda o estilo do ícone (arrow/plus_minus) de TODOS os itens."""
        for item in self.items:
            item.setIconStyle(style)

    def setFlat(self, flat):
        for item in self.items:
            item.setFlat(flat)

    def expandAll(self):
        for item in self.items:
            item.setExpanded(True)

    def collapseAll(self):
        for item in self.items:
            item.setExpanded(False)

    def scrollToItem(self, target_item):
        if not target_item.content().isVisible():
            target_item.toggle()

        # 2. Forçar o processamento de eventos pendentes
        # Isto é CRUCIAL: Como acabámos de dar .show() no conteúdo, o layout
        # precisa de calcular o novo tamanho antes de sabermos para onde rolar.
        QApplication.processEvents()

        # 3. Mandar o ScrollArea focar no widget
        # xmargin=0, ymargin=0 garante que ele aparece,
        # mas pode adicionar margem (ex: 20) para não ficar colado ao topo.
        self.scroll.ensureWidgetVisible(target_item)

    def scrollToHeader(self, target_item: QAccordionItem):
        self.scroll.ensureWidgetVisible(target_item.header())

    def resetScroll(self):
        self.scroll.verticalScrollBar().setValue(0)