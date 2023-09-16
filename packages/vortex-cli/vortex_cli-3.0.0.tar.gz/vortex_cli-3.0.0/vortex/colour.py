from __future__ import annotations

from enum import Enum


class Colour(Enum):
    NORMAL = "\033[m"
    RED = "\033[41m"
    BOLD = "\033[1m"
    GREEN = "\033[42m"
    YELLOW = "\033[43;30m"

    @staticmethod
    def highlight(text: str, colour: Colour, replace_in: str | None = None) -> str:
        highlighted_txt = f"{colour.value}{text}{Colour.NORMAL.value}"
        if replace_in:
            highlighted_txt = replace_in.replace(text, highlighted_txt)
        return highlighted_txt
