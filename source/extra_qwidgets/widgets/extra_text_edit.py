from PySide6.QtCore import QMimeData, QSize, Qt
from PySide6.QtWidgets import QTextEdit, QSizePolicy

# Certifique-se que o import está correto para o seu projeto
from extra_qwidgets.documents.twemoji_text_document import QTwemojiTextDocument


class QExtraTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuração do Documento
        self.setDocument(QTwemojiTextDocument(self))

        # Variáveis Privadas
        self._max_height = 16777215  # QWIDGETSIZE_MAX (Padrão do Qt)
        self._responsive = False

        # Inicialização
        self.setResponsive(True)

        # Ajuste de Política de Tamanho
        # Para um widget que cresce, 'Minimum' ou 'Preferred' na vertical é melhor que 'Expanding'
        size_policy = self.sizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.setSizePolicy(size_policy)

    # --- Overrides do Sistema Qt ---

    def sizeHint(self) -> QSize:
        """
        Informa ao layout qual o tamanho ideal do widget neste momento.
        """
        if self._responsive and self.document():
            # 1. Calcula a altura do conteúdo real
            doc_height = self.document().size().height()

            # 2. Soma as margens internas e bordas do frame
            # frameWidth() cobre as bordas desenhadas pelo estilo
            margins = self.contentsMargins()
            frame_borders = self.frameWidth() * 2

            total_height = doc_height + margins.top() + margins.bottom() + frame_borders

            # 3. Limita à altura máxima definida
            final_height = min(total_height, self._max_height)

            return QSize(super().sizeHint().width(), int(final_height))

        return super().sizeHint()

    def createMimeDataFromSelection(self) -> QMimeData:
        """Preserva os emojis customizados ao copiar/arrastar."""
        document: QTwemojiTextDocument = self.document()
        custom_text = document.toText(self.textCursor())

        new_mime_data = QMimeData()
        new_mime_data.setText(custom_text)
        return new_mime_data

    # --- Getters e Setters ---

    def responsive(self) -> bool:
        return self._responsive

    def setResponsive(self, responsive: bool = True):
        if self._responsive == responsive:
            return

        self._responsive = responsive

        if responsive:
            self.textChanged.connect(self._on_text_changed)
            # Remove a política de scroll automático padrão para gerenciarmos manualmente
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._on_text_changed()  # Força ajuste inicial
        else:
            try:
                self.textChanged.disconnect(self._on_text_changed)
            except RuntimeError:
                pass

            # Restaura comportamento padrão
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.updateGeometry()

    def maximumHeight(self) -> int:
        return self._max_height

    def setMaximumHeight(self, height: int):
        self._max_height = height
        # Não chamamos super().setMaximumHeight aqui para não travar o widget visualmente
        # A restrição é aplicada logicamente no sizeHint
        self.updateGeometry()

    # --- Lógica Interna ---

    def _on_text_changed(self):
        """Chamado quando o texto muda para recalcular a geometria."""
        if not self._responsive:
            return

        # 1. Avisa o layout que o tamanho ideal mudou
        self.updateGeometry()

        # 2. Gerencia a visibilidade da ScrollBar
        # Se o conteúdo for maior que o limite máximo, precisamos da scrollbar
        doc_height = self.document().size().height()
        content_margins = self.contentsMargins().top() + self.contentsMargins().bottom() + (self.frameWidth() * 2)

        if (doc_height + content_margins) > self._max_height:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)