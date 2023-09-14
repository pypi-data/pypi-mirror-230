import urllib.parse as urllib_parse

from shields_io_gui.classes.color_palette import ColorPalette
from shields_io_gui.classes.logo_palette import LogoPalette
from shields_io_gui.classes.badge_style import BadgeStyle


class ShieldsIO:
    BASE_URL_TEMPLATE = 'https://img.shields.io/badge/{text1}-{text2}-informational?'

    def __init__(self):
        self.style = BadgeStyle.FLAT
        self.logo = 'Python'
        self.color = '#3776AB'
        self.logo_color = '#3776AB'
        self.label_color = 'Yellow'
        self.text1 = ''
        self.text2 = 'Python'
        self.link = None
        self.auto_color_enabled = True
        self.auto_name_enabled = True
        self.auto_text1_background = False
        self.auto_text2_background = True

    def update_parameters(self, **kwargs):
        if 'auto_name_enabled' in kwargs and not kwargs['auto_name_enabled']:
            self.text2 = self.convert_symbol(kwargs['text2'], to_html=False) or ''

        self.text1 = self.convert_symbol(kwargs['text1'], to_html=False) or ''

        if 'link' in kwargs:
            self.link = kwargs['link']

        if 'logo' in kwargs:
            if 'auto_name_enabled' in kwargs and kwargs['auto_name_enabled']:
                self.text2 = kwargs['logo']
            self.logo = kwargs['logo']

        self.style = BadgeStyle.from_string(kwargs['style'])

        self.logo_color = ''
        if 'auto_color_enabled' in kwargs and kwargs['auto_color_enabled']:
            try:
                self.logo_color = LogoPalette.get_logo_color(self.logo)
            except AttributeError:
                if '#' in kwargs['logo_color']:
                    self.logo_color = kwargs['logo_color'].strip()
                else:
                    self.logo_color = '#3776AB'
        else:
            if 'logo_color' in kwargs and '#' in kwargs['logo_color']:
                self.logo_color = kwargs['logo_color'].strip()
            elif 'logo_color' in kwargs and '#' not in kwargs['logo_color']:
                if ColorPalette.identify_color(kwargs['logo_color']) == "value":
                    self.logo_color = ColorPalette.get_hex_value(kwargs['logo_color'].strip())
                elif ColorPalette.identify_color(kwargs['logo_color']) == "name":
                    self.logo_color = kwargs['logo_color'].strip()

        self.label_color = ''
        if 'label_color' in kwargs and '#' in kwargs['label_color']:
            if 'auto_text1_background' in kwargs and kwargs['auto_text1_background']:
                self.label_color = ColorPalette.inverse_color(self.logo_color).upper()
            else:
                self.label_color = kwargs['label_color'].upper()
        elif 'label_color' in kwargs and '#' not in kwargs['label_color']:
            if 'auto_text1_background' in kwargs and kwargs['auto_text1_background']:
                if ColorPalette.identify_color(self.logo_color) == "value":
                    self.label_color = ColorPalette.inverse_color(self.logo_color).upper()
                elif ColorPalette.identify_color(self.logo_color) == "name":
                    color_value = ColorPalette.get_hex_value(self.logo_color)
                    self.label_color = ColorPalette.inverse_color(color_value).upper()
            else:
                if ColorPalette.identify_color(kwargs['label_color']) == "value":
                    self.label_color = ColorPalette.get_hex_value(kwargs['label_color']).upper()
                elif ColorPalette.identify_color(kwargs['label_color']) == "name":
                    self.label_color = kwargs['label_color'].strip()

        self.color = ''
        if 'color' in kwargs and '#' in kwargs['color']:
            if 'auto_text2_background' in kwargs and kwargs['auto_text2_background']:
                self.color = self.logo_color
            else:
                self.color = kwargs['color'].upper()
        elif 'color' in kwargs and '#' not in kwargs['color']:
            if 'auto_text2_background' in kwargs and kwargs['auto_text2_background']:
                self.color = self.logo_color
            elif ColorPalette.identify_color(kwargs['color']) == "value":
                self.color = ColorPalette.get_hex_value(kwargs['color'].strip()).upper()
            elif ColorPalette.identify_color(kwargs['color']) == "name":
                self.color = kwargs['color'].strip()

    def parse_and_update_parameters(self, url):
        parsed_url = urllib_parse.urlparse(url)
        if parsed_url.netloc != 'img.shields.io':
            return {}

        parsed_attributes = {}
        text = urllib_parse.urlparse(url).path.replace('/badge/', '').replace('-informational', '').replace('%20', ' ')

        try:
            left_text, *right_text = text.split('-')
            parsed_attributes['text1'] = left_text.replace('_', ' ')
        except ValueError:
            right_text = urllib_parse.urlparse(url).path.replace('/badge/', '')

        parsed_attributes['text2'] = ' '.join(right_text).replace('_', ' ')

        query_string = f'{urllib_parse.urlparse(url).query}{urllib_parse.urlparse(url).fragment}'
        query = urllib_parse.parse_qs(query_string)

        for key, value in query.items():
            if key == 'label':
                parsed_attributes['text1'] = value[0]
            elif key == 'color':
                parsed_attributes['color'] = value[0]
            elif key == 'logoColor':
                parsed_attributes['logo_color'] = value[0]
            elif key == 'labelColor':
                parsed_attributes['label_color'] = value[0]
            elif key == 'link':
                parsed_attributes['link'] = value[0]
            elif key == 'style':
                parsed_attributes['style'] = value[0]
            elif key == 'logo':
                logo_name = next((name for name, id in LogoPalette.logos.items() if id['id'] == value[0].lower()), None)
                if logo_name:
                    parsed_attributes['logo'] = logo_name

        self.update_parameters(**parsed_attributes)

        return parsed_attributes

    @staticmethod
    def format_color(input_color):
        if input_color is None or input_color.upper() == 'NONE':
            return ''

        if input_color.startswith("#"):
            return input_color[1:].upper()

        return input_color.lower()

    def convert_symbol(self, text: str, to_html=True):
        if to_html:
            return urllib_parse.quote(text)
        return urllib_parse.unquote(text)

    def get_url(self):
        params_dict = {
            'style': self.style.value,
            'logo': LogoPalette.get_logo_key(self.logo),
            'color': self.format_color(self.color),
            'logoColor': self.format_color(self.logo_color),
            'labelColor': self.format_color(self.label_color),
            'link': self.link
        }

        params_dict = {k: v for k, v in params_dict.items() if v is not None}
        params = [f'{key}={value}' for key, value in params_dict.items() if len(value) > 0]

        return self.BASE_URL_TEMPLATE.format(
            text1=urllib_parse.quote(self.text1),
            text2=urllib_parse.quote(self.text2)
        ) + '&'.join(params)

    @staticmethod
    def get_all_styles():
        return BadgeStyle.get_all_styles()

    def get_html(self):
        base_url = self.get_url()
        return f'<img alt="Static Badge" src="{base_url}">'

    def get_ascii(self):
        base_url = self.get_url()
        return f'image:{base_url}[Static Badge]'

    def get_rst(self):
        base_url = self.get_url()
        return f'.. image:: {base_url}\n   :alt: Static Badge'

    def get_markdown(self):
        base_url = self.get_url()
        return f'![Static Badge]({base_url})'
