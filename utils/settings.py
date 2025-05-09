import json
import os

class Settings:
    def __init__(self):
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        self.default_settings = {
            "general": {
                "default_download_location": os.path.join(os.path.expanduser("~"), "Downloads"),
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
        self.settings = {}
        self.load()

    def load(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.default_settings.copy()
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.default_settings.copy()

    def __save_settings__(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    # Getters and Setters for each setting
    def __get_setting__(self, section, key):
        return self.settings.get(section, {}).get(key, None)
    
    def __set_setting__(self, section, key, value):
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value

    def save(self):
        self.__save_settings__()

    def get_default_download_location(self):
        return self.__get_setting__('general', 'default_download_location')
    def set_default_download_location(self, value):
        self.__set_setting__('general', 'default_download_location', value)
    def get_theme(self):
        return self.__get_setting__('general', 'theme')
    def set_theme(self, value):
        self.__set_setting__('general', 'theme', value)
    def get_max_connections(self):
        return self.__get_setting__('downloader', 'max_connections')
    def set_max_connections(self, value):
        self.__set_setting__('downloader', 'max_connections', value)
    def get_post_process_audio(self):
        return self.__get_setting__('downloader', 'post_process_audio')
    def set_post_process_audio(self, value):
        self.__set_setting__('downloader', 'post_process_audio', value)
    def get_post_process_video(self):
        return self.__get_setting__('downloader', 'post_process_video')
    def set_post_process_video(self, value):
        self.__set_setting__('downloader', 'post_process_video', value)
    def get_preferred_audio_format(self):
        return self.__get_setting__('downloader', 'preferred_audio_format')
    def set_preferred_audio_format(self, value):
        self.__set_setting__('downloader', 'preferred_audio_format', value)
    def get_preferred_video_quality(self):
        return self.__get_setting__('downloader', 'preferred_video_quality')
    def set_preferred_video_quality(self, value):
        self.__set_setting__('downloader', 'preferred_video_quality', value)
    def get_auto_add_metadata(self):
        return self.__get_setting__('downloader', 'auto_add_metadata')
    def set_auto_add_metadata(self, value):
        self.__set_setting__('downloader', 'auto_add_metadata', value)