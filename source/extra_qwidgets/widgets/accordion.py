from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame

from extra_qwidgets.widgets.accordion_item import QAccordionItem


class QAccordion(QWidget):
    enteredSection = Signal(QAccordionItem)
    leftSection = Signal(QAccordionItem)

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

        self._active_section = None

        self.items = []

        self._setup_connections()

    def _setup_connections(self):
        self.scroll.verticalScrollBar().valueChanged.connect(self._on_scroll)

    def _on_scroll(self, value):
        for item in self.items:
            if item.y() <= value <= item.y() + item.height() and item != self._active_section:
                self.enteredSection.emit(item)
                if self._active_section is not None:
                    self.leftSection.emit(item)
                self._active_section = item
                break

    def addSection(self, title: str, widget: QWidget, position: int = -1) -> QAccordionItem:
        item = QAccordionItem(title, widget)
        self.addAccordionItem(item, position)
        return item

    def addAccordionItem(self, item: QAccordionItem, position: int = -1):
        self.scroll_layout.insertWidget(position, item)
        self.items.append(item)

    def removeAccordionItem(self, item: QAccordionItem):
        self.scroll_layout.removeWidget(item)
        self.items.remove(item)

    def setIconPosition(self, position):
        """Changes the icon position (left/right) of ALL items."""
        for item in self.items:
            item.setIconPosition(position)

    def setIconStyle(self, style):
        """Changes the icon style (arrow/plus_minus) of ALL items."""
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

    def scrollToItem(self, target_item: QAccordionItem):
        # 1. Gets the Y coordinate of the target widget relative to the ScrollArea content
        # (Assuming target_widget is a direct child of the content widget)
        y_pos = target_item.y()

        # 2. Sets the vertical scroll bar value
        self.scroll.verticalScrollBar().setValue(y_pos)

    def resetScroll(self):
        self.scroll.verticalScrollBar().setValue(0)
