import typing

from PySide6.QtCore import QUrl, QSignalBlocker, QRegularExpression, QSize
from PySide6.QtGui import (QTextDocument, QTextCursor, QTextImageFormat,
                           QTextCharFormat, QFontMetrics, QTextFragment, QGuiApplication)
from emojis.db import Emoji, get_emoji_by_alias, get_emoji_by_code

from extra_qwidgets.widgets.emoji_picker.emoji_image_provider import EmojiImageProvider



class QTwemojiTextDocument(QTextDocument):
    # Regex compilado estático para performance
    _EMOJI_PATTERN = R"(?:\x{1F3F4}(?:\x{E0067}\x{E0062}\x{E0065}\x{E006E}\x{E0067}|\x{E0067}\x{E0062}\x{E0073}\x{E0063}\x{E0074}|\x{E0067}\x{E0062}\x{E0077}\x{E006C}\x{E0073})\x{E007F})|(?:[\x{0030}-\x{0039}\x{0023}\x{002A}]\x{FE0F}?\x{20E3})|(?:[\x{1F1E6}-\x{1F1FF}]{2})|(?:\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?(?:\x{200D}\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?)*)"
    _ALIAS_PATTERN = R"(:\w+:)"

    def __init__(self, parent=None, twemoji=True, alias_replacement=True):
        super().__init__(parent)

        self._twemoji = False
        self._alias_replacement = False
        self._line_limit = 0

        # Variável para rastrear onde a edição ocorreu (Otimização B)
        self._last_change_pos = 0

        self.setTwemoji(twemoji)
        self.setAliasReplacement(alias_replacement)

        # Conecta o sinal 'Change' (antes do Changed) para capturar a posição
        self.contentsChange.connect(self._on_contents_change)

    # --- Configurações ---

    def lineLimit(self) -> int:
        return self._line_limit

    def setLineLimit(self, line_limit: int):
        self._line_limit = line_limit
        try:
            self.contentsChange.disconnect(self._limit_line)
        except RuntimeError:
            pass

        if line_limit > 0:
            self.contentsChange.connect(self._limit_line)

    def twemoji(self) -> bool:
        return self._twemoji

    def setTwemoji(self, value: bool):
        if self._twemoji == value:
            return

        self._twemoji = value

        if value:
            self.contentsChanged.connect(self._twemojize)
            # Na ativação inicial, processa o documento todo
            self._twemojize_full()
        else:
            try:
                self.contentsChanged.disconnect(self._twemojize)
            except RuntimeError:
                pass
            self._detwemojize()

    def aliasReplacement(self) -> bool:
        return self._alias_replacement

    def setAliasReplacement(self, value: bool):
        if self._alias_replacement == value:
            return

        self._alias_replacement = value

        if value:
            self.contentsChanged.connect(self._replace_alias)
            self._replace_alias()
        else:
            try:
                self.contentsChanged.disconnect(self._replace_alias)
            except RuntimeError:
                pass

    # --- Lógica Principal (Otimização B aplicada) ---

    def _on_contents_change(self, position, chars_removed, chars_added):
        """Captura a posição da mudança antes que ela seja processada."""
        self._last_change_pos = position

    def _ensure_resource_loaded(self, emoji: Emoji, size: int):
        """Lazy Loading via EmojiImageProvider."""
        if not emoji:
            return

        alias = emoji.aliases[0]
        url = QUrl(f"twemoji://{alias}")

        if self.resource(QTextDocument.ResourceType.ImageResource, url):
            return

        dpr = QGuiApplication.primaryScreen().devicePixelRatio()

        pixmap = EmojiImageProvider.get_pixmap(
            emoji_data=emoji,
            size=QSize(size, size),
            dpr=dpr
        )

        if not pixmap.isNull():
            self.addResource(QTextDocument.ResourceType.ImageResource, url, pixmap)

    def _twemojize(self):
        """
        Versão OTIMIZADA: Processa apenas o bloco (parágrafo) atual.
        Chamada automaticamente a cada alteração de texto.
        """
        # 1. Identifica o bloco onde a edição ocorreu
        block = self.findBlock(self._last_change_pos)
        if not block.isValid():
            return

        text = block.text()
        block_pos = block.position()

        # 2. Busca emojis apenas neste texto curto
        regex = QRegularExpression(self._EMOJI_PATTERN, QRegularExpression.PatternOption.UseUnicodePropertiesOption)
        iterator = regex.globalMatch(text)

        # 3. Coleta correspondências para processar de trás para frente
        # (Importante para não invalidar índices ao substituir texto por imagem)
        matches = []
        while iterator.hasNext():
            match = iterator.next()
            matches.append(match)

        if not matches:
            return

        cursor = QTextCursor(self)
        font_height = self._font_height(cursor)
        emoji_size = int(font_height * 0.9)

        # 4. Inicia bloco de edição para Undo/Redo atômico
        cursor.beginEditBlock()

        # Processa em ordem reversa (do fim da linha para o começo)
        for match in reversed(matches):
            start_rel = match.capturedStart(0)
            end_rel = match.capturedEnd(0)

            # Converte posição relativa do bloco para absoluta do documento
            abs_start = block_pos + start_rel
            abs_end = block_pos + end_rel

            cursor.setPosition(abs_start)
            cursor.setPosition(abs_end, QTextCursor.MoveMode.KeepAnchor)

            emoji_str = match.captured(0)
            emoji_without_color = self._remove_emoji_color(emoji_str)
            emoji_obj = get_emoji_by_code(emoji_without_color)

            if emoji_obj:
                self._ensure_resource_loaded(emoji_obj, emoji_size)
                image_fmt = self._emoji_to_text_image(emoji_obj, emoji_size)

                with QSignalBlocker(self):
                    cursor.insertImage(image_fmt)

        cursor.endEditBlock()

    def _twemojize_full(self):
        """Versão completa para uso na inicialização (scan total)."""
        cursor = QTextCursor(self)
        font_height = self._font_height(cursor)
        emoji_size = int(font_height * 0.9)

        # Usa a lógica antiga de escanear tudo (_localize_emojis retorna lista reversa)
        for emoji_str, start, end in self._localize_emojis():
            cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

            emoji_without_color = self._remove_emoji_color(emoji_str)
            emoji_obj = get_emoji_by_code(emoji_without_color)

            if emoji_obj:
                self._ensure_resource_loaded(emoji_obj, emoji_size)
                image_fmt = self._emoji_to_text_image(emoji_obj, emoji_size)

                with QSignalBlocker(self):
                    cursor.insertImage(image_fmt)

    def _replace_alias(self):
        """
        Substituição de alias (:smile:).
        Também poderia ser otimizado para _last_change_pos, mas alias é menos frequente.
        Mantido lógica global por segurança, ou pode-se aplicar a mesma lógica do _twemojize.
        """
        cursor = QTextCursor(self)
        font_height = self._font_height(cursor)
        emoji_size = int(font_height * 0.9)

        for emoji, start, end in self._localize_alias():
            cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

            if self._twemoji:
                self._ensure_resource_loaded(emoji, emoji_size)
                image_fmt = self._emoji_to_text_image(emoji, emoji_size)

                with QSignalBlocker(self):
                    cursor.removeSelectedText()
                    cursor.insertImage(image_fmt)
            else:
                with QSignalBlocker(self):
                    cursor.insertText(emoji.emoji)

    # --- Helpers e Utilitários ---

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

    def toText(self, cursor: QTextCursor = None) -> str:
        result = ""
        block = self.firstBlock()

        while block.isValid():
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()
                is_selected = True if not cursor else self._is_fragment_selected(cursor, frag)

                if frag.isValid() and is_selected:
                    char_format = frag.charFormat()
                    if char_format.isImageFormat():
                        image_format = char_format.toImageFormat()
                        if image_format.name().startswith("twemoji://"):
                            emoji = self._text_image_to_emoji(image_format)
                            if emoji:
                                result += emoji.emoji
                    else:
                        result += frag.text()
                it += 1
            if block != self.lastBlock():
                result += '\n'
            block = block.next()
        return result

    # --- Helpers de Regex e Cores ---

    def _localize_alias(self):
        regex = QRegularExpression(self._ALIAS_PATTERN)
        global_match = regex.globalMatch(self.toPlainText())
        matches = []
        while global_match.hasNext():
            match = global_match.next()
            words = match.captured(0)[1:-1]
            emoji = get_emoji_by_alias(words)
            if emoji:
                matches.insert(0, (emoji, match.capturedStart(0), match.capturedEnd(0)))
        return matches

    def _localize_emojis(self):
        # Usado apenas pelo _twemojize_full ou _detwemojize
        regex = QRegularExpression(self._EMOJI_PATTERN, QRegularExpression.PatternOption.UseUnicodePropertiesOption)
        iterator = regex.globalMatch(self.toPlainText())
        matches = []
        while iterator.hasNext():
            match = iterator.next()
            matches.insert(0, (match.captured(0), match.capturedStart(0), match.capturedEnd(0)))
        return matches

    def _localize_emoji_images(self):
        block = self.begin()
        emojis_images = []
        while block.isValid():
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()
                if frag.isValid() and frag.charFormat().isImageFormat():
                    img_fmt = frag.charFormat().toImageFormat()
                    if img_fmt.name().startswith("twemoji://"):
                        emojis_images.insert(0, (img_fmt, frag.position(), frag.position() + frag.length()))
                it += 1
            block = block.next()
        return emojis_images

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
        # Correção do iterador aplicada aqui também
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
    def _emoji_to_text_image(emoji: Emoji, height: int) -> QTextImageFormat:
        image = QTextImageFormat()
        if emoji and emoji.aliases:
            image.setName(f"twemoji://{emoji.aliases[0]}")
            image.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
            image.setHeight(height)
            image.setWidth(height)
            image.setQuality(100)
        return image

    @staticmethod
    def _text_image_to_emoji(image: QTextImageFormat) -> typing.Optional[Emoji]:
        name = image.name()
        if len(name) > 10:
            return get_emoji_by_alias(name[10:])
        return None

    @staticmethod
    def _is_fragment_selected(cursor: QTextCursor, fragment: QTextFragment) -> bool:
        if not cursor.hasSelection():
            return False
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        frag_start = fragment.position()
        frag_end = frag_start + fragment.length()
        return sel_end > frag_start and sel_start < frag_end