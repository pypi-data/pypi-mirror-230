__BLUE_DEFAULT = "#3584e4"
__BLUE_ACCENT = "#99c1f1"
__GREEN_DEFAULT = "#33d17a"
__GREEN_ACCENT = "#8ff0a4"
__YELLOW_DEFAULT = "#f6d32d"
__YELLOW_ACCENT = "#f9f06b"
__ORANGE_DEFAULT = "#ff7800"
__ORANGE_ACCENT = "#ffbe6f"
__RED_DEFAULT = "#e01b24"
__RED_ACCENT = "#f66151"
__PURPLE_DEFAULT = "#9141ac"
__PURPLE_ACCENT = "#dc8add"
__BROWN_DEFAULT = "#986a44"
__BROWN_ACCENT = "#cdab8f"
__LIGHT_DEFAULT = "#deddda"
__LIGHT_ACCENT = "#fefefe"
__DARK_DEFAULT = "#3d3846"
__DARK_ACCENT = "#77767b"

PRIMARY: list[str] = ["#00ff00", "#00FF00"]
SECONDARY: list[str] = ["#0000ff", "#0000FF"]
BACKGROUND: list[str] = ["#ff0000", "#FF0000"]
DETAIL: list[str] = ["#ffffff", "#FFFFFF"]
INVERSE_BG: list[str] = ["#000000"]

DEFAULTS: dict[str, str] = {
    "default": __BLUE_DEFAULT,
    "accent": __BLUE_ACCENT,
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
    "blue": {"default": __BLUE_DEFAULT, "accent": __BLUE_ACCENT},
    "green": {"default": __GREEN_DEFAULT, "accent": __GREEN_ACCENT},
    "yellow": {"default": __YELLOW_DEFAULT, "accent": __YELLOW_ACCENT},
    "orange": {"default": __ORANGE_DEFAULT, "accent": __ORANGE_ACCENT},
    "red": {"default": __RED_DEFAULT, "accent": __RED_ACCENT},
    "purple": {"default": __PURPLE_DEFAULT, "accent": __PURPLE_ACCENT},
    "brown": {"default": __BROWN_DEFAULT, "accent": __BROWN_ACCENT},
    "light": {"default": __LIGHT_DEFAULT, "accent": __LIGHT_ACCENT},
    "dark": {"default": __DARK_DEFAULT, "accent": __DARK_ACCENT},
}
