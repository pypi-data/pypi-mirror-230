_PREFIX = "\033["
_RESET = f"{_PREFIX}0m"


class Colors:
    black = "30"
    red = "31"
    green = "32"
    yellow = "33"
    blue = "34"
    magenta = "35"
    cyan = "36"
    white = "37"


class Modifiers:
    bold = "1"
    dim = "2"
    italic = "3"
    underline = "4"
    flash = "5"
    invert = "7"
    strikethrough = "9"
    highlight_grey = "40"
    highlight_red = "41"
    highlight_green = "42"
    highlight_yellow = "43"
    highlight_blue = "44"
    highlight_purple = "45"
    highlight_cyan = "46"
    highlight_white = "47"


def colored_text(text: str, *modifiers: str) -> str:
    all_modifiers: list[str] = list(modifiers) or [Colors.white]
    return f"{_PREFIX}{';'.join(all_modifiers)}m{text}{_RESET}"
