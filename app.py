import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from ui.main_window import YouTubeDownloader
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application icon
    app_icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))

    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())