"""
Entry point for the application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

import os
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()