import json
import os
import requests


LOCAL_JSON_PATH = os.path.expanduser("~/icons.json")
GITHUB_RAW_URL = "https://raw.githubusercontent.com/8tm/shields-io-gui/master/config/icons.json"


def fetch_json_from_github():
    response = requests.get(GITHUB_RAW_URL)
    response.raise_for_status()
    with open(LOCAL_JSON_PATH, 'w') as file:
        file.write(response.text)


def load_logos_from_json():
    if not os.path.exists(LOCAL_JSON_PATH):
        fetch_json_from_github()

    with open(LOCAL_JSON_PATH, 'r') as file:
        return json.load(file)["icons"]


def convert_key_to_id(keys):
    if 'slug' in keys:
        return keys['slug']
    return keys['title'].replace(".", "dot").replace("-", "").replace("/", "").replace(" ", "").lower()


class LogoPalette:
    raw_data = load_logos_from_json()
    logos = {
        entry['title']: {
            "id": convert_key_to_id(entry),
            "color": "#" + entry['hex']
        } for entry in raw_data
    }

    @classmethod
    def get_logo_names(cls):
        return list(cls.logos.keys())

    @classmethod
    def get_logo_key(cls, logo_name):
        return cls.logos.get(logo_name, {}).get("id")

    @classmethod
    def get_logo_color(cls, logo_name):
        return cls.logos.get(logo_name, {}).get("color")
