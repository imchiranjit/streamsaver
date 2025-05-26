from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QFrame, QComboBox, QMessageBox,
    QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.settings import Settings
from .settings_window import SettingsWindow
from threads.fetch_thread import FetchThread
from threads.download_thread import DownloadThread
from .material_dialog import MaterialDialog

class YouTubeDownloader(QWidget):
    def __init__(self, default_url=None):
        super().__init__()
        self.setWindowTitle("Stream Saver")
        self.setGeometry(300, 300, 600, 400)
        self.download_path = ""
        self.download_thread = None
        self.fetch_thread = None
        self.format_data = None
        self.settings = Settings()
        self.setup_ui()
        self.apply_material_styles()
        self.load_settings()  # Load settings
        if default_url:
            self.url_input.setText(default_url)
            self.fetch_video_info()

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
                selection-color: {surface};
                selection-background-color: {primary_color};
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
                background-color: transparent;
                color: #ed5e68;
                border: none;
                border-radius: 24px;
                border: 1px solid #ed5e68;
                font-weight: bold;
                padding: 8px 16px;
            }}
            
            QPushButton#secondaryButton:hover {{
                background-color: rgba(244, 67, 54, 0.1);
            }}
            
            QPushButton#secondaryButton:disabled {{
                background-color: #f1f1f1;
                color: #bdbdbd;
                border-color: #f1f1f1;
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

    def load_settings(self):
        self.settings.load()
        self.download_path = self.settings.get_default_download_location()
        self.location_label.setText(self.download_path)

    # Add this method to open settings window
    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.closed.connect(self.load_settings)  # Reload settings when closed
        self.settings_window.exec_()

    def fetch_video_info(self):
        url = self.url_input.text().strip()
        if not url:
            MaterialDialog.error(self, "Error", "Please enter a YouTube URL.")
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
            MaterialDialog.error(self, "Error", message)
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
            MaterialDialog.error(self, "Error", "Please enter a YouTube URL.")
            return
        if not self.download_path:
            MaterialDialog.error(self, "Error", "Please select a download location.")
            return
        
        # Get selected format IDs
        video_idx = self.video_quality_combo.currentIndex()
        audio_idx = self.audio_quality_combo.currentIndex()
        
        if video_idx <= 0:
            MaterialDialog.error(self, "Error", "Please select a video quality.")
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
        
        self.download_thread = DownloadThread(url, self.download_path, format_str, self.settings.get_max_connections())
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def cancel_download(self):
        result = MaterialDialog.question(
            self,
            "Cancel Download",
            "Are you sure you want to cancel the download?",
            buttons=("Yes", "No"),
            default_button=1  # Default to "No"
        )
        if result != 2:  # Not "Yes"
            return
        
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
            MaterialDialog.info(self, "Success", message)
            self.progress_bar.setValue(100)
            self.status_label.setText("Download completed")
        else:
            # Only show error message if it wasn't cancelled by user
            if "cancelled by user" in message:
                self.status_label.setText("Download cancelled")
                self.progress_bar.setValue(0)
            else:
                MaterialDialog.error(self, "Error", message)
                self.status_label.setText("Download failed")

    def closeEvent(self, event):
        result = MaterialDialog.question(
            self,
            "Exit",
            "Are you sure you want to quit?",
            buttons=("Yes", "No"),
            default_button=1  # Default to "No"
        )

        if result == 2:  # "Yes"
            print("Window is closing. Performing cleanup...")
            # You can call your custom callback here
            # self.my_on_close_callback()
            event.accept()
        else:
            event.ignore()