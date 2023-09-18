import json


def format_values(options):
    options["params"] = format_params(options["params"])
    options["color_mode"], options["color"] = format_color(options["color_mode"], options["color"])
    return options


def format_params(params):
    params_dict = {}
    if params:
        params_dict = json.loads(params)
    return params_dict


def format_color(color_mode, color):
    if color_mode == "HEX":
        color_mode, standard_color = convert_hex_to_rgba(color)
    else:
        standard_color = color.split(",")

    return color_mode, tuple(standard_color)


def convert_hex_to_rgba(hex_color_code):
    raw_hex = hex_color_code.strip().strip("#")

    color_value = []
    color_mode = None

    if len(raw_hex) == 1:
        color_value = [int(raw_hex * 2, 16)] * 3
        color_mode = "RGB"
    elif len(raw_hex) == 3:
        color_value = [int(_hex * 2, 16) for _hex in raw_hex]
        color_mode = "RGB"
    elif len(raw_hex) == 4:
        color_value = [int(_hex * 2, 16) for _hex in raw_hex]
        color_mode = "RGBA"
    elif len(raw_hex) == 6:
        rgb_list = [
            raw_hex[0:2],
            raw_hex[2:4],
            raw_hex[4:6],
        ]
        color_value = [int(_hex, 16) for _hex in rgb_list]
        color_mode = "RGB"
    elif len(raw_hex) == 8:
        rgba_list = [
            raw_hex[0:2],
            raw_hex[2:4],
            raw_hex[4:6],
        ]
        color_value = [int(_hex, 16) for _hex in rgba_list]
        color_mode = "RGBA"

    return color_mode, color_value
