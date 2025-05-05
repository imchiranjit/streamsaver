import sys
import os
import json
from settings import SettingsWindow
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QProgressBar, QHBoxLayout, QFrame, QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import yt_dlp


class FetchThread(QThread):
    finished = pyqtSignal(bool, dict, str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            formats_data = {'video': [], 'audio': []}
            video_info = {}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if info.get('formats'):
                    # Save video title and thumbnail
                    video_info['title'] = info.get('title', 'Unknown Title')
                    video_info['thumbnail'] = info.get('thumbnail', '')
                    
                    # Process formats
                    for fmt in info['formats']:
                        format_id = fmt.get('format_id', '')
                        format_note = fmt.get('format_note', '')
                        ext = fmt.get('ext', '')
                        resolution = fmt.get('resolution', '')
                        
                        if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                            # This is a format with both video and audio
                            tbr = fmt.get('tbr', 0)
                            quality_str = f"{resolution} ({format_note}) [{ext}] [{tbr}kbps]"
                            formats_data['video'].append({
                                'format_id': format_id,
                                'display': quality_str,
                                'is_video_audio': True
                            })
                        elif fmt.get('vcodec') != 'none':
                            # Video-only format
                            vbr = fmt.get('vbr', 0)
                            quality_str = f"{resolution} (Video Only) [{ext}] [{vbr}kbps]"
                            formats_data['video'].append({
                                'format_id': format_id,
                                'display': quality_str,
                                'is_video_audio': False
                            })
                        elif fmt.get('acodec') != 'none':
                            # Audio-only format
                            abr = fmt.get('abr', 0)
                            quality_str = f"{abr}kbps (Audio Only) [{ext}]"
                            formats_data['audio'].append({
                                'format_id': format_id,
                                'display': quality_str
                            })
            
            # Sort video formats by resolution (higher first)
            formats_data['video'] = sorted(
                formats_data['video'],
                key=lambda x: x['display'],
                reverse=True
            )
            
            # Sort audio formats by bitrate (higher first)
            formats_data['audio'] = sorted(
                formats_data['audio'],
                key=lambda x: x['display'],
                reverse=True
            )
            
            self.finished.emit(True, {'formats': formats_data, 'info': video_info}, "Formats fetched successfully")
                
        except Exception as e:
            self.finished.emit(False, {}, str(e))


class DownloadThread(QThread):
    progress = pyqtSignal(float, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, url, download_path, format_id):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.format_id = format_id
        self.is_cancelled = False

    def run(self):
        try:
            ydl_opts = {
                'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
                'progress_hooks': [self.progress_hook],
                'format': self.format_id
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if not self.is_cancelled:
                    ydl.download([self.url])
            
            if self.is_cancelled:
                self.finished.emit(False, "Download cancelled by user")
            else:
                self.finished.emit(True, "Download completed successfully!")
                
        except Exception as e:
            self.finished.emit(False, str(e))

    def cancel_download(self):
        self.is_cancelled = True

    def progress_hook(self, d):
        if self.is_cancelled:
            return
            
        if d['status'] == 'downloading':
            percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', d.get('total_bytes_estimate', 0)) * 100
            if percent:
                # Convert to float if it's not None and clamp between 0-100
                percent = float(percent) if percent is not None else 0
                percent = max(0, min(percent, 100))
                
                # Format download info
                speed = d.get('speed', 0)
                if speed:
                    speed_str = f"{speed/1024/1024:.2f} MB/s"
                else:
                    speed_str = "calculating..."
                
                eta = d.get('eta', 0)
                if eta:
                    eta_str = f"ETA: {eta} sec"
                else:
                    eta_str = "calculating..."
                
                status = f"{speed_str} | {eta_str}"
                self.progress.emit(percent, status)


class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stream Saver")
        self.setGeometry(300, 300, 600, 400)
        self.download_path = ""
        self.download_thread = None
        self.fetch_thread = None
        self.format_data = None
        self.settings = None
        self.setup_ui()
        self.load_settings()  # Load settings
        self.apply_material_styles()

    def load_settings(self):
        """Load settings from JSON file"""
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    self.settings = json.load(f)
                    # Set default download path from settings if available
                    if self.settings and 'general' in self.settings and 'default_download_location' in self.settings['general']:
                        self.download_path = self.settings['general']['default_download_location']
                        if self.download_path and os.path.exists(self.download_path):
                            self.location_label.setText(self.download_path)
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = None

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # App header layout
        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        
        # App title
        title_label = QLabel("Stream Saver")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)

        # Subtitle
        subtitle = QLabel("Download videos easily")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #5f6368;")
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        
        # Add settings button to the right
        self.settings_button = QPushButton("⚙️")  # Gear emoji
        self.settings_button.setObjectName("iconButton")
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setMaximumWidth(40)
        self.settings_button.setMaximumHeight(40)
        header_layout.addWidget(self.settings_button, alignment=Qt.AlignRight)

        main_layout.addLayout(header_layout)
        
        # Add some spacing
        main_layout.addSpacing(20)

        # Card container for inputs
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)
        
        # URL input and fetch button
        url_layout = QVBoxLayout()
        
        url_input_layout = QHBoxLayout()
        self.url_label = QLabel("YouTube URL")
        self.url_label.setObjectName("fieldLabel")
        url_layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.url_input.setObjectName("materialInput")
        self.url_input.setMinimumHeight(40)
        url_input_layout.addWidget(self.url_input)
        
        url_layout.addLayout(url_input_layout)
        
        self.fetch_button = QPushButton("Fetch")
        self.fetch_button.setObjectName("outlineButton")
        self.fetch_button.clicked.connect(self.fetch_video_info)
        self.fetch_button.setMinimumHeight(40)
        self.fetch_button.setMinimumWidth(80)
        url_input_layout.addWidget(self.fetch_button)
        
        card_layout.addLayout(url_layout)
        
        # Video info display (shows after fetching)
        self.video_title = QLabel("")
        self.video_title.setObjectName("videoTitle")
        self.video_title.setWordWrap(True)
        self.video_title.setVisible(False)
        card_layout.addWidget(self.video_title)
        
        # Quality selection section
        quality_layout = QHBoxLayout()
        
        # Video quality selection
        video_quality_layout = QVBoxLayout()
        self.video_quality_label = QLabel("Video Quality")
        self.video_quality_label.setObjectName("fieldLabel")
        video_quality_layout.addWidget(self.video_quality_label)
        
        self.video_quality_combo = QComboBox()
        self.video_quality_combo.setObjectName("materialCombo")
        self.video_quality_combo.setMinimumHeight(40)
        self.video_quality_combo.setEnabled(False)
        self.video_quality_combo.currentIndexChanged.connect(self.on_video_quality_changed)
        video_quality_layout.addWidget(self.video_quality_combo)
        
        quality_layout.addLayout(video_quality_layout)
        
        # Audio quality selection
        audio_quality_layout = QVBoxLayout()
        self.audio_quality_label = QLabel("Audio Quality")
        self.audio_quality_label.setObjectName("fieldLabel")
        audio_quality_layout.addWidget(self.audio_quality_label)
        
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.setObjectName("materialCombo")
        self.audio_quality_combo.setMinimumHeight(40)
        self.audio_quality_combo.setEnabled(False)
        audio_quality_layout.addWidget(self.audio_quality_combo)
        
        quality_layout.addLayout(audio_quality_layout)
        
        card_layout.addLayout(quality_layout)
        
        # Location selection
        location_layout = QHBoxLayout()
        
        self.location_label = QLabel("Not selected")
        self.location_label.setObjectName("locationLabel")
        self.location_label.setText(self.download_path if self.download_path else "Not selected")
        
        self.choose_button = QPushButton("Choose Location")
        self.choose_button.setObjectName("outlineButton")
        self.choose_button.clicked.connect(self.choose_directory)
        self.choose_button.setMinimumHeight(40)
        
        location_layout.addWidget(self.location_label)
        location_layout.addWidget(self.choose_button)
        card_layout.addLayout(location_layout)
        
        # Add the card to main layout
        main_layout.addWidget(card)

        # Progress section
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("materialProgress")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumHeight(6)
        self.progress_bar.setMaximumHeight(6)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to fetch video info")
        self.status_label.setObjectName("statusLabel")
        main_layout.addWidget(self.status_label)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        # Add cancel button on the left
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setEnabled(False)  # Disabled by default
        buttons_layout.addWidget(self.cancel_button)
        
        # Spacer to push download button to the right
        buttons_layout.addStretch()
        
        self.download_button = QPushButton("Download")
        self.download_button.setObjectName("primaryButton")
        self.download_button.clicked.connect(self.download_video)
        self.download_button.setMinimumHeight(48)
        self.download_button.setMinimumWidth(120)
        self.download_button.setEnabled(False)  # Disabled until format selection
        buttons_layout.addWidget(self.download_button)
        
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def apply_material_styles(self):
        # Material Design 3 inspired color palette
        primary_color = "#1a73e8"  # Blue
        primary_variant = "#0d47a1"
        on_surface = "#202124" 
        surface = "#ffffff"
        error_color = "#b00020"
        background = "#f8f9fa"
        
        self.setStyleSheet(f"""            
            QPushButton#iconButton {{
                background-color: transparent;
                border-radius: 20px;
                font-size: 20px;
                padding: 5px;
            }}

            QPushButton#iconButton:hover {{
                background-color: #e8f0fe;
            }}

            QWidget {{
                background-color: {background};
                color: {on_surface};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QFrame#card {{
                background-color: {surface};
                border-radius: 12px;
                border: 1px solid #dadce0;
            }}
            
            QLabel#fieldLabel {{
                font-size: 14px;
                color: #5f6368;
            }}
            
            QLabel#videoTitle {{
                font-size: 14px;
                font-weight: bold;
                color: {on_surface};
                padding-bottom: 8px;
                margin-bottom: 8px;
                border-bottom: 1px solid #dadce0;
            }}
            
            QLabel#statusLabel {{
                font-size: 13px;
                color: #5f6368;
                margin-top: 4px;
            }}
            
            QLabel#locationLabel {{
                color: #5f6368;
                padding-left: 4px;
            }}
            
            QLineEdit#materialInput {{
                border: 1px solid #dadce0;
                border-radius: 8px;
                padding: 8px 12px;
                background: {surface};
                selection-background-color: #e8f0fe;
            }}
            
            QLineEdit#materialInput:focus {{
                border: 2px solid {primary_color};
            }}
            
            QComboBox#materialCombo {{
                border: 1px solid #dadce0;
                border-radius: 8px;
                padding: 8px 12px;
                background: {surface};
                selection-background-color: #e8f0fe;
            }}
            
            QComboBox#materialCombo:focus {{
                border: 2px solid {primary_color};
            }}
            
            QComboBox#materialCombo::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border-left: none;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            
            QPushButton#primaryButton {{
                background-color: {primary_color};
                color: white;
                border: none;
                border-radius: 24px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            
            QPushButton#primaryButton:hover {{
                background-color: {primary_variant};
            }}
            
            QPushButton#primaryButton:disabled {{
                background-color: #a9a9a9;
            }}
            
            QPushButton#secondaryButton {{
                background-color: #ed5e68;
                color: #feffff;
                border: none;
                border-radius: 24px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            
            QPushButton#secondaryButton:hover {{
                background-color: #d0d0d0;
            }}
            
            QPushButton#secondaryButton:disabled {{
                background-color: #f1f1f1;
                color: #bdbdbd;
            }}
            
            QPushButton#outlineButton {{
                background-color: {surface};
                color: {primary_color};
                border: 1px solid {primary_color};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            
            QPushButton#outlineButton:hover {{
                background-color: #e8f0fe;
            }}
            
            QProgressBar#materialProgress {{
                background-color: #e0e0e0;
                border-radius: 3px;
                border: none;
            }}
            
            QProgressBar#materialProgress::chunk {{
                background-color: {primary_color};
                border-radius: 3px;
            }}
        """)

    # Add this method to open settings window
    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.closed.connect(self.load_settings)  # Reload settings when closed
        self.settings_window.exec_()

    def fetch_video_info(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Error", "Please enter a YouTube URL.")
            return
        
        self.fetch_button.setEnabled(False)
        self.video_quality_combo.clear()
        self.audio_quality_combo.clear()
        self.download_button.setEnabled(False)
        self.video_title.setVisible(False)
        self.status_label.setText("Fetching video information...")
        self.progress_bar.setValue(0)
        
        self.fetch_thread = FetchThread(url)
        self.fetch_thread.finished.connect(self.fetch_finished)
        self.fetch_thread.start()
    
    def fetch_finished(self, success, data, message):
        self.fetch_button.setEnabled(True)
        
        if success:
            self.format_data = data
            
            # Update video title
            if 'info' in data and 'title' in data['info']:
                self.video_title.setText(f"Title: {data['info']['title']}")
                self.video_title.setVisible(True)
            
            # Populate video quality dropdown
            self.video_quality_combo.clear()
            self.video_quality_combo.addItem("Select video quality", None)
            for idx, fmt in enumerate(data['formats']['video']):
                self.video_quality_combo.addItem(fmt['display'], fmt['format_id'])
            
            # Populate audio quality dropdown
            self.audio_quality_combo.clear()
            self.audio_quality_combo.addItem("Select audio quality (optional)", None)
            for idx, fmt in enumerate(data['formats']['audio']):
                self.audio_quality_combo.addItem(fmt['display'], fmt['format_id'])
            
            self.video_quality_combo.setEnabled(True)
            self.audio_quality_combo.setEnabled(True)
            self.status_label.setText("Please select video quality")
        else:
            QMessageBox.critical(self, "Error", message)
            self.status_label.setText("Failed to fetch video information")
    
    def on_video_quality_changed(self, index):
        if index <= 0:
            self.download_button.setEnabled(False)
            return
        
        # Check if the selected video format includes audio
        video_format_data = self.format_data['formats']['video'][index-1]
        if video_format_data.get('is_video_audio', False):
            # If format has both video and audio, disable audio selection
            self.audio_quality_combo.setCurrentIndex(0)
            self.audio_quality_combo.setEnabled(False)
        else:
            # If video only, enable audio selection
            self.audio_quality_combo.setEnabled(True)
            
        # Enable download button
        self.download_button.setEnabled(True)

    def choose_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if path:
            self.download_path = path
            self.location_label.setText(path)

    def download_video(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Error", "Please enter a YouTube URL.")
            return
        if not self.download_path:
            QMessageBox.critical(self, "Error", "Please select a download location.")
            return
        
        # Get selected format IDs
        video_idx = self.video_quality_combo.currentIndex()
        audio_idx = self.audio_quality_combo.currentIndex()
        
        if video_idx <= 0:
            QMessageBox.critical(self, "Error", "Please select a video quality.")
            return
        
        video_format = self.video_quality_combo.itemData(video_idx)
        audio_format = self.audio_quality_combo.itemData(audio_idx) if audio_idx > 0 else None
        
        # Create format string for yt-dlp
        format_str = video_format
        if audio_format:
            format_str = f"{video_format}+{audio_format}"

        self.download_button.setEnabled(False)
        self.fetch_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting download...")
        
        self.download_thread = DownloadThread(url, self.download_path, format_str)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.status_label.setText("Cancelling download...")
            self.download_thread.cancel_download()
            self.cancel_button.setEnabled(False)
    
    def update_progress(self, percent, status):
        self.progress_bar.setValue(int(percent))
        self.status_label.setText(status)
    
    def download_finished(self, success, message):
        self.download_button.setEnabled(True)
        self.fetch_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.progress_bar.setValue(100)
            self.status_label.setText("Download completed")
        else:
            # Only show error message if it wasn't cancelled by user
            if "cancelled by user" in message:
                self.status_label.setText("Download cancelled")
                self.progress_bar.setValue(0)
            else:
                QMessageBox.critical(self, "Error", message)
                self.status_label.setText("Download failed")

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            print("Window is closing. Performing cleanup...")
            # You can call your custom callback here
            # self.my_on_close_callback()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())