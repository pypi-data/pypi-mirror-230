__BLUE_DEFAULT = "#1a5fb4"
__BLUE_ACCENT = "#99c1f1"
__GREEN_DEFAULT = "#26a269"
__GREEN_ACCENT = "#8ff0a4"
__YELLOW_DEFAULT = "#e5a50a"
__YELLOW_ACCENT = "#f9f06b"
__ORANGE_DEFAULT = "#c64600"
__ORANGE_ACCENT = "#ffbe6f"
__RED_DEFAULT = "#a51d2d"
__RED_ACCENT = "#f66151"
__PURPLE_DEFAULT = "#613583"
__PURPLE_ACCENT = "#dc8add"
__BROWN_DEFAULT = "#63452c"
__BROWN_ACCENT = "#cdab8f"
__WHITE_DEFAULT = "#9a9996"
__WHITE_ACCENT = "#fefefe"
__BLACK_DEFAULT = "#010101"
__BLACK_ACCENT = "#77767b"

__DEFAULT_COLOR = "#3584e4"
__DEFAULT_ACCENT = "#99c1f1"
__LIGHT_DEFAULT = "#c0bfbc"
__LIGHT_ACCENT = "#f6f5f4"
__DARK_DEFAULT = "#241f31"
__DARK_ACCENT = "#5e5c64"

PRIMARY: list[str] = ["#00ff00", "#00FF00"]
SECONDARY: list[str] = ["#0000ff", "#0000FF"]
BACKGROUND: list[str] = ["#ff0000", "#FF0000"]
DETAIL: list[str] = ["#ffffff", "#FFFFFF"]
INVERSE_BG: list[str] = ["#000000"]

DEFAULTS: dict[str, str] = {
    "default": __DEFAULT_COLOR,
    "accent": __DEFAULT_ACCENT,
    "variant": __LIGHT_DEFAULT,
    "alt": __LIGHT_ACCENT,
    "difference": __DARK_DEFAULT,
}
SCHEMES: dict[str, dict[str, str]] = {
    "dark": {
        "variant": __LIGHT_DEFAULT,
        "alt": __LIGHT_ACCENT,
        "difference": __DARK_DEFAULT,
    },
    "light": {
        "variant": __DARK_DEFAULT,
        "alt": __DARK_ACCENT,
        "difference": __LIGHT_DEFAULT,
    },
}
INVERSE_SCHEMES: dict[str, dict[str, str]] = {
    "dark": {
        "variant": __DARK_DEFAULT,
        "alt": __DARK_ACCENT,
        "difference": __LIGHT_DEFAULT,
    },
    "light": {
        "variant": __LIGHT_DEFAULT,
        "alt": __LIGHT_ACCENT,
        "difference": __DARK_DEFAULT,
    },
}
COLORS: dict[str, dict[str, str]] = {
    "default": {"default": __DEFAULT_COLOR, "accent": __DEFAULT_ACCENT},
    "blue": {"default": __BLUE_DEFAULT, "accent": __BLUE_ACCENT},
    "green": {"default": __GREEN_DEFAULT, "accent": __GREEN_ACCENT},
    "yellow": {"default": __YELLOW_DEFAULT, "accent": __YELLOW_ACCENT},
    "orange": {"default": __ORANGE_DEFAULT, "accent": __ORANGE_ACCENT},
    "red": {"default": __RED_DEFAULT, "accent": __RED_ACCENT},
    "purple": {"default": __PURPLE_DEFAULT, "accent": __PURPLE_ACCENT},
    "brown": {"default": __BROWN_DEFAULT, "accent": __BROWN_ACCENT},
    "white": {"default": __WHITE_DEFAULT, "accent": __WHITE_ACCENT},
    "black": {"default": __BLACK_DEFAULT, "accent": __BLACK_ACCENT},
}
