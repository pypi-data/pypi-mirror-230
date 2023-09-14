from . import PRIMARY, SECONDARY, BACKGROUND, DETAIL, INVERSE_BG


class Tint:
    """this is only here to make the process more modular
    use `PyTint().tint_svg()` instead.
    """

    def __init__(self, svg_in: str) -> None:
        self.__primary = PRIMARY
        self.__secondary = SECONDARY
        self.__background = BACKGROUND
        self.__detail = DETAIL
        self.__inverse_background = INVERSE_BG
        self.__svg_in = svg_in

    def get_svg(self) -> str:
        return self.__svg_in

    def tint_colors(self, default: str, accent: str):
        for color in self.__primary:
            self.__svg_in = self.__svg_in.replace(color, default)
        for color in self.__secondary:
            self.__svg_in = self.__svg_in.replace(color, accent)

    def tint_scheme(self, variant: str, alt: str, difference: str):
        for scheme in self.__background:
            self.__svg_in = self.__svg_in.replace(scheme, variant)
        for scheme in self.__detail:
            self.__svg_in = self.__svg_in.replace(scheme, alt)
        for scheme in self.__inverse_background:
            self.__svg_in = self.__svg_in.replace(scheme, difference)


class BatchTint:
    """this is only here to make the process more modular
    use `PyTint().tint_batch()` instead.
    """

    def __init__(self, svg_dict: dict[str, str]) -> None:
        self.__svg_dict = svg_dict

    def get_svg_dict(self) -> dict[str, str]:
        return self.__svg_dict

    def tint_colors(self, default: str, accent: str):
        new_dict: dict[str, str] = {}
        for svg in self.__svg_dict:
            text = self.__svg_dict.get(svg)
            if not (text and text.strip()):
                raise Exception(f"svg data for '{svg}' not found, could be empty file")
            svg_tint = Tint(text)
            svg_tint.tint_colors(default, accent)
            color_text = svg_tint.get_svg()
            new_dict.update({svg: color_text})
        self.__svg_dict = new_dict

    def tint_scheme(self, variant: str, alt: str, difference: str):
        new_dict: dict[str, str] = {}
        for svg in self.__svg_dict:
            text = self.__svg_dict.get(svg)
            if not (text and text.strip()):
                raise Exception(f"svg data for '{svg}' not found, could be empty file")
            svg_tint = Tint(text)
            svg_tint.tint_scheme(variant, alt, difference)
            scheme_text = svg_tint.get_svg()
            new_dict.update({svg: scheme_text})
        self.__svg_dict = new_dict
