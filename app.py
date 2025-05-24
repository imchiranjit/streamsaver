import os
import urllib.parse
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

    # Process URL parameters from command line
    default_url = None
    
    if len(sys.argv) > 1:
        url_arg = sys.argv[1]
        if url_arg.startswith('http'):
            default_url = url_arg
        elif url_arg.startswith('streamsaver://'):
            url = url_arg.split('streamsaver://')[1]
            default_url = urllib.parse.unquote(url)

    # Initialize the main window with the URL argument if provided
    window = YouTubeDownloader(default_url=default_url)
    window.show()
    sys.exit(app.exec_())