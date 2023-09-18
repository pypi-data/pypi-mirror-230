import argparse
from datetime import datetime
from format import format_values
from generate import generate

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "filename",
        nargs='?',
        type=str,
        default=f"IMG_{datetime.now().isoformat(timespec='seconds')}",
        help="File name of the generated file. File extension is used to infer the image file type.",
    )

    parser.add_argument(
        "-s",
        "--size",
        nargs=2,
        type=int,
        default=[1080, 1080],
        help="Image dimensions",
        metavar=("HEIGHT", "WIDTH"),
    )

    parser.add_argument(
        "-m",
        "--color-mode",
        default="HEX",
        choices=["RGB", "RGBA", "HSV", "CMYK", "YCbCr", "LAB", "P", "RGBX", "1", "F", "I", "L", "HEX"],
        help="Color format to use in image and given in --color",
    )

    parser.add_argument(
        "-c",
        "--color",
        default="#ffffff",
        help="Color value to use in image, it must be in format specified by --color-mode",
    )

    parser.add_argument(
        "-i",
        "--image-format",
        default="PNG",
        choices=["BLP", "BMP", "DDS", "DIB", "EPS", "GIF", "ICNS", "ICO", "IM", "JPEG", "JPEG_2000", "MSP",
                 "PCX", "PNG", "PPM", "SGI", "SPIDER", "TGA", "TIFF", "WebP", "XBM", "PALM", "PDF", "XV"],
        help="Image file format. Overrides the inferred file type from file name",
    )

    parser.add_argument(
        "-p",
        "--params",
        help="Additional params in JSON format that will be passed when saving image."
    )



    options = parser.parse_args()
    formatted_options = format_values(vars(options))
    status = generate(**formatted_options)

