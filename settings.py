import os
import json
from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QSpinBox, QCheckBox, QFrame,
    QTabWidget, QGridLayout, QGroupBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class SettingsWindow(QDialog):
    closed = pyqtSignal()  # Signal to indicate the window is closed
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stream Saver - Settings")
        self.setGeometry(300, 300, 600, 400)
        
        # Default settings
        self.settings = {
            "general": {
                "default_download_location": "",
                "theme": "light"
            },
            "downloader": {
                "max_connections": 3,
                "post_process_audio": False,
                "post_process_video": False,
                "preferred_audio_format": "mp3",
                "preferred_video_quality": "best",
                "auto_add_metadata": True
            }
        }
        
        self.load_settings()
        self.setup_ui()
        self.apply_material_styles()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # App title
        title_label = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("Customize your Stream Saver experience")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #5f6368;")
        main_layout.addWidget(subtitle, alignment=Qt.AlignCenter)
        
        # Add some spacing
        main_layout.addSpacing(20)
        
        # Card container for settings
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)
        
        # Tab widget for settings categories
        tabs = QTabWidget()
        tabs.setObjectName("materialTabs")
        
        # General Settings Tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setContentsMargins(16, 16, 16, 16)
        general_layout.setSpacing(16)
        
        # Default download location
        location_group = QGroupBox("Default Download Location")
        location_group.setObjectName("settingsGroup")
        location_layout = QHBoxLayout(location_group)
        
        self.location_label = QLabel(self.settings["general"]["default_download_location"] or "Not selected")
        self.location_label.setObjectName("locationLabel")
        self.location_label.setWordWrap(True)
        
        self.choose_button = QPushButton("Choose Location")
        self.choose_button.setObjectName("outlineButton")
        self.choose_button.clicked.connect(self.choose_directory)
        self.choose_button.setMinimumHeight(40)
        
        location_layout.addWidget(self.location_label)
        location_layout.addWidget(self.choose_button)
        
        general_layout.addWidget(location_group)
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_group.setObjectName("settingsGroup")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("materialCombo")
        self.theme_combo.addItem("Light", "light")
        self.theme_combo.addItem("Dark", "dark")
        self.theme_combo.setMinimumHeight(40)
        
        # Set current theme
        index = self.theme_combo.findData(self.settings["general"]["theme"])
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        theme_layout.addWidget(self.theme_combo)
        general_layout.addWidget(theme_group)
        
        # Add stretch to push everything to the top
        general_layout.addStretch()
        
        # Downloader Settings Tab
        downloader_tab = QWidget()
        downloader_layout = QVBoxLayout(downloader_tab)
        downloader_layout.setContentsMargins(16, 16, 16, 16)
        downloader_layout.setSpacing(16)
        
        # Connection settings
        connection_group = QGroupBox("Connection Settings")
        connection_group.setObjectName("settingsGroup")
        connection_layout = QGridLayout(connection_group)
        
        connection_layout.addWidget(QLabel("Maximum Connections:"), 0, 0)
        self.max_connections = QSpinBox()
        self.max_connections.setObjectName("materialSpinBox")
        self.max_connections.setRange(1, 10)
        self.max_connections.setValue(self.settings["downloader"]["max_connections"])
        self.max_connections.setMinimumHeight(40)
        connection_layout.addWidget(self.max_connections, 0, 1)
        
        downloader_layout.addWidget(connection_group)
        
        # Post-processing settings
        post_process_group = QGroupBox("Post-Processing")
        post_process_group.setObjectName("settingsGroup")
        post_process_layout = QVBoxLayout(post_process_group)
        
        self.process_audio = QCheckBox("Extract audio from videos")
        self.process_audio.setObjectName("materialCheckbox")
        self.process_audio.setChecked(self.settings["downloader"]["post_process_audio"])
        
        self.process_video = QCheckBox("Optimize video files after download")
        self.process_video.setObjectName("materialCheckbox")
        self.process_video.setChecked(self.settings["downloader"]["post_process_video"])
        
        self.add_metadata = QCheckBox("Automatically add metadata (title, artist, etc.)")
        self.add_metadata.setObjectName("materialCheckbox")
        self.add_metadata.setChecked(self.settings["downloader"]["auto_add_metadata"])
        
        post_process_layout.addWidget(self.process_audio)
        post_process_layout.addWidget(self.process_video)
        post_process_layout.addWidget(self.add_metadata)
        
        downloader_layout.addWidget(post_process_group)
        
        # Format preferences
        format_group = QGroupBox("Format Preferences")
        format_group.setObjectName("settingsGroup")
        format_layout = QGridLayout(format_group)
        
        format_layout.addWidget(QLabel("Preferred Audio Format:"), 0, 0)
        self.audio_format = QComboBox()
        self.audio_format.setObjectName("materialCombo")
        self.audio_format.addItems(["mp3", "m4a", "wav", "flac", "opus"])
        index = self.audio_format.findText(self.settings["downloader"]["preferred_audio_format"])
        if index >= 0:
            self.audio_format.setCurrentIndex(index)
        self.audio_format.setMinimumHeight(40)
        format_layout.addWidget(self.audio_format, 0, 1)
        
        format_layout.addWidget(QLabel("Preferred Video Quality:"), 1, 0)
        self.video_quality = QComboBox()
        self.video_quality.setObjectName("materialCombo")
        self.video_quality.addItem("Best Quality", "best")
        self.video_quality.addItem("720p", "720")
        self.video_quality.addItem("480p", "480")
        self.video_quality.addItem("360p", "360")
        
        index = self.video_quality.findData(self.settings["downloader"]["preferred_video_quality"])
        if index >= 0:
            self.video_quality.setCurrentIndex(index)
        self.video_quality.setMinimumHeight(40)
        format_layout.addWidget(self.video_quality, 1, 1)
        
        downloader_layout.addWidget(format_group)
        
        # Add stretch to push everything to the top
        downloader_layout.addStretch()
        
        # Add tabs to tab widget
        tabs.addTab(general_tab, "General")
        tabs.addTab(downloader_tab, "Downloader")
        
        card_layout.addWidget(tabs)
        
        # Add the card to main layout
        main_layout.addWidget(card)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        # Add cancel button on the left
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.clicked.connect(self.close)
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.setMinimumWidth(120)
        buttons_layout.addWidget(self.cancel_button)
        
        # Spacer to push save button to the right
        buttons_layout.addStretch()
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setMinimumHeight(48)
        self.save_button.setMinimumWidth(120)
        buttons_layout.addWidget(self.save_button)
        
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
            
            QGroupBox#settingsGroup {{
                border: 1px solid #dadce0;
                border-radius: 8px;
                margin-top: 16px;
                font-weight: bold;
                padding-top: 16px;
            }}
            
            QGroupBox#settingsGroup::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            
            QLabel#fieldLabel {{
                font-size: 14px;
                color: #5f6368;
            }}
            
            QLabel#locationLabel {{
                color: #5f6368;
                padding-left: 4px;
            }}
            
            QTabWidget#materialTabs::pane {{
                border: none;
                top: -1px;
            }}
            
            QTabBar::tab {{
                background: transparent;
                border: none;
                padding: 8px 12px;
                margin-right: 4px;
                color: #5f6368;
                font-weight: bold;
            }}
            
            QTabBar::tab:selected {{
                color: {primary_color};
                border-bottom: 2px solid {primary_color};
            }}
            
            QTabBar::tab:hover:!selected {{
                color: #202124;
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
            
            QSpinBox#materialSpinBox {{
                border: 1px solid #dadce0;
                border-radius: 8px;
                padding: 8px 12px;
                background: {surface};
            }}
            
            QSpinBox#materialSpinBox:focus {{
                border: 2px solid {primary_color};
            }}
            
            QSpinBox#materialSpinBox::up-button, QSpinBox#materialSpinBox::down-button {{
                width: 20px;
                border-radius: 4px;
                background: #f1f3f4;
                margin: 4px;
            }}
            
            QCheckBox#materialCheckbox {{
                spacing: 8px;
                padding: 4px;
            }}
            
            QCheckBox#materialCheckbox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid #5f6368;
                border-radius: 2px;
            }}
            
            QCheckBox#materialCheckbox::indicator:checked {{
                background-color: {primary_color};
                border-color: {primary_color};
                image: url(check.png);
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
                background-color: #f1f3f4;
                color: {on_surface};
                border: none;
                border-radius: 24px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            
            QPushButton#secondaryButton:hover {{
                background-color: #d0d0d0;
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
        """)

    def choose_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Select Default Download Folder")
        if path:
            self.location_label.setText(path)
    
    def get_settings_path(self):
        """Get the path for the settings file"""
        # Get the directory where the script is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "settings.json")
    
    def load_settings(self):
        """Load settings from JSON file"""
        settings_path = self.get_settings_path()
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    for category in loaded_settings:
                        if category in self.settings:
                            self.settings[category].update(loaded_settings[category])
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings to JSON file"""
        # Update settings from UI values
        self.settings["general"]["default_download_location"] = self.location_label.text()
        self.settings["general"]["theme"] = self.theme_combo.currentData()
        
        self.settings["downloader"]["max_connections"] = self.max_connections.value()
        self.settings["downloader"]["post_process_audio"] = self.process_audio.isChecked()
        self.settings["downloader"]["post_process_video"] = self.process_video.isChecked()
        self.settings["downloader"]["auto_add_metadata"] = self.add_metadata.isChecked()
        self.settings["downloader"]["preferred_audio_format"] = self.audio_format.currentText()
        self.settings["downloader"]["preferred_video_quality"] = self.video_quality.currentData()
        
        # Save to file
        settings_path = self.get_settings_path()
        try:
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print("Settings saved successfully")
            self.close()
        except Exception as e:
            print(f"Error saving settings: {e}")

    def closeEvent(self, event):
        print("Child window is closing")
        self.closed.emit()  # Emit the signal
        event.accept()
        super().closeEvent(event)  # Call parent to properly close dialog