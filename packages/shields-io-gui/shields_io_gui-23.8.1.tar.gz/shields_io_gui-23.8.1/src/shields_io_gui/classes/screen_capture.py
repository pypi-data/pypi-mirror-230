import base64

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QColor, QCursor, QPixmap
from PyQt5.QtCore import Qt, QByteArray


COLOR_RECT_SIZE = 100
TIMER_INTERVAL = 50


class ScreenCapture(QGraphicsView):
    def __init__(self, parent, pixmap):
        super().__init__()

        custom_cursor_data = (
            b'iVBORw0KGgoAAAANSUhEUgAAAAsAAAALCAYAAACprHcmAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9kTtIw1AUhv+2SotUBO0g4pChOtnBB'
            b'6JbrUIRKoRaoVUHk5u+oElDkuLiKLgWHHwsVh1cnHV1cBUEwQeIq4uToouUeG5SaBHjgcv9+O/5f+49F/A3Kkw1u+KAqllGOpkQsrlVIf'
            b'iKEHzoxyzGJWbqc6KYgmd93VMv1V2MZ3n3/Vm9St5kgE8gjjPdsIg3iKc3LZ3zPnGElSSF+Jx4zKALEj9yXXb5jXPRYT/PjBiZ9DxxhFg'
            b'odrDcwaxkqMRTxFFF1Sjfn3VZ4bzFWa3UWOue/IXhvLayzHVaw0hiEUsQIUBGDWVUYCFGu0aKiTSdJzz8Q45fJJdMrjIYORZQhQrJ8YP/'
            b'we/ZmoXJCTcpnAC6X2z7YwQI7gLNum1/H9t28wQIPANXWttfbQAzn6TX21r0COjbBi6u25q8B1zuAINPumRIjhSg5S8UgPcz+qYcMHAL9'
            b'Ky5c2ud4/QByNCsUjfAwSEwWqTsdY93hzrn9m9Pa34/5xVy1UWQIZUAAAAGYktHRAAAAAAAAPlDu38AAAAJcEhZcwAALiMAAC4jAXilP3'
            b'YAAAAHdElNRQfnCAEUDTTAbCxqAAAAIHRFWHRDb21tZW50AENyZWF0ZWQgd2l0aCBHSU1QIGJ5IDh0bVMaHQUAAAChSURBVBjTlZHRCcM'
            b'wDESfu0cJpAvkK8QBd5lO4MH61Q26QCYoNBSMpvD1Rwlp/3w/kuDukE7gEIwZSoSaQBFqhiIYOUJwm6HKTDJTAm39DFVw2x13IugNSl7l'
            b'IheMZChHoqRFUi9pOQoyFKK7/hH7H4GZItSQQNvuT+ni7Rn4AFxDeO3HtTifJjCADlhDGICH+9zXEIbOhwmsLY2mnFs++AVpEc4lF7SLw'
            b'QAAAABJRU5ErkJggg=='
        )
        cursor_pixmap = QPixmap()
        byte_array = QByteArray(base64.b64decode(custom_cursor_data))
        cursor_pixmap.loadFromData(byte_array, format='PNG')

        self.parent = parent
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setCursor(QCursor(cursor_pixmap))
        self.screenshot_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.screenshot_item)
        self.color_rect = self.scene.addRect(0, 0, COLOR_RECT_SIZE, COLOR_RECT_SIZE, brush=QColor(255, 255, 255))
        self.color_rect.setZValue(1)
        self.setGeometry(pixmap.rect())
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.stop_color_picking()
            self.close()
