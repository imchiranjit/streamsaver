import os
import argparse
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from ui.main_window import YouTubeDownloader
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='YouTube Downloader Application')
    parser.add_argument('--url', '-u', type=str, help='Default YouTube video URL to load')
    return parser.parse_args()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Set application icon
    app_icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))

    # Initialize the main window with the URL argument if provided
    window = YouTubeDownloader(default_url=args.url if hasattr(args, 'url') else None)
    window.show()
    sys.exit(app.exec_())