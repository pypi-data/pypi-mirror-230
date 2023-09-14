from . import DEFAULTS, SCHEMES, INVERSE_SCHEMES, COLORS


class Colors:
    _default_colors = DEFAULTS
    _scheme_colors = SCHEMES
    _inverse_scheme_colors = INVERSE_SCHEMES
    _colors = COLORS

    def __init__(self) -> None:
        self._scheme_variants = list(self._scheme_colors.keys())
        self._color_list = list(self._colors.keys())

    def get_defaults(self) -> list[str]:
        """get default values

        Returns:
            list[str]: [default, accent, variant, alt, difference]
        """
        return list(Colors._default_colors.values())

    def get_scheme_variants(self) -> list[str]:
        """get available scheme variants

        Returns:
            list[str]: ["dark", "light", ...]
        """
        return self._scheme_variants

    def get_colors_list(self) -> list[str]:
        """get list of supported colors

        Returns:
            list[str]: ["red", "green", "blue", ... ]
        """
        return self._color_list

    def select_scheme(self, scheme: str, inverse: bool = False) -> tuple[str, str, str]:
        """get selected scheme values

        Args:
            scheme (str): selected scheme ("dark" | "light" | ...)
            inverse (bool, optional): invert the scheme colors. defaults to False.

        Raises:
            Exception: selected scheme is not in the colors dict.
            Exception: one of the values for the selected scheme is missing.

        Returns:
            tuple[str, str, str]: (variant, alt, difference)
        """
        variants = Colors._scheme_colors.get(scheme)
        if inverse:
            variants = Colors._inverse_scheme_colors.get(scheme)
        if not variants:
            raise Exception(f"invalid scheme.\nchoose from {self._scheme_variants}")
        variant = variants.get("variant")
        alt = variants.get("alt")
        difference = variants.get("difference")
        if not all((variant, alt, difference)):
            raise Exception(
                f"scheme error, variant: {variant}, alt: {alt}, difference: {difference}"
            )
        return variant, alt, difference  # type: ignore

    def select_color(self, color: str) -> tuple[str, str]:
        """get selected color values

        Args:
            color (str): selected color ("red" | "green" | "blue" | ...)

        Raises:
            Exception: selected color is not in the colors dict.
            Exception: one of the values for the selected color is missing.

        Returns:
            tuple[str, str]: [default, accent]
        """
        pair = Colors._colors.get(color)
        if not pair:
            raise Exception(f"invalid color.\nchoose from {self._color_list}")
        default = pair.get("default")
        accent = pair.get("accent")
        if default is None or accent is None:
            raise Exception(f"color error, default: {default}, accent: {accent}")
        return default, accent
