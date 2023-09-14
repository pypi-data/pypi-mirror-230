from .colors import Colors
from .tint import Tint, BatchTint
from .svg_tool import ExtractSVG, WriteSVG


class PyTint:
    def __init__(self, color: str, scheme: str, inverse_scheme: bool = False) -> None:
        """create a PyTint instance

        Args:
            color (str): selected color ("red" | "green" | "blue" | ...)
            scheme (str): selected scheme ("dark" | "light" | ...)
            inverse_scheme (bool, optional): invert the scheme colors. defaults to False.
        """
        self.__cols = Colors()
        self.__default, self.__accent = self.__cols.select_color(color)
        self.__variant, self.__alt, self.__difference = self.__cols.select_scheme(
            scheme, inverse=inverse_scheme
        )

    def tint_svg(self, svg_in: str, svg_out: str):
        """colorize single svg

        Args:
            svg_in (str): full path to the svg blueprint file, e.g: '/home/user/blueprints/blueprint.svg'
            svg_out (str): full path to output file, e.g: '/home/user/.icons/mytheme/new_icon.svg'
        output file doesn't have to exist.
        """
        svg = ExtractSVG(svg_in).extract_single()
        tnt = Tint(svg)
        tnt.tint_colors(self.__default, self.__accent)
        tnt.tint_scheme(self.__variant, self.__alt, self.__difference)
        svg = tnt.get_svg()
        WriteSVG(svg_out).write_single(svg)

    def tint_batch(self, svg_dir: str, out_dir: str):
        """colorize all svgs in a directory

        Args:
            svg_dir (str): full path to the blueprints directory, e.g: '/home/user/blueprints'
            out_dir (str): full path to the output directory, e.g: '/home/user/.icons/mytheme'
        both directories must exist.
        """
        svgs = ExtractSVG(svg_dir).extract_batch()
        tnt = BatchTint(svgs)
        tnt.tint_colors(self.__default, self.__accent)
        tnt.tint_scheme(self.__variant, self.__alt, self.__difference)
        svg_dict = tnt.get_svg_dict()
        WriteSVG(out_dir).write_batch(svg_dict)
