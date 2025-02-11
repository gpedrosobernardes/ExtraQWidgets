from pathlib import Path
from PySide6.QtGui import QIcon


def get_icon(icon_name: str) -> QIcon:
    icons_folder = Path(__file__).parent.parent.absolute() / "assets/icons"
    fullpath = icons_folder / icon_name
    return QIcon(str(fullpath))


def adjust_brightness(hex_color: str, percentage: float = 10) -> str:
    """
    Ajusta o brilho de uma cor hexadecimal.

    Args:
        hex_color (str): Cor no formato hexadecimal (e.g., '#RRGGBB').
        percentage (float): Porcentagem para ajustar o brilho (positivo para mais brilho, negativo para menos).

    Returns:
        str: Nova cor no formato hexadecimal com o brilho ajustado.
    """
    # Remover o símbolo '#' se presente
    hex_color = hex_color.lstrip("#")

    # Converter o hexadecimal para valores RGB
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Calcular o fator de ajuste
    factor = 1 + (percentage / 100)

    # Aplicar o ajuste e garantir que os valores fiquem no intervalo [0, 255]
    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))

    # Converter de volta para hexadecimal
    return f"#{r:02X}{g:02X}{b:02X}"