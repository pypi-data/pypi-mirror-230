import json
import os
import re
import requests


LOCAL_JSON_PATH = os.path.expanduser("~/colors.json")
GITHUB_RAW_URL = "https://raw.githubusercontent.com/8tm/shields-io-gui/master/config/colors.json"


class ColorPalette:
    @classmethod
    def get_color_names(cls):
        colors = cls.get_colors()
        return list(colors.keys())

    @classmethod
    def load_colors_from_file(cls, filepath):
        with open(filepath, 'r') as file:
            return json.load(file)

    @classmethod
    def download_colors(cls):
        response = requests.get(GITHUB_RAW_URL)
        response.raise_for_status()
        return response.json()

    @classmethod
    def hex_to_rgb(cls, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    @classmethod
    def rgb_to_hex(cls, rgb_color):
        return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

    @classmethod
    def inverse_color(cls, hex_color):
        rgb_color = cls.hex_to_rgb(hex_color)
        inverted_rgb = tuple(255 - x for x in rgb_color)
        return cls.rgb_to_hex(inverted_rgb)

    @classmethod
    def identify_color(cls, input_string):
        hex_pattern = re.compile(r'^#?[A-Fa-f0-9]{6}$')

        if any(char.isdigit() for char in input_string):
            if hex_pattern.match(input_string):
                return "value"
            else:
                return "unknown"
        else:
            return "name"

    @staticmethod
    def get_colors():
        if os.path.exists(LOCAL_JSON_PATH):
            with open(LOCAL_JSON_PATH, 'r') as f:
                return json.load(f)
        else:
            try:
                response = requests.get(GITHUB_RAW_URL)
                response.raise_for_status()
                colors = response.json()
                with open(LOCAL_JSON_PATH, 'w') as f:
                    json.dump(colors, f)
                return colors
            except requests.RequestException as e:
                return {}

    colors = get_colors()
    colors = {key: value for key, value in colors.items()}
    colors_lower = {str(key).lower(): value for key, value in colors.items()}

    @classmethod
    def get_color_names(cls):
        return list(cls.colors.keys())

    @classmethod
    def get_hex_value(cls, color_name: str):
        return str(cls.colors_lower.get(color_name.lower()))
