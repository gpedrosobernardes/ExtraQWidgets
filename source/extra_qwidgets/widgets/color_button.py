import typing

from PySide6.QtWidgets import QPushButton, QStyleOptionButton, QStyle
from PySide6.QtGui import QPalette, QColor


class QColorButton(QPushButton):
    def __init__(self, text, color, text_color = "auto", parent = None):
        super().__init__(text, parent)

        # Guardamos as cores como atributos da classe
        self._color = None
        self._text_color = None

        self.setColor(color)
        self.setTextColor(text_color)

        # Configuração visual inicial
        self.setAutoFillBackground(True)

    def initStyleOption(self, option: QStyleOptionButton):
        """
        Método chamado automaticamente pelo Qt antes de desenhar o botão.
        Aqui interceptamos a opção de estilo e trocamos a cor da paleta
        baseado no estado atual (Hover, Pressed, etc).
        """
        # 1. Deixa o QPushButton preencher a option com o estado padrão
        super().initStyleOption(option)

        state: QStyle.StateFlag = getattr(option, 'state')
        palette: QPalette = getattr(option, 'palette')

        # 2. Verifica o estado no objeto 'option' e altera a cor da paleta localmente
        if state & QStyle.StateFlag.State_Sunken:  # Pressionado
            pressed_color = self._color.darker(115)  # 15% mais escuro
            palette.setColor(QPalette.ColorRole.Button, pressed_color)
            palette.setColor(QPalette.ColorRole.Window, pressed_color)  # Para preenchimento de fundo

        elif state & QStyle.StateFlag.State_MouseOver:  # Mouse em cima
            hover_color = self._color.lighter(115)  # 15% mais claro
            palette.setColor(QPalette.ColorRole.Button, hover_color)
            palette.setColor(QPalette.ColorRole.Window, hover_color)

        else:  # Estado Normal
            palette.setColor(QPalette.ColorRole.Button, self._color)
            palette.setColor(QPalette.ColorRole.Window, self._color)

        if self._text_color == "auto":
            palette.setColor(QPalette.ColorRole.ButtonText, self.getContrastingTextColor(self._color))

        else:
            palette.setColor(QPalette.ColorRole.ButtonText, self._text_color)

    def color(self) -> QColor:
        return self._color

    def setColor(self, color):
        if isinstance(color, str):
            self._color = QColor(color)

        elif isinstance(color, QColor):
            self._color = color

    def textColor(self) -> typing.Union[str, QColor]:
        return self._text_color

    def setTextColor(self, text_color):
        if isinstance(text_color, str):
            if text_color == "auto":
                self._text_color = text_color

            else:
                self._text_color = QColor(text_color)

        elif isinstance(text_color, QColor):
            self._text_color = text_color

    @staticmethod
    def getContrastingTextColor(bg_color: QColor) -> QColor:
        """
        Retorna Qt.black ou Qt.white dependendo da luminância da cor de fundo.
        Fórmula baseada na percepção humana (NTSC conversion formula).
        """
        r = bg_color.red()
        g = bg_color.green()
        b = bg_color.blue()

        # Calculamos o brilho ponderado
        # 0.299R + 0.587G + 0.114B
        luminance = (0.299 * r) + (0.587 * g) + (0.114 * b)

        # O limiar comum é 128 (metade de 255).
        # Se for mais brilhante que 128, o fundo é claro -> Texto Preto
        # Se for mais escuro, o fundo é escuro -> Texto Branco
        return QColor("black") if luminance > 128 else QColor("white")

