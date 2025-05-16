import os
import argparse
import urllib.parse
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from ui.main_window import YouTubeDownloader
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='YouTube Downloader Application')
    parser.add_argument('--url', '-u', type=str, help='Default YouTube video URL to load')
    parser.add_argument('--aurl', type=str, help='Application URL from protocol handler (streamsaver://)')
    return parser.parse_args()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Set application icon
    app_icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))

    # Process URL parameters
    default_url = None
    
    # Check for aurl first (from protocol handler)
    if hasattr(args, 'aurl') and args.aurl:
        # Remove protocol prefix if present
        if args.aurl.startswith('streamsaver://'):
            # Extract the encoded part after the protocol
            encoded_part = args.aurl[len('streamsaver://'):]
            # Decode the URL
            default_url = urllib.parse.unquote(encoded_part)
    
    # If no aurl, use the standard url parameter
    elif hasattr(args, 'url') and args.url:
        default_url = args.url

    # Initialize the main window with the URL argument if provided
    window = YouTubeDownloader(default_url=default_url)
    window.show()
    sys.exit(app.exec_())