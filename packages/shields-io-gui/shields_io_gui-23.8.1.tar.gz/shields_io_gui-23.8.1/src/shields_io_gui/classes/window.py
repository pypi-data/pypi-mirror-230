from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QUrl, QTimer, QEvent, QObject
from PyQt5.QtGui import QColor
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSlider,
)
import pyautogui

from shields_io_gui.classes.color_palette import ColorPalette
from shields_io_gui.classes.color_picker import ColorPicker
from shields_io_gui.classes.logo_palette import LogoPalette
from shields_io_gui.classes.screen_capture import ScreenCapture
from shields_io_gui.classes.shields_io import ShieldsIO
from shields_io_gui.classes.custom_widgets import CustomComboBox, CustomLineEdit


COLOR_RECT_SIZE = 100
TIMER_INTERVAL = 50


class MouseEventListener(QObject):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.callback(event)
            QApplication.instance().removeEventFilter(self)
        return super(MouseEventListener, self).eventFilter(obj, event)


class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.shields_io = ShieldsIO()
        self.color = ColorPicker()
        self.content_modified = False
        self.dynamic_entries = {}
        self.bg_color = '#333333'
        self.current_zoom_factor = 2.0
        self.zoom_value = 500
        self.selected_combo_color = None
        self.selected_checkbox_color = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.pick_color)

        self.zoom_slider: QSlider = QSlider(Qt.Horizontal)
        self.bg_color_btn: QPushButton = QPushButton('Choose a background color')
        self.url_address: CustomLineEdit = CustomLineEdit()
        self.browser: QWebEngineView = QWebEngineView()
        self.url_parse_entry: CustomLineEdit = CustomLineEdit()
        self.analyze_btn: QPushButton = QPushButton('Analyze the URL and display the image')
        self.style_combo: CustomComboBox = CustomComboBox()
        self.url_link_label: QLabel = QLabel('Link url:')
        self.url_link: CustomLineEdit = CustomLineEdit()
        self.logo_combo: CustomComboBox = CustomComboBox()

        self.auto_logo_color_checkbox: QCheckBox = QCheckBox('Use Logo color')
        self.auto_name_checkbox: QCheckBox = QCheckBox('Use Logo name')
        self.auto_text1_background_color_checkbox: QCheckBox = QCheckBox('Use inversed Logo color for left background')
        self.auto_text2_background_color_checkbox: QCheckBox = QCheckBox('Use Logo color for right background')
        self.auto_color_enabled = True

        self.text1_entry: CustomLineEdit = CustomLineEdit('')
        self.text2_entry: CustomLineEdit = CustomLineEdit('Python')
        self.logo_color_combo: CustomComboBox = CustomComboBox()
        self.label_color_combo: CustomComboBox = CustomComboBox()
        self.color_combo: CustomComboBox = CustomComboBox()
        self.url_label: QLabel = QLabel('Copy as URL')
        self.markdown_label: QLabel = QLabel('Copy as MarkDown')
        self.html_label: QLabel = QLabel('Copy as HTML')
        self.ascii_label: QLabel = QLabel('Copy as AsciiDoc')
        self.rst_label: QLabel = QLabel('Copy as rSt')
        self.params_layout: QGridLayout = QGridLayout()

        self.init_ui()

    def start_color_picking(self, combobox, checkbox):
        self.selected_combo_color = combobox
        self.selected_checkbox_color = checkbox
        self.hide()
        x_start, y_start, total_width, height, cropped_pixmap = self.color.capture_screen()
        self.screen_capture = ScreenCapture(self, cropped_pixmap)
        self.screen_capture.setGeometry(x_start, y_start, total_width, height)
        self.timer.start(TIMER_INTERVAL)

    def pick_color(self):
        x, y = pyautogui.position()
        rgb, hex_color = self.color.get_color(x, y)
        if rgb:
            r, g, b = rgb
            self.screen_capture.color_rect.setBrush(QColor(r, g, b))
            self.screen_capture.color_rect.setPos(x + 5, y + 5)
            self.color.cached_pixmap.fill(QColor(r, g, b))
            self.selected_combo_color.setCurrentText(hex_color)

    def stop_color_picking(self):
        self.selected_checkbox_color.setChecked(False)
        self.show()
        self.timer.stop()

    def colorize(self, combo):
        color_names = ColorPalette.get_color_names()
        combo.addItems(color_names)

        for index, color_name in enumerate(color_names):
            hex_color = ColorPalette.get_hex_value(color_name)
            color = QColor(f'#{hex_color}')
            combo.setItemData(index, color, role=Qt.BackgroundRole)

    def init_ui(self):
        link_style = '''
            QLabel {
                color: blue;
            }
            QLabel:hover {
                color: green;
            }
        '''
        self.setStyleSheet(link_style)

        self.zoom_slider.setRange(100, 500)
        self.zoom_slider.setValue(self.zoom_value)
        self.zoom_slider.valueChanged.connect(self.update_zoom)

        self.bg_color_btn.clicked.connect(self.choose_bg_color)

        self.url_address.textChanged.connect(self.update_url)

        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0')

        self.browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.browser.setFixedHeight(200)
        self.browser.loadFinished.connect(self.on_load_finished)

        self.url_parse_entry.setPlaceholderText('Enter the img.shields.io URL for analysis...')
        self.analyze_btn.clicked.connect(self.parse_and_display)

        self.style_combo.setEditable(False)
        self.style_combo.addItems(self.shields_io.get_all_styles())
        self.style_combo.currentIndexChanged.connect(self.update_url)

        self.url_link.setPlaceholderText('URL link...')
        self.url_link.textChanged.connect(self.update_url)

        logo_names = LogoPalette.get_logo_names()

        self.logo_combo.addItems(logo_names)
        self.logo_combo.setEditable(True)
        self.logo_combo.currentTextChanged.connect(self.update_url)

        self.text1_entry.setPlaceholderText('Add text on the left side...')
        self.text1_entry.textChanged.connect(self.update_url)

        self.text2_entry.setPlaceholderText('Add text on the right side...')
        self.text2_entry.textChanged.connect(self.update_url)

        self.auto_logo_color_checkbox.setCheckable(True)
        self.auto_logo_color_checkbox.setChecked(True)
        self.auto_logo_color_checkbox.stateChanged.connect(self.toggle_auto_color)

        self.auto_name_checkbox.setCheckable(True)
        self.auto_name_checkbox.setChecked(True)
        self.auto_name_checkbox.stateChanged.connect(self.toggle_auto_name)



        self.auto_text1_background_color_checkbox.setCheckable(True)
        self.auto_text1_background_color_checkbox.setChecked(False)
        self.auto_text1_background_color_checkbox.stateChanged.connect(self.toggle_auto_color)

        self.auto_text2_background_color_checkbox.setCheckable(True)
        self.auto_text2_background_color_checkbox.setChecked(True)
        self.auto_text2_background_color_checkbox.stateChanged.connect(self.toggle_auto_color)



        self.logo_color_btn = QPushButton("...")
        self.label_color_btn = QPushButton("...")
        self.color_btn = QPushButton("...")

        self.logo_color_btn.setFixedWidth(30)
        self.label_color_btn.setFixedWidth(30)
        self.color_btn.setFixedWidth(30)

        self.logo_color_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.label_color_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.color_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)




        self.P_btn_1 = QPushButton("P")
        self.P_btn_2 = QPushButton("P")
        self.P_btn_3 = QPushButton("P")

        self.P_btn_1.setFixedWidth(30)
        self.P_btn_2.setFixedWidth(30)
        self.P_btn_3.setFixedWidth(30)

        self.P_btn_1.clicked.connect(lambda: self.start_color_picking(self.logo_color_combo, self.auto_logo_color_checkbox))
        self.P_btn_2.clicked.connect(lambda: self.start_color_picking(self.label_color_combo, self.auto_text1_background_color_checkbox))
        self.P_btn_3.clicked.connect(lambda: self.start_color_picking(self.color_combo, self.auto_text2_background_color_checkbox))

        self.logo_color_btn.clicked.connect(lambda: self.choose_color_for_combobox(self.logo_color_combo))
        self.label_color_btn.clicked.connect(lambda: self.choose_color_for_combobox(self.label_color_combo))
        self.color_btn.clicked.connect(lambda: self.choose_color_for_combobox(self.color_combo))

        logo_layout = QHBoxLayout()
        label_layout = QHBoxLayout()
        color_layout = QHBoxLayout()


        self.colorize(self.logo_color_combo)
        self.logo_color_combo.currentTextChanged.connect(self.update_url)

        self.colorize(self.label_color_combo)
        self.label_color_combo.currentTextChanged.connect(self.update_url)

        self.colorize(self.color_combo)
        self.color_combo.currentTextChanged.connect(self.update_url)


        self.url_label.content_to_copy = ''
        self.url_label.mousePressEvent = self.copy_to_clipboard
        self.url_label.setObjectName('url_label')

        self.markdown_label.content_to_copy = ''
        self.markdown_label.mousePressEvent = self.copy_to_clipboard
        self.markdown_label.setObjectName('markdown_label')

        self.html_label.content_to_copy = ''
        self.html_label.mousePressEvent = self.copy_to_clipboard
        self.html_label.setObjectName('html_label')

        self.ascii_label.content_to_copy = ''
        self.ascii_label.mousePressEvent = self.copy_to_clipboard
        self.ascii_label.setObjectName('ascii_label')

        self.rst_label.content_to_copy = ''
        self.rst_label.mousePressEvent = self.copy_to_clipboard
        self.rst_label.setObjectName('rst_label')

        def label_mouse_press_event(event, label):
            self.copy_to_clipboard(label)

        self.html_label.mousePressEvent = lambda event, label=self.html_label: label_mouse_press_event(event, label)
        self.ascii_label.mousePressEvent = lambda event, label=self.ascii_label: label_mouse_press_event(event, label)
        self.rst_label.mousePressEvent = lambda event, label=self.rst_label: label_mouse_press_event(event, label)
        self.markdown_label.mousePressEvent = lambda event, label=self.markdown_label: label_mouse_press_event(event, label)
        self.url_label.mousePressEvent = lambda event, label=self.url_label: label_mouse_press_event(event, label)

        self.params_layout.addWidget(self.zoom_slider, 0, 0, 1, 2)
        self.params_layout.addWidget(self.bg_color_btn, 0, 2)

        self.params_layout.addWidget(self.url_address, 1, 0, 1, 3)

        self.params_layout.addWidget(self.browser, 2, 0, 1, 3)

        self.params_layout.addWidget(self.url_parse_entry, 3, 0, 1, 2)
        self.params_layout.addWidget(self.analyze_btn, 3, 2)

        self.params_layout.addWidget(self.url_link, 4, 0, 1, 2)
        self.params_layout.addWidget(self.style_combo, 4, 2)

        self.params_layout.addWidget(self.logo_combo, 5, 0)
        self.params_layout.addWidget(self.text1_entry, 5, 1)
        self.params_layout.addWidget(self.text2_entry, 5, 2)

        self.params_layout.addWidget(self.auto_name_checkbox, 6, 2)


        self.params_layout.addWidget(self.auto_logo_color_checkbox, 7, 0)
        self.params_layout.addWidget(self.auto_text1_background_color_checkbox, 7, 1)
        self.params_layout.addWidget(self.auto_text2_background_color_checkbox, 7, 2)



        logo_layout.addWidget(self.logo_color_combo)
        logo_layout.addWidget(self.P_btn_1)
        logo_layout.addWidget(self.logo_color_btn)

        label_layout.addWidget(self.label_color_combo)
        label_layout.addWidget(self.P_btn_2)
        label_layout.addWidget(self.label_color_btn)

        color_layout.addWidget(self.color_combo)
        color_layout.addWidget(self.P_btn_3)
        color_layout.addWidget(self.color_btn)



        self.params_layout.addLayout(logo_layout, 8, 0)
        self.params_layout.addLayout(label_layout, 8, 1)
        self.params_layout.addLayout(color_layout, 8, 2)


        self.params_layout.addWidget(self.url_label, 9, 0)
        self.params_layout.addWidget(self.markdown_label, 9, 1)
        self.params_layout.addWidget(self.html_label, 9, 2)

        self.params_layout.addWidget(self.ascii_label, 10, 0)
        self.params_layout.addWidget(self.rst_label, 10, 1)


        repo_label = QLabel("<a href='https://github.com/8tm/shields-io-gui'>https://github.com/8tm/shields-io-gui</a>")
        repo_label.setAlignment(Qt.AlignCenter)
        repo_label.setStyleSheet('color: blue; text-decoration: underline;')
        repo_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        repo_label.setOpenExternalLinks(True)

        self.params_layout.addWidget(repo_label, self.params_layout.rowCount() - 1, 2)


        self.params_layout.setColumnStretch(0, 1)
        self.params_layout.setColumnStretch(1, 1)
        self.params_layout.setColumnStretch(2, 1)

        self.setLayout(self.params_layout)

        self.setWindowTitle('Shields.io GUI')
        self.setGeometry(100, 100, 800, 300)

        self.update_url()
        self.update_zoom(self.zoom_value)
        self.blockContextMenu()

        logo_name = 'Python'
        if logo_name:
            index = self.logo_combo.findText(logo_name)
            if index >= 0:
                self.logo_combo.setCurrentIndex(index)

        self.logo_color_combo.setCurrentText('#3776AB')

        color_name = 'Yellow'
        self.label_color_combo.setCurrentText(color_name)
        color_name_index = self.label_color_combo.findText(color_name)
        if color_name_index >= 0:
            self.label_color_combo.setCurrentIndex(color_name_index)

        self.color_combo.setCurrentText('#3776AB')

    def handle_mouse_click(self, event, combobox):
        QApplication.instance().restoreOverrideCursor()

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0)

        color = QColor(screenshot.toImage().pixel(event.pos()))

        hex_value = color.name()

        combobox.setCurrentText(hex_value)
        self.update_url()

    def choose_color_for_combobox(self, combobox):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            combobox.setCurrentText(hex_color)
            self.update_url()

    def toggle_auto_name(self, state):
        self.auto_name_enabled = state == Qt.Checked
        self.text2_entry.setText(self.logo_combo.currentText())
        self.update_url()

    def toggle_auto_color(self, state):
        self.auto_color_enabled = state == Qt.Checked
        self.update_url()

    def copy_to_clipboard(self, label):
        content = label.content_to_copy
        clipboard = QApplication.clipboard()
        clipboard.setText(content)

    def update_zoom(self, value):
        self.zoom_value = value
        self.current_zoom_factor = self.zoom_value / 100.0
        self.browser.setZoomFactor(self.current_zoom_factor)

    def set_browser_bg_color(self, color):
        css = '''
            html, body {{
                background-color: {};
                height: 100%;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
        '''.format(color)
        self.browser.page().runJavaScript(f'document.body.style.cssText = `{css}`;')

    def update_url(self):
        self.shields_io.update_parameters(
            style=self.style_combo.currentText(),
            logo=self.logo_combo.currentText(),
            color=self.color_combo.currentText(),
            logo_color=self.logo_color_combo.currentText(),
            label_color=self.label_color_combo.currentText(),
            text1=self.text1_entry.text(),
            text2=self.text2_entry.text(),
            link=self.url_link.text(),
            auto_color_enabled=self.auto_logo_color_checkbox.isChecked(),
            auto_name_enabled=self.auto_name_checkbox.isChecked(),
            auto_text1_background=self.auto_text1_background_color_checkbox.isChecked(),
            auto_text2_background=self.auto_text2_background_color_checkbox.isChecked(),
        )
        self.content_modified = False

        url = self.shields_io.get_url()

        updated_params = self.shields_io.parse_and_update_parameters(url)
        self.text2_entry.setText(updated_params['text2'])

        self.browser.setUrl(QUrl(url))
        self.browser.load(QUrl(url))

        self.html_label.content_to_copy = self.shields_io.get_html()
        self.ascii_label.content_to_copy = self.shields_io.get_ascii()
        self.rst_label.content_to_copy = self.shields_io.get_rst()
        self.markdown_label.content_to_copy = self.shields_io.get_markdown()
        self.url_label.content_to_copy = url
        self.url_address.setText(url)
        self.set_browser_bg_color(self.bg_color)

    def parse_and_display(self):
        self.auto_logo_color_checkbox.setChecked(False)
        self.auto_name_checkbox.setChecked(False)
        self.auto_text1_background_color_checkbox.setChecked(False)
        self.auto_text2_background_color_checkbox.setChecked(False)

        url = self.url_parse_entry.text()
        parsed_attributes = self.shields_io.parse_and_update_parameters(url)

        self.text1_entry.setText('')
        self.text2_entry.setText('')

        self.text1_entry.setText(parsed_attributes["text1"])
        self.text2_entry.setText(parsed_attributes["text2"])

        if 'color' in parsed_attributes:
            if ColorPalette.identify_color(parsed_attributes["color"]) == "value" and '#' not in parsed_attributes["color"]:
                self.color_combo.setCurrentText(f'#{parsed_attributes["color"]}')
            else:
                self.color_combo.setCurrentText(parsed_attributes["color"])
        else:
            self.color_combo.setCurrentText('')

        if 'logo_color' in parsed_attributes:
            if ColorPalette.identify_color(parsed_attributes["logo_color"]) == "value" and '#' not in parsed_attributes["logo_color"]:
                self.logo_color_combo.setCurrentText(f'#{parsed_attributes["logo_color"]}')
            else:
                self.logo_color_combo.setCurrentText(parsed_attributes["logo_color"])
        else:
            self.logo_color_combo.setCurrentText('')

        if 'label_color' in parsed_attributes:
            if ColorPalette.identify_color(parsed_attributes["label_color"]) == "value" and '#' not in parsed_attributes["label_color"]:
                self.label_color_combo.setCurrentText(f'#{parsed_attributes["label_color"]}')
            else:
                self.label_color_combo.setCurrentText(parsed_attributes["label_color"])
        else:
            self.label_color_combo.setCurrentText('')

        index = self.style_combo.findText(parsed_attributes["style"])
        if index >= 0:
            self.style_combo.setCurrentIndex(index)

        if "logo" in parsed_attributes:
            logo_name = parsed_attributes["logo"]
            if logo_name:
                index = self.logo_combo.findText(logo_name)
                if index >= 0:
                    self.logo_combo.setCurrentIndex(index)

        self.update_url()

    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color.name()

        self.set_browser_bg_color(self.bg_color)
        self.update_url()

    def on_load_finished(self, ok):
        if ok and not self.content_modified:
            def callback(result):
                self.content_modified = True
                html_content = result
                modified_html = '''
                    <html>
                    <head>
                        <style>
                            html, body {{
                                background-color: {};
                                height: 100%;
                                width: 100%;
                                margin: 0;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                            }}
                        </style>
                    </head>
                    <body>
                        {}
                    </body>
                    </html>
                '''.format(self.bg_color, html_content)

                self.browser.setHtml(modified_html)

            self.browser.page().toHtml(callback)
            self.browser.setZoomFactor(self.current_zoom_factor)

    def navigate(self):
        url = self.url_parse_entry.text()

        def callback(result):
            html_content = result
            modified_html = '''
                <html>
                <head>
                    <style>
                        html, body {{
                            height: 100%;
                            margin: 0;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }}
                    </style>
                </head>
                <body>
                    {}
                </body>
                </html>
            '''.format(html_content)
            self.browser.setHtml(modified_html)

        self.browser.load(QUrl(url))
        self.browser.page().toHtml(callback)

    def contextMenuEvent(self, event):
        pass

    def blockContextMenu(self):
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)
