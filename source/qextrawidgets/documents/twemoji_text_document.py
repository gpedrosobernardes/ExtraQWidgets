import typing

from PySide6.QtCore import QUrl, QSignalBlocker, QRegularExpression, QSize, Qt, QRegularExpressionMatch
from PySide6.QtGui import (QTextDocument, QTextCursor, QTextImageFormat,
                           QTextCharFormat, QFontMetrics, QTextFragment, QGuiApplication, QPixmap, QPainter)
from emojis.db import Emoji, get_emoji_by_alias, get_emoji_by_code
from urllib.parse import urlparse, urlencode, urlunparse

from qextrawidgets.emoji_utils import EmojiFinder, EmojiImageProvider


class QTwemojiTextDocument(QTextDocument):


    def __init__(self, parent=None, twemoji=True, alias_replacement=True, emoji_margin=1):
        super().__init__(parent)

        self._twemoji = False
        self._twemoji_contents_changed_signal = None
        self._alias_replacement = False
        self._alias_replacement_contents_changed_signal = None
        self._line_limit = 0
        self._limit_line_signal = None
        self._emoji_margin = emoji_margin
        self._emoji_size = -1  # -1 means auto (based on font size)

        # Variable to track where the edit occurred (Optimization B)
        self._last_change_pos = 0

        self.setTwemoji(twemoji)
        self.setAliasReplacement(alias_replacement)

        # Connects the 'Change' signal (before Changed) to capture the position
        self.contentsChange.connect(self._on_contents_change)

    # --- Configurations ---

    def lineLimit(self) -> int:
        return self._line_limit

    def setLineLimit(self, line_limit: int):
        if self._line_limit == line_limit:
            return

        self._line_limit = line_limit

        if line_limit > 0:
            self._limit_line_signal = self.contentsChange.connect(self._limit_line)
        elif self._limit_line_signal:
            self.contentsChanged.disconnect(self._limit_line_signal)
            self._limit_line_signal = None

    def twemoji(self) -> bool:
        return self._twemoji

    def setTwemoji(self, value: bool):
        if self._twemoji == value:
            return

        self._twemoji = value

        if value:
            self._twemoji_contents_changed_signal = self.contentsChanged.connect(self._twemojize)
            # On initial activation, process the entire document
            self._twemojize_full()
        elif self._twemoji_contents_changed_signal:
            self.contentsChanged.disconnect(self._twemoji_contents_changed_signal)
            self._twemoji_contents_changed_signal = None
            self._detwemojize()

    def aliasReplacement(self) -> bool:
        return self._alias_replacement

    def setAliasReplacement(self, value: bool):
        if self._alias_replacement == value:
            return

        self._alias_replacement = value

        if value:
            self._alias_replacement_contents_changed_signal = self.contentsChanged.connect(self._replace_alias)
            self._replace_alias()
        elif self._alias_replacement_contents_changed_signal:
            self.contentsChanged.disconnect(self._replace_alias)
            self._alias_replacement_contents_changed_signal = None

    def emojiMargin(self) -> int:
        return self._emoji_margin

    def setEmojiMargin(self, margin: int):
        if self._emoji_margin == margin:
            return
        self._emoji_margin = margin
        if self._twemoji:
            with QSignalBlocker(self):
                self.updateEmojiImages()

    def emojiSize(self) -> int:
        return self._emoji_size

    def setEmojiSize(self, size: int):
        if self._emoji_size == size:
            return
        self._emoji_size = size
        if self._twemoji:
            with QSignalBlocker(self):
                self.updateEmojiImages()

    # --- Main Logic (Optimization B applied) ---

    def _on_contents_change(self, position, chars_removed, chars_added):
        """Captures the change position before it is processed."""
        self._last_change_pos = position

    def _ensure_resource_loaded(self, emoji: Emoji, size: int, margin: int):
        """Lazy Loading via EmojiImageProvider."""
        if not emoji:
            return

        url = self._encode_url(emoji.aliases[0], margin, size)

        if self.resource(QTextDocument.ResourceType.ImageResource, url):
            return

        dpr = QGuiApplication.primaryScreen().devicePixelRatio()

        pixmap = EmojiImageProvider.get_pixmap(
            emoji_data=emoji,
            size=QSize(size, size),
            dpr=dpr
        )

        if margin > 0:
            total_size = size + (margin * 2)
            final_pixmap = QPixmap(int(total_size * dpr), int(total_size * dpr))
            final_pixmap.setDevicePixelRatio(dpr)
            final_pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(final_pixmap)
            painter.drawPixmap(margin, margin, pixmap)
            painter.end()
            pixmap = final_pixmap

        if not pixmap.isNull():
            self.addResource(QTextDocument.ResourceType.ImageResource, url, pixmap)

    @staticmethod
    def _encode_url(alias, margin=1, size=72, dpr=1.0) -> QUrl:
        params = dict(margin=margin, size=size, dpr=dpr)
        query_string = urlencode(params)
        components = ('twemoji', alias, '', '', query_string, '')
        return QUrl(urlunparse(components))

    def _calculate_emoji_size(self, cursor: QTextCursor) -> int:
        """Calculates the emoji size based on configuration or font."""
        if self._emoji_size != -1:
            return self._emoji_size
        
        font_height = self._font_height(cursor)
        return int(font_height * 0.9)

    def _twemojize(self):
        """
        OPTIMIZED version: Processes only the current block (paragraph).
        Called automatically on every text change.
        """
        # 1. Identifies the block where the edit occurred
        block = self.findBlock(self._last_change_pos)
        if not block.isValid():
            return

        text = block.text()
        block_pos = block.position()

        # 2. Searches for emojis only in this short text
        matches = EmojiFinder.find_all_emoji(text)

        if not matches:
            return

        cursor = QTextCursor(self)
        margin = self._emoji_margin

        # 4. Starts edit block for atomic Undo/Redo
        cursor.beginEditBlock()

        # Process in reverse order (from end of line to start)
        for match in reversed(matches):
            start_rel = match.capturedStart(0)
            end_rel = match.capturedEnd(0)

            # Converts relative block position to absolute document position
            abs_start = block_pos + start_rel
            abs_end = block_pos + end_rel

            cursor.setPosition(abs_start)
            cursor.setPosition(abs_end, QTextCursor.MoveMode.KeepAnchor)

            emoji_size = self._calculate_emoji_size(cursor)

            emoji_str = match.captured(0)
            emoji_without_color = self._remove_emoji_color(emoji_str)
            emoji_obj = get_emoji_by_code(emoji_without_color)

            if emoji_obj:
                self._ensure_resource_loaded(emoji_obj, emoji_size, margin)
                image_fmt = self._emoji_to_text_image(emoji_obj, emoji_size, margin)

                with QSignalBlocker(self):
                    cursor.insertImage(image_fmt)

        cursor.endEditBlock()

    def _twemojize_full(self):
        """Full version for use at initialization (total scan)."""
        cursor = QTextCursor(self)
        margin = self._emoji_margin

        # Uses the old logic of scanning everything (_localize_emojis returns reversed list)
        for emoji, match in reversed(EmojiFinder.find_all_emoji_objects(super().toPlainText(), True)):
            cursor.setPosition(match.capturedStart(0), QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(match.capturedEnd(0), QTextCursor.MoveMode.KeepAnchor)

            emoji_size = self._calculate_emoji_size(cursor)

            self._ensure_resource_loaded(emoji, emoji_size, margin)
            image_fmt = self._emoji_to_text_image(emoji, emoji_size, margin)

            with QSignalBlocker(self):
                cursor.insertImage(image_fmt)

    def updateEmojiImages(self):
        """Updates the margin and size of existing emoji images without converting to text."""
        cursor = QTextCursor(self)
        cursor.beginEditBlock()

        for img_fmt, start, end in self._localize_emoji_images():
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

            emoji = self._text_image_to_emoji(img_fmt)
            if emoji:
                # Recalculate size based on current font height at cursor position or fixed size
                emoji_size = self._calculate_emoji_size(cursor)
                margin = self._emoji_margin

                self._ensure_resource_loaded(emoji, emoji_size, margin)
                new_img_fmt = self._emoji_to_text_image(emoji, emoji_size, margin)

                cursor.insertImage(new_img_fmt)

        cursor.endEditBlock()

    def __replace_alias(self):
        """
        Alias replacement (:smile:).
        Could also be optimized for _last_change_pos, but alias is less frequent.
        Kept global logic for safety, or the same logic as _twemojize could be applied.
        """
        for emoji, match in reversed(EmojiFinder.find_all_emoji_aliases(super().toPlainText())):
            if self._twemoji:
                emoji_size = self._calculate_emoji_size(cursor)
                self._ensure_resource_loaded(emoji, emoji_size, self._emoji_margin)
                image_fmt = self._emoji_to_text_image(emoji, emoji_size, self._emoji_margin)
                self._replace_match(match, image_fmt)
            else:
                self._replace_match(match, emoji.emoji)

    def _replace_match(self, match: typing.Union[QRegularExpressionMatch, QTextFragment], content: typing.Union[str, QTextImageFormat]):
        cursor = QTextCursor(self)

        start = match.position() if isinstance(match, QTextFragment) else match.capturedStart(0)
        end = match.position() + match.length() if isinstance(match, QTextFragment) else match.capturedEnd(0)

        cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

        with QSignalBlocker(self):
            if isinstance(content, QTextImageFormat):
                cursor.removeSelectedText()
                cursor.insertImage(content)
            else:
                cursor.insertText(content)

    # --- Helpers and Utilities ---

    def _limit_line(self, position, chars_removed, chars_added):
        if self._line_limit <= 0:
            return

        if self.blockCount() > self._line_limit:
            cursor = QTextCursor(self)
            cursor.movePosition(QTextCursor.MoveOperation.End)
            with QSignalBlocker(self):
                while self.blockCount() > self._line_limit:
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deletePreviousChar()

    def toPlainText(self) -> str:
        result = ""
        for block in self._blocks():
            for frag in self._fragments(block):
                if self._is_emoji_frag(frag):
                    image_format = frag.charFormat().toImageFormat()
                    emoji = self._text_image_to_emoji(image_format)
                    if emoji:
                        result += emoji.emoji
                else:
                    result += frag.text()
            if block != self.lastBlock():
                result += '\n'
        return result

    # --- Regex and Color Helpers ---

    def _localize_emoji_images(self):
        emoji_images = []
        for frag in self.emoji_fragments():
            img_fmt = frag.charFormat().toImageFormat()
            emoji_images.insert(0, (img_fmt, frag.position(), frag.position() + frag.length()))
        return emoji_images

    def fragments(self):
        for block in self._blocks():
            for frag in self._fragments(block):
                yield frag

    def emoji_fragments(self):
        for frag in self.fragments():
            if self._is_emoji_frag(frag):
                yield frag

    def _blocks(self):
        block = self.firstBlock()
        while block.isValid():
            yield block
            block = block.next()

    @staticmethod
    def _fragments(block):
        it = block.begin()
        while not it.atEnd():
            frag = it.fragment()
            if frag.isValid():
                yield frag
            it += 1

    @staticmethod
    def _is_emoji_frag(frag):
        if frag.charFormat().isImageFormat():
            img_fmt = frag.charFormat().toImageFormat()
            if img_fmt.name().startswith("twemoji://"):
                return True
        return False

    def _detwemojize(self):
        cursor = QTextCursor(self)
        for img_fmt, start, end in self._localize_emoji_images():
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            emoji = self._text_image_to_emoji(img_fmt)
            if emoji:
                cursor.insertText(emoji.emoji)

    @staticmethod
    def _font_height(cursor: QTextCursor):
        font = cursor.charFormat().font()
        fm = QFontMetrics(font)
        return fm.height()

    @staticmethod
    def _get_emoji_colors(emoji: str) -> typing.Set[str]:
        # Iterator correction applied here too
        re_color = QRegularExpression(R"[\x{1F3FB}-\x{1F3FF}]")
        iterator = re_color.globalMatch(emoji)
        matches = set()
        while iterator.hasNext():
            match = iterator.next()
            matches.add(match.captured(0))
        return matches

    def _remove_emoji_color(self, emoji: str) -> str:
        for color in self._get_emoji_colors(emoji):
            emoji = emoji.replace(color, "")
        return emoji

    @staticmethod
    def _emoji_to_text_image(emoji: Emoji, height: int, margin: int) -> QTextImageFormat:
        image = QTextImageFormat()
        if emoji and emoji.aliases:
            name = f"twemoji://{emoji.aliases[0]}"
            if margin > 0:
                name += f"?m={margin}"
            image.setName(name)
            image.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
            total_size = height + (margin * 2)
            image.setHeight(total_size)
            image.setWidth(total_size)
            image.setQuality(100)
        return image

    @staticmethod
    def _text_image_to_emoji(image: QTextImageFormat) -> typing.Optional[Emoji]:
        uri = urlparse(image.name())
        return get_emoji_by_alias(uri.netloc)

    @staticmethod
    def _is_fragment_selected(cursor: QTextCursor, fragment: QTextFragment) -> bool:
        if not cursor.hasSelection():
            return False
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        frag_start = fragment.position()
        frag_end = frag_start + fragment.length()
        return sel_end > frag_start and sel_start < frag_end

    def setDefaultFont(self, font):
        """Override setDefaultFont to trigger emoji resize when font changes."""
        super().setDefaultFont(font)
        if self._twemoji and self._emoji_size == -1:
            # We reuse updateEmojiImages logic which recalculates size based on font
            with QSignalBlocker(self):
                self.updateEmojiImages()
