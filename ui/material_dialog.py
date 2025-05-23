from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from utils.sounds import Sounds

class MaterialDialog(QDialog):
    def __init__(self, parent=None, title="", message="", icon_type="info", 
                 buttons=("OK",), default_button=0):
        """
        A themed dialog box matching the Stream Saver design.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Main message text
            icon_type: 'info', 'warning', 'error', or 'question'
            buttons: Tuple of button labels
            default_button: Index of default button
        """
        super().__init__(parent)
        self.icon_type = icon_type
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setMinimumWidth(400)
        self.result_value = None
        self.button_values = {}
        
        # Map of button values to return values (similar to QMessageBox)
        self.BUTTON_ROLE_MAP = {
            "OK": 0,
            "Cancel": 1,
            "Yes": 2,
            "No": 3,
            "Abort": 4,
            "Retry": 5,
            "Ignore": 6
        }
        
        self.setup_ui(title, message, icon_type, buttons, default_button)
        self.apply_styles()
        
    def setup_ui(self, title, message, icon_type, buttons, default_button):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create card container
        card = QFrame()
        card.setObjectName("dialogCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 4)
        header_layout.setSpacing(16)
        
        # Icon
        icon_label = QLabel()
        icon_label.setObjectName(f"icon{icon_type.capitalize()}")
        icon_label.setMinimumSize(48, 48)
        icon_label.setMaximumSize(48, 48)
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignVCenter)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        card_layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(message)
        message_label.setObjectName("dialogMessage")
        message_label.setWordWrap(True)
        message_label.setMinimumWidth(350)
        message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        message_font = QFont()
        message_font.setPointSize(11)
        message_label.setFont(message_font)
        message_label.setContentsMargins(0, 0, 0, 12)  # Add some space below message
        card_layout.addWidget(message_label)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.setSpacing(8)  # Reduce spacing between buttons
        
        for i, button_text in enumerate(buttons):
            button = QPushButton(button_text)
            
            # Determine button style based on text and position
            if button_text in ["Cancel", "No", "Close"]:
                button.setObjectName("secondaryButton")
            elif i == default_button or button_text in ["OK", "Yes"]:
                button.setObjectName("primaryButton")
                self.setFocus()
            else:
                button.setObjectName("outlineButton")
            
            # Store button value for result
            button_value = self.BUTTON_ROLE_MAP.get(button_text, i)
            self.button_values[button] = button_value
            
            # Set as default if specified
            if i == default_button:
                button.setDefault(True)
            
            # Connect button click
            button.clicked.connect(self.button_clicked)
            button_layout.addWidget(button)
        
        card_layout.addLayout(button_layout)
        main_layout.addWidget(card)
        self.setLayout(main_layout)
        
    def button_clicked(self):
        sending_button = self.sender()
        self.result_value = self.button_values.get(sending_button, 0)
        self.accept()
        
    def apply_styles(self):
        # Material Design 3 inspired color palette - matching your main app
        primary_color = "#1a73e8"  # Blue
        primary_variant = "#0d47a1"
        on_surface = "#202124" 
        surface = "#ffffff"
        error_color = "#b00020"
        warning_color = "#FF9800"
        info_color = "#1a73e8"
        question_color = "#673AB7"
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #f8f9fa;
            }}
            
            QFrame#dialogCard {{
                background-color: {surface};
                border-radius: 12px;
                border: 1px solid #dadce0;
            }}
            
            QLabel {{
                color: {on_surface};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}

            QLabel#dialogTitle, QLabel#dialogMessage {{
                background-color: transparent;
            }}
            
            QLabel#iconInfo {{
                min-width: 48px;
                min-height: 48px;
                max-width: 48px;
                max-height: 48px;
                border-radius: 24px;
                qproperty-text: "i";
                font-size: 24px;
                font-weight: bold;
                color: {info_color};
                padding: 0px;
                margin: 0px;
                text-align: center;
            }}
            
            QLabel#iconWarning {{
                min-width: 48px;
                min-height: 48px;
                max-width: 48px;
                max-height: 48px;
                border-radius: 24px;
                qproperty-text: "!";
                font-size: 24px;
                font-weight: bold;
                color: {warning_color};
                padding: 0px;
                margin: 0px;
                text-align: center;
            }}
            
            QLabel#iconError {{
                min-width: 48px;
                min-height: 48px;
                max-width: 48px;
                max-height: 48px;
                border-radius: 24px;
                qproperty-text: "×";
                font-size: 24px;
                font-weight: bold;
                color: {error_color};
                padding: 0px;
                margin: 0px;
                text-align: center;
            }}
            
            QLabel#iconQuestion {{
                min-width: 48px;
                min-height: 48px;
                max-width: 48px;
                max-height: 48px;
                border-radius: 24px;
                qproperty-text: "?";
                font-size: 24px;
                font-weight: bold;
                color: {question_color};
                padding: 0px;
                margin: 0px;
                text-align: center;
            }}
                        
            QPushButton#primaryButton {{
                background-color: {primary_color};
                color: white;
                border: none;
                border-radius: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 6px 12px;
                min-width: 64px;
                max-height: 28px;
            }}
            
            QPushButton#primaryButton:hover {{
                background-color: {primary_variant};
            }}
            
            QPushButton#secondaryButton {{
                background-color: transparent;
                color: #ed5e68;
                border: none;
                border-radius: 14px;
                border: 1px solid #ed5e68;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 6px 12px;
                min-width: 64px;
                max-height: 28px;
            }}
            
            QPushButton#secondaryButton:hover {{
                background-color: rgba(244, 67, 54, 0.1);
            }}
            
            QPushButton#outlineButton {{
                background-color: {surface};
                color: {primary_color};
                border: 1px solid {primary_color};
                border-radius: 4px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 6px 12px;
                min-width: 64px;
                max-height: 28px;
            }}
            
            QPushButton#outlineButton:hover {{
                background-color: #e8f0fe;
            }}
        """)

    def showEvent(self, event):
        """Override showEvent to play sound when dialog becomes visible"""
        super().showEvent(event)
        try:
            # Play sound after dialog is shown
            sounds = Sounds()
            sounds.play_system_sound(self.icon_type)
        except Exception as e:
            print("Error playing sound:", str(e))
    
    @staticmethod
    def info(parent, title, message, buttons=("OK",), default_button=0):
        """Show an information dialog"""
        dialog = MaterialDialog(parent, title, message, "info", buttons, default_button)
        dialog.exec_()
        return dialog.result_value
        
    @staticmethod
    def warning(parent, title, message, buttons=("OK",), default_button=0):
        """Show a warning dialog"""
        dialog = MaterialDialog(parent, title, message, "warning", buttons, default_button)
        dialog.exec_()
        return dialog.result_value
    
    @staticmethod
    def error(parent, title, message, buttons=("OK",), default_button=0):
        """Show an error dialog"""
        dialog = MaterialDialog(parent, title, message, "error", buttons, default_button)
        dialog.exec_()
        return dialog.result_value
    
    @staticmethod
    def question(parent, title, message, buttons=("Yes", "No"), default_button=1):
        """Show a question dialog"""
        dialog = MaterialDialog(parent, title, message, "question", buttons, default_button)
        dialog.exec_()
        return dialog.result_value