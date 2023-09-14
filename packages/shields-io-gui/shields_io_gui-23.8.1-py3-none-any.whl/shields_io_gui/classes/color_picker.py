from io import BytesIO

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QImage
import pyautogui


COLOR_RECT_SIZE = 100
TIMER_INTERVAL = 50


def pillow_image_to_qimage(img):
    """Convert Pillow Image to QImage."""
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qt_image = QImage()
    qt_image.loadFromData(buffer.getvalue())
    return qt_image


class ColorPicker:
    def __init__(self):
        self.cached_pixmap = QPixmap(COLOR_RECT_SIZE, COLOR_RECT_SIZE)
        self.captured_image = None

    def capture_screen(self):
        total_width = 0
        y_start = float('inf')
        y_end = 0
        x_start = float('inf')
        screen_count = QApplication.desktop().screenCount()
        for i in range(screen_count):
            geometry = QApplication.desktop().screenGeometry(i)
            total_width += geometry.width()
            y_start = min(y_start, geometry.top())
            y_end = max(y_end, geometry.bottom())
            x_start = min(x_start, geometry.left())
        height = y_end - y_start
        screenshot = pyautogui.screenshot(region=(x_start, y_start, total_width, height))
        self.captured_image = pillow_image_to_qimage(screenshot)
        pixmap = QPixmap.fromImage(self.captured_image)
        cropped_pixmap = pixmap.copy(0, 1, total_width, height - 1)
        return x_start, y_start, total_width, height, cropped_pixmap

    def get_color(self, x, y):
        if not (0 <= x < self.captured_image.width() and 0 <= y < self.captured_image.height()):
            return None, None
        color = self.captured_image.pixelColor(x, y)
        r, g, b = color.red(), color.green(), color.blue()
        hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        return (r, g, b), hex_color
