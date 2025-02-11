from pathlib import Path

from emojis.db import Emoji


def emoji_to_code_point(emoji: Emoji):
    delimiter = "-"
    # Convert the string into a list of UTF-16 code units
    code_units = [ord(char) for char in emoji.emoji]

    # Process the code units in pairs (high surrogate + low surrogate)
    code_points = []
    i = 0
    while i < len(code_units):
        high_surrogate = code_units[i]
        low_surrogate = code_units[i + 1] if i + 1 < len(code_units) else None

        # Check if the current pair is a valid surrogate pair
        if 0xD800 <= high_surrogate <= 0xDBFF and 0xDC00 <= low_surrogate <= 0xDFFF:
            # Calculate the code point
            code_point = (
                    ((high_surrogate - 0xD800) << 10)
                    + (low_surrogate - 0xDC00)
                    + 0x10000
            )
            code_points.append(hex(code_point)[2:])  # Remove the '0x' prefix
            i += 2  # Move to the next pair
        else:
            # If not a surrogate pair, treat it as a regular code point
            code_points.append(hex(high_surrogate)[2:])
            i += 1

    # Join the code points with the specified delimiter
    return delimiter.join(code_points)


def get_emoji_path(emoji: Emoji) -> str:
    file_name = emoji_to_code_point(emoji)
    path = Path(__file__).parent.parent.parent.absolute() / f"assets/emojis/{file_name}.png"
    if path.exists():
        return str(path)
    else:
        file_name = "-".join(file_name.split("-")[:-1])
        path = Path(__file__).parent.parent.parent.absolute() / f"assets/emojis/{file_name}.png"
        return str(path)