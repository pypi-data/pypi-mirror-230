from os import path, listdir
import magic


class ExtractSVG:
    __svg_mimetype = "image/svg+xml"

    def __init__(self, svg_in: str) -> None:
        if not path.exists(svg_in):
            raise Exception(f"{svg_in} does not exist.")
        self.__svg_in = svg_in
        self.__mobj = magic.Magic(mime=True)

    def check_svg(self, file: str, ex: bool = True) -> bool:
        mimetype: str = str(self.__mobj.from_file(file))  # type: ignore
        if mimetype != ExtractSVG.__svg_mimetype:
            if ex:
                raise Exception(f"{file} is not an SVG file.")
            return False
        return True

    def extract_single(self) -> str:
        if path.isdir(self.__svg_in):
            raise Exception(f"{self.__svg_in} is a directory.")
        self.check_svg(self.__svg_in)
        return "".join(open(self.__svg_in, "r").readlines())

    def extract_batch(self) -> dict[str, str]:
        if not path.isdir(self.__svg_in):
            raise Exception(f"{self.__svg_in} is not a directory.")
        svgs = listdir(self.__svg_in)
        extracted_svgs: dict[str, str] = {}
        for svg_name in svgs:
            svg = f"{self.__svg_in}/{svg_name}"
            is_svg = self.check_svg(svg, ex=False)
            if is_svg:
                text = ExtractSVG(svg).extract_single()
                extracted_svgs.update({svg: text})
        return extracted_svgs


class WriteSVG:
    def __init__(self, out_svg: str) -> None:
        self.__out_svg = out_svg

    def write_single(self, text: str):
        if path.isdir(self.__out_svg):
            raise Exception(f"{self.__out_svg} is a directory.")
        open(self.__out_svg, "w").write(text)

    def write_batch(self, svg_dict: dict[str, str]):
        if not path.exists(self.__out_svg):
            raise Exception(f"{self.__out_svg} does not exist.")
        if not path.isdir(self.__out_svg):
            raise Exception(f"{self.__out_svg} is not a directory.")
        for svg, text in svg_dict.items():
            if not path.exists(svg):
                raise Exception(f"{svg} does not exist.")
            if path.isdir(svg):
                raise Exception(f"{svg} is a directory.")
            svg_name = path.basename(svg)
            open(f"{self.__out_svg}/{svg_name}", "w").write(text)
