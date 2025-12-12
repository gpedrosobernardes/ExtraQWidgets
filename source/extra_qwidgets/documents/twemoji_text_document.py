from PySide6.QtCore import QUrl, QSignalBlocker, QTextBoundaryFinder, QRegularExpression
from PySide6.QtGui import QTextDocument, QTextCursor, QTextImageFormat, QImage, QTextCharFormat, \
    QFontMetrics
from emojis.db import Emoji, get_emoji_by_alias
from pydantic import ValidationError
from twemoji_api.api import get_all_emojis
from twemoji_api.params import EmojiParams

from extra_qwidgets.utils import scale_inside


class QTwemojiTextDocument(QTextDocument):
    def __init__(self, parent = None, twemoji = True, alias_replacement = True):
        super().__init__(parent)
        self.setTwemoji(twemoji)
        self.setAliasReplacement(alias_replacement)
        self._load_emojis()

    def _load_emojis(self):
        for e in get_all_emojis():
            alias = e.emoji.aliases[0]
            url = QUrl(f"twemoji://{alias}")
            img = QImage(str(e.path))
            self.addResource(
                QTextDocument.ResourceType.ImageResource,
                url,
                scale_inside(img, 0.9)
            )

    def twemoji(self):
        return self._twemoji

    def setTwemoji(self, value):
        self._twemoji = value

        if value:
            self.contentsChanged.connect(self._twemojize)
            self._twemojize()
        else:
            self.contentsChanged.disconnect(self._twemojize)
            self._detwemojize()

    def aliasReplacement(self):
        return self._alias_replacement

    def setAliasReplacement(self, value):
        self._alias_replacement = value

        if value:
            self.contentsChanged.connect(self._replace_alias)
            self._replace_alias()
        else:
            self.contentsChanged.disconnect(self._replace_alias)

    def _replace_alias(self):
        text = self.toPlainText()
        re = QRegularExpression(R"(:\w+:)")
        cursor = QTextCursor(self)
        global_match = re.globalMatch(text)
        matches = []
        font_height = self._font_heigth(cursor)

        while global_match.hasNext():
            matches.append(global_match.next())

        for match in reversed(matches):
            words = match.captured(0)[1:-1]
            start = match.capturedStart(0)
            end = match.capturedEnd(0)
            cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            emoji = get_emoji_by_alias(words)
            if emoji:
                if self._twemoji:
                    image = self.emoji_to_text_image(emoji, font_height)
                    with QSignalBlocker(self):
                        cursor.removeSelectedText()
                        cursor.insertImage(image)
                else:
                    with QSignalBlocker(self):
                        cursor.insertText(emoji.emoji)


    @staticmethod
    def _font_heigth(cursor):
        font = cursor.charFormat().font()
        font_metrics = QFontMetrics(font)
        return font_metrics.lineSpacing() + font_metrics.leading()

    def _twemojize(self):
        cursor = QTextCursor(self)

        font_height = self._font_heigth(cursor)

        text = self.toPlainText()
        finder = QTextBoundaryFinder(QTextBoundaryFinder.BoundaryType.Grapheme, text)
        finder.toEnd()
        pos = finder.position()

        while pos > 0:
            previous_pos = pos
            pos = finder.toPreviousBoundary()
            cursor.setPosition(pos, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(previous_pos, QTextCursor.MoveMode.KeepAnchor)
            current_text = cursor.selectedText()
            with QSignalBlocker(self):
                try:
                    emoji = EmojiParams(emoji=current_text).emoji
                except ValidationError:
                    pass
                else:
                    cursor.removeSelectedText()
                    image = self.emoji_to_text_image(emoji, font_height)
                    cursor.insertImage(image)

    def _detwemojize(self):
        block = self.begin()

        fragments_to_replace = []
        while block.isValid():
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()
                if frag.isValid() and frag.charFormat().isImageFormat():
                    img_fmt = frag.charFormat().toImageFormat()
                    if img_fmt.name().startswith("twemoji://"):
                        fragments_to_replace.append((frag.position(), frag.length(), img_fmt))
                it += 1
            block = block.next()

        cursor = QTextCursor(self)
        for pos, length, img_fmt in reversed(fragments_to_replace):
            cursor.setPosition(pos)
            cursor.setPosition(pos + length, QTextCursor.MoveMode.KeepAnchor)
            emoji = self.text_image_to_emoji(img_fmt)
            cursor.insertText(emoji.emoji)

    @staticmethod
    def emoji_to_text_image(emoji: Emoji, height: int) -> QTextImageFormat:
        image = QTextImageFormat()
        image.setName(f"twemoji://{emoji.aliases[0]}")
        image.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
        image.setHeight(height)
        return image

    @staticmethod
    def text_image_to_emoji(image: QTextImageFormat) -> Emoji:
        alias = image.name()[10:]
        return get_emoji_by_alias(alias)

