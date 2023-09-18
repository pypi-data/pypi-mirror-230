
from PIL import Image


def generate(
        filename: str,
        size,
        color_mode,
        color,
        image_format = None,
        params = {}
):
    status = None

    try:
        img = Image.new(mode=color_mode, size=size, color=color)
        img.save(filename, image_format, **params)
        status = True
        print("Image Generated")
    except Exception as err:
        print(f"Oops!  That was an Error {err=}, {type(err)=}. Check options and try again")

    return status


