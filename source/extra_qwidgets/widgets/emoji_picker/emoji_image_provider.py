from emojis.db import Emoji
from twemoji_api.api import get_emoji_path
from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QPixmapCache, QImageReader, Qt


class EmojiImageProvider:
    """
    Class exclusively responsible for loading, resizing, and caching
    emoji images.
    """

    @staticmethod
    def get_pixmap(emoji_data: Emoji, size: QSize, dpr: float = 1.0) -> QPixmap:
        """
        Returns a QPixmap ready to be drawn.

        :param emoji_data: Object containing the emoji path or code.
        :param size: Desired QSize (logical size).
        :param dpr: Device Pixel Ratio (for Retina/4K screens).
        """

        # 1. Calculate real physical size (pixels)
        target_width = int(size.width() * dpr)
        target_height = int(size.height() * dpr)

        # 2. Generate unique key for Cache
        # Ex: "emoji_1f600_64x64"
        emoji_alias = emoji_data[0][0]
        cache_key = f"emoji_{emoji_alias}"

        # 3. Try to fetch from Cache
        pixmap = QPixmap()
        if QPixmapCache.find(cache_key, pixmap):
            return pixmap

        # --- CACHE MISS (Load from disk) ---

        # 4. Load using QImageReader (more efficient than QPixmap(path))
        emoji_path = str(get_emoji_path(emoji_data[1]))
        reader = QImageReader(emoji_path)

        if reader.canRead():
            # Important for SVG: Define render size before reading
            reader.setScaledSize(QSize(target_width, target_height))

            image = reader.read()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                pixmap.setDevicePixelRatio(dpr)

                # Save to cache for future
                QPixmapCache.insert(cache_key, pixmap)
                return pixmap

        # 5. Fallback (Returns a transparent pixmap or placeholder in case of error)
        fallback = QPixmap(size * dpr)
        fallback.fill(Qt.GlobalColor.transparent)
        fallback.setDevicePixelRatio(dpr)
        return fallback
