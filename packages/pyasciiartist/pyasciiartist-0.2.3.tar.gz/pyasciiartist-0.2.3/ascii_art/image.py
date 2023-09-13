# source.py

import os
import time
from typing import Union, Optional, Tuple
from pathlib import Path
import tempfile

import numpy as np
from PIL import Image, ImageEnhance

from ascii_magic import AsciiArt
from ascii_magic.constants import DEFAULT_STYLES

__all__ = [
    "image_to_ascii_art_html",
    "save_image",
    "save_html",
    "load_html",
    "load_image",
    "DEFAULT_QUALITY",
    "DEFAULT_COLOR",
    "wrap_html",
    "unwrap_html",
    "html_to_image",
    "image_ascii_art",
    "DEFAULT_COLOR_FACTOR",
    "DEFAULT_BRIGHTNESS_FACTOR",
    "numpy_to_pillow",
    "pillow_to_numpy"
]

DEFAULT_COLOR = True
DEFAULT_QUALITY = 90
DEFAULT_COLOR_FACTOR = 1.75
DEFAULT_BRIGHTNESS_FACTOR = 2

def pillow_to_numpy(image: Image.Image) -> np.ndarray:
    """
    Converts a pillow source object into a numpy source array.

    :param image: The source image.

    :return: The converted source.
    """

    # noinspection PyTypeChecker
    return np.array(image.convert("RGB"))
# end pillow_to_numpy

def numpy_to_pillow(image: np.ndarray) -> Image.Image:
    """
    Converts a numpy source array into a pillow source object.

    :param image: The source image.

    :return: The converted source.
    """

    return Image.fromarray(image)
# end numpy_to_pillow

def image_to_ascii_art_html(
        image: Union[Image.Image, np.ndarray],
        lines: Optional[int] = None,
        color: Optional[bool] = None
) -> str:
    """
    Generates an HTML string of ASCII art from a source pillow source object.

    :param image: The source image object or file path.
    :param lines: The amount of lines in the html string.
    :param color: The value to color the html.

    :return: The HTML string.
    """

    if isinstance(image, np.ndarray):
        image = numpy_to_pillow(image)
    # end if

    width, height = image.size

    if lines is None:
        lines = int(height / 6)
    # end if

    if color is None:
        color = DEFAULT_COLOR
    # end if

    art = AsciiArt.from_pillow_image(image)

    data = art.to_html(
        columns=lines,
        width_ratio=(
            (width / height)
            if (width > height) else
            (height / width)
        ),
        monochrome=not color
    )

    return wrap_html(data)
# end image_to_ascii_art_html_file

def wrap_html(html: str) -> str:
    """
    Wraps the html with the styling for the source.

    :param html: The html data.

    :return: The wrapped html data.
    """

    return f"""<!DOCTYPE html>
    <head>
        <title>ASCII art</title>
    </head>
    <body>
        <pre style="{DEFAULT_STYLES}">{html}</pre>
    </body>
    </html>"""
# end wrap_html

def unwrap_html(html: str) -> str:
    """
    Unwraps the html from the styling.

    :param html: The html data.

    :return: The unwrapped html data.
    """

    before = f"""<!DOCTYPE html>
    <head>
        <title>ASCII art</title>
    </head>
    <body>
        <pre style="{DEFAULT_STYLES}">"""

    after = f"""</pre>
    </body>
    </html>"""

    return html.strip(before).strip(after)
# end unwrap_html

def save_html(html: str, path: Union[str, Path]) -> None:
    """
    Saves the HTML data to the saving path.

    :param html: The HTML string.
    :param path: The saving path.
    """

    with open(str(path), "w") as file:
        file.write(html)
    # end open
# end save_html

def load_html(path: Union[str, Path]) -> str:
    """
    Loads the HTML data from the path.

    :param path: The saving path.

    :return: The HTML string.
    """

    with open(str(path), "r") as file:
        return file.read()
    # end open
# end load_html

def save_image(image: Union[Image.Image, np.ndarray], path: Union[str, Path]) -> None:
    """
    Saves the source data to the saving path.

    :param image: The source object.
    :param path: The saving path.
    """

    if path.endswith("npy") or isinstance(image, np.ndarray):
        if not isinstance(image, np.ndarray):
            image = np.array(image)
        # end if

        np.save(path[:path.find(".")], image)

    else:
        if not path.endswith(".png"):
            image = image.convert("RGB")
        # end if

        image.save(str(path))
    # end if
# end save_image

def load_image(path: Union[str, Path]) -> Union[Image.Image, np.ndarray]:
    """
    Loads the source data from the path.

    :param path: The saving path.

    :return: The source object.
    """

    if str(path).endswith(".npy"):
        return Image.fromarray(
            np.load(str(path), allow_pickle=True).astype('uint8'),
            'RGB'
        )

    else:
        return Image.open(str(path))
    # end if
# end load_image

def html_to_image(
        html: str,
        size: Optional[Tuple[int, int]] = None,
        quality: Optional[int] = None,
        brightness_factor: Optional[float] = None,
        color_factor: Optional[float] = None
) -> Image.Image:
    """
    Generates an image from the html.

    :param html: The HTML string.
    :param size: The size to crop the source to.
    :param quality: The quality of the source.
    :param brightness_factor: The brightness factor to scale the source.
    :param color_factor: The color factor to scale the source.

    :return: The generated source object.
    """

    if quality is None:
        quality = DEFAULT_QUALITY
    # end if

    if brightness_factor is None:
        brightness_factor = DEFAULT_BRIGHTNESS_FACTOR
    # end if

    if color_factor is None:
        color_factor = DEFAULT_COLOR_FACTOR
    # end if

    quality = int(quality)

    if not (1 <= quality <= 100):
        raise ValueError(
            f"Quality must be an int between "
            f"{1} and {100} or equal to them, not: {quality}."
        )
    # end if

    location = tempfile.TemporaryDirectory().name

    os.makedirs(location, exist_ok=True)

    with open(str(Path(location) / Path('data.html')), "w") as html_file:
        html_path = html_file.name

        html_file.write(html)
    # end TemporaryFile

    image_path = Path(location) / Path("data.png")

    os.system(
        " ".join(
            [
                'wkhtmltoimage',
                '--quality', str(quality),
                '--quiet',
                str(html_path),
                str(image_path)
            ]
        )
    )

    while not os.path.exists(image_path):
        time.sleep(0.0001)
    # end while

    image = Image.open(image_path)

    if brightness_factor != 1:
        current_brightness = ImageEnhance.Brightness(image)
        image = current_brightness.enhance(brightness_factor)
    # end if

    if color_factor != 1:
        current_color = ImageEnhance.Color(image)
        image = current_color.enhance(color_factor)
    # end if

    if size is not None:
        image = image.resize(
            (int(image.width * size[1] / image.height), size[1])
        )

        ud_diff = image.height - size[1]

        x0 = ud_diff // 2
        y0 = ud_diff // 2
        x1 = size[0] - x0
        y1 = size[1] - y0

        image = image.crop((x0, y0, x1, y1))
    # end if

    return image
# end html_to_image

def image_ascii_art(
        source: Optional[Union[str, Path, Image.Image]] = None,
        html: Optional[Union[str, Path]] = None,
        lines: Optional[int] = None,
        color: Optional[bool] = None,
        quality: Optional[int] = None,
        brightness_factor: Optional[float] = None,
        color_factor: Optional[float] = None,
        html_destination: Optional[Union[str, Path]] = None,
        destination: Optional[Union[str, Path]] = None,
) -> None:
    """
    Generate an ASCII ark source from a source image or HTML file.

    :param source: The source image object or file path.
    :param html: The html file path or data.
    :param lines: The amount of lines in the html string.
    :param color: The value to color the html.
    :param quality: The quality of the source.
    :param brightness_factor: The brightness factor to scale the source.
    :param color_factor: The color factor to scale the source.
    :param html_destination: The path to save the html data in.
    :param destination: The path to save the generated source data in.
    """

    if (html, source) == (None, None):
        raise ValueError("At least one of html or source must be defined.")
    # end if

    if html is None:
        if isinstance(source, (str, Path)):
            source = load_image(str(source))
        # end if

        html = image_to_ascii_art_html(
            image=source, lines=lines, color=color
        )
    # end if

    if isinstance(html, Path) or (isinstance(html, str) and Path(html).exists()):
        html = load_html(html)
    # end if

    art_image = html_to_image(
        html=html,
        quality=quality,
        brightness_factor=brightness_factor,
        color_factor=color_factor,
        size=(source.width, source.height)
    )

    if html_destination is not None:
        save_html(html=html, path=html_destination)
    # end if

    if destination is not None:
        save_image(image=art_image, path=destination)
    # end if
# end image_ascii_art