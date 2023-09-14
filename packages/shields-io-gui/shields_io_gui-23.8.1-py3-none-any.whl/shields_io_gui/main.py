import os
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
)

from shields_io_gui.classes.window import Window

os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'


def main():
    app = QApplication(sys.argv)
    window = Window()
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

