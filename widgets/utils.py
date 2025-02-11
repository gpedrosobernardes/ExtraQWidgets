from pathlib import Path
from PySide6.QtGui import QIcon


def get_icon(icon_name: str) -> QIcon:
    icons_folder = Path(__file__).parent.parent.absolute() / "assets/icons"
    fullpath = icons_folder / icon_name
    return QIcon(str(fullpath))
