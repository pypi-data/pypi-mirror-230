import numexpr
import cv2
import numpy as np
from math import ceil
from a_cv_imwrite_imread_plus import open_image_in_cv


def to_ascii(img, width=250, height_adjust_stretch=3, letters="█║▓▒░| "):
    """
    Convert an image to ASCII art.

    Parameters:
        img (str or numpy.ndarray): url/path/base64/bin/np.array/PIL.Image representing an image.
        width (int): Width of the ASCII art output.
        height_adjust_stretch (float): Vertical stretch factor for the ASCII art.
        letters (str): The set of characters to use for varying shades in the ASCII art.

    Returns:
        str: ASCII art representation of the input image.

    Example:
        To convert an image and print it as ASCII art:
        from np_asciiart import to_ascii
        pic = to_ascii(
            img=r"https://www.python.org/static/img/python-logo.png",
            width=160,
            height_adjust_stretch=2.5,
            letters="█▓▓▒▒░░ ",
        )

        print(pic)

    """
    img = open_image_in_cv(img, channels_in_output=2)
    ratio = img.shape[0] / img.shape[1]
    height = width * ratio
    dim = (int(width), int(int(height) / height_adjust_stretch))
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    imgempt = np.empty(img.shape, dtype="U1")
    steps = ceil(256 / len(letters))
    for letter, startcol, endcol in zip(
        letters, (range(0, 256, steps)), (range(steps, 256 + steps, steps))
    ):
        imgempt[
            numexpr.evaluate(
                "(img>=startcol) & (img<endcol)",
                global_dict={},
                local_dict={"img": img, "startcol": startcol, "endcol": endcol},
            )
        ] = letter
    return "\n".join(["".join(x) for x in imgempt])
