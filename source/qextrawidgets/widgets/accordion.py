from PySide6.QtCore import Qt, Signal, QEasingCurve
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame

from qextrawidgets.widgets.accordion_item import QAccordionItem, QAccordionHeader


class QAccordion(QWidget):
    """
    Accordion widget with optional smooth animations.
    Supports multiple accordion items with expand/collapse animations.
    """

    enteredSection = Signal(QAccordionItem)
    leftSection = Signal(QAccordionItem)

    def __init__(self):
        super().__init__()
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._scroll.setWidget(self._scroll_content)
        self._main_layout.addWidget(self._scroll)

        self._active_section = None
        self._items = []

        # Animation settings (applied to new items)
        self._default_animation_enabled = True
        self._default_animation_duration = 200
        self._default_animation_easing = QEasingCurve.Type.InOutQuart

        self._setup_connections()

    def _setup_connections(self):
        self._scroll.verticalScrollBar().valueChanged.connect(self._on_scroll)

    def _on_scroll(self, value):
        for item in self._items:
            if item.y() <= value <= item.y() + item.height() and item != self._active_section:
                self.enteredSection.emit(item)
                if self._active_section is not None:
                    self.leftSection.emit(item)
                self._active_section = item
                break

    def _on_item_expanded(self, position: int, expanded: bool):
        """Called when an item is expanded."""
        self._scroll_layout.setStretch(position, expanded)

    # --- Item Management ---

    def setSectionTitle(self, index: int, title: str):
        self._items[index].setTitle(title)

    def addSection(self, title: str, widget: QWidget):
        self.insertSection(title, widget)

    def addAccordionItem(self, item: QAccordionItem):
        self.insertAccordionItem(item)

    def insertSection(self, title: str, widget: QWidget, position: int = -1) -> QAccordionItem:
        """
        Creates and adds a new accordion section.

        :param title: Section title
        :param widget: Content widget
        :param position: Insert position (-1 for end)
        :return: The created QAccordionItem
        """
        item = QAccordionItem(title, widget)
        # Apply default animation settings
        item.setAnimationEnabled(self._default_animation_enabled)
        item.setAnimationDuration(self._default_animation_duration)
        item.setAnimationEasing(self._default_animation_easing)

        self.insertAccordionItem(item, position)
        return item

    def insertAccordionItem(self, item: QAccordionItem, position: int = -1):
        """
        Adds an existing QAccordionItem.

        :param item: QAccordionItem to add
        :param position: Insert position (-1 for end)
        """
        self._scroll_layout.insertWidget(position, item)
        item.expandedChanged.connect(lambda expanded: self._on_item_expanded(position, expanded))
        self._items.append(item)

    def removeAccordionItem(self, item: QAccordionItem):
        """
        Removes an accordion item.

        :param item: QAccordionItem to remove
        """
        self._scroll_layout.removeWidget(item)
        self._items.remove(item)

    # --- Style Settings (Applied to ALL items) ---

    def setIconPosition(self, position: QAccordionHeader.IconPosition):
        """Changes the icon position (left/right) of ALL items."""
        for item in self._items:
            item.setIconPosition(position)

    def setIconStyle(self, style: QAccordionHeader.IndicatorStyle):
        """Changes the icon style (arrow/plus_minus) of ALL items."""
        for item in self._items:
            item.setIconStyle(style)

    def setFlat(self, flat: bool):
        """Sets whether headers are flat or raised for ALL items."""
        for item in self._items:
            item.setFlat(flat)

    # --- Animation Settings (Applied to ALL items) ---

    def setAnimationEnabled(self, enabled: bool):
        """
        Enables or disables animations for ALL items.

        :param enabled: True to enable animations, False to disable
        """
        self._default_animation_enabled = enabled
        for item in self._items:
            item.setAnimationEnabled(enabled)

    def animationEnabled(self) -> bool:
        """Returns the default animation enabled state."""
        return self._default_animation_enabled

    def setAnimationDuration(self, duration: int):
        """
        Sets the animation duration in milliseconds for ALL items.

        :param duration: Duration in milliseconds (typical: 100-500)
        """
        self._default_animation_duration = duration
        for item in self._items:
            item.setAnimationDuration(duration)

    def animationDuration(self) -> int:
        """Returns the default animation duration."""
        return self._default_animation_duration

    def setAnimationEasing(self, easing: QEasingCurve.Type):
        """
        Sets the animation easing curve for ALL items.

        Common options:
        - QEasingCurve.Type.Linear: Constant speed
        - QEasingCurve.Type.InOutQuad: Smooth acceleration/deceleration
        - QEasingCurve.Type.InOutQuart: More pronounced easing (default)
        - QEasingCurve.Type.OutCubic: Fast start, slow end
        - QEasingCurve.Type.InOutBack: Slight overshoot effect

        :param easing: QEasingCurve.Type
        """
        self._default_animation_easing = easing
        for item in self._items:
            item.setAnimationEasing(easing)

    def animationEasing(self) -> QEasingCurve.Type:
        """Returns the default animation easing curve."""
        return self._default_animation_easing

    # --- Expand/Collapse Operations ---

    def expandAll(self, animated: bool = None):
        """
        Expands all accordion items.

        :param animated: Override animation setting. If None, uses each item's setting.
        """
        for item in self._items:
            item.setExpanded(True, animated=animated)

    def collapseAll(self, animated: bool = None):
        """
        Collapses all accordion items.

        :param animated: Override animation setting. If None, uses each item's setting.
        """
        for item in self._items:
            item.setExpanded(False, animated=animated)

    # --- Scroll Operations ---

    def scrollToItem(self, target_item: QAccordionItem):
        """
        Scrolls to make the target item visible.

        :param target_item: QAccordionItem to scroll to
        """
        # Gets the Y coordinate of the target widget relative to the ScrollArea content
        y_pos = target_item.y()
        # Sets the vertical scroll bar value
        self._scroll.verticalScrollBar().setValue(y_pos)

    def resetScroll(self):
        """Scrolls to the top of the accordion."""
        self._scroll.verticalScrollBar().setValue(0)