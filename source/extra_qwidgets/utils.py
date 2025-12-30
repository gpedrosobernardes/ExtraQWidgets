import typing

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPainter, QPixmap, QColor, Qt, QImage
from PySide6.QtWidgets import QApplication


def is_dark_mode() -> bool:
    style_hints = QApplication.styleHints()
    color_scheme = style_hints.colorScheme()
    return color_scheme.value == 2


def colorize_pixmap(pixmap: QPixmap, color: str) -> QPixmap:
    # Create a new QPixmap with the same size and fill it with transparent color
    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.GlobalColor.transparent)

    # Paint the original pixmap onto the new pixmap with the desired color
    painter = QPainter(colored_pixmap)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(colored_pixmap.rect(), QColor(color))
    painter.end()

    # Convert the colored QPixmap back to QIcon
    return colored_pixmap


def get_all_pixmap_from_icon(icon: QIcon, size: QSize = QSize(64, 64)) -> typing.Dict[typing.Tuple[QIcon.Mode, QIcon.State], QPixmap]:
    modes = [QIcon.Mode.Normal, QIcon.Mode.Disabled, QIcon.Mode.Active, QIcon.Mode.Selected]
    states = [QIcon.State.Off, QIcon.State.On]
    all_pixmap = {}
    for mode in modes:
        for state in states:
            pixmap = icon.pixmap(size, mode, state)
            if not pixmap.isNull():
                key = (mode, state)
                all_pixmap[key] = pixmap
    return all_pixmap


def colorize_icon(icon: QIcon, color: str, size: QSize = QSize(64, 64)) -> QIcon:
    new_icon = QIcon()
    for key, value in get_all_pixmap_from_icon(icon, size).items():
        mode, state = key
        pixmap = icon.pixmap(size, mode, state)
        new_icon.addPixmap(colorize_pixmap(pixmap, color), mode, state)
    return new_icon


def colorize_icon_by_theme(icon: QIcon, size: QSize = QSize(64, 64)) -> QIcon:
    color = "#FFFFFF" if is_dark_mode() else "#000000"
    return colorize_icon(icon, color, size)


def scale_inside(image: QImage, factor: float) -> QImage:
    # tamanho final (igual ao original)
    w, h = image.width(), image.height()

    # cria imagem com o mesmo tamanho, mas transparente
    out = QImage(w, h, QImage.Format.Format_ARGB32)

    out.fill(Qt.GlobalColor.transparent)

    # calcula tamanho reduzido
    new_w = int(w * factor)
    new_h = int(h * factor)

    # calcula posição para centralizar
    x = (w - new_w) // 2
    y = (h - new_h) // 2

    # desenha imagem menor dentro da maior
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    p.drawImage(x, y, image.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    p.end()

    return out