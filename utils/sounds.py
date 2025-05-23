import platform
import sys
import os

class Sounds():

    def play_system_sound(self, icon_type):
        """Play appropriate system sound for dialog type (cross-platform)"""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                self._play_windows_sound(icon_type)
            elif system == "darwin":  # macOS
                self._play_macos_sound(icon_type)
            elif system == "linux":
                self._play_linux_sound(icon_type)
            else:
                # Fallback for other systems
                self._play_fallback_sound()
                
        except Exception:
            # Silent fail if sound system is not available
            pass
    
    def _play_windows_sound(self, icon_type):
        """Play Windows system sounds using rundll32"""
        try:
            # Use rundll32 to play system sounds
            sound_map = {
                "info": "0",      # MB_OK sound
                "warning": "48",  # MB_ICONEXCLAMATION  
                "error": "16",    # MB_ICONHAND
                "question": "32"  # MB_ICONQUESTION
            }
            sound_code = sound_map.get(icon_type, "0")
            
            # This method is working - using MessageBeep with sound codes
            os.system(f'rundll32 user32.dll,MessageBeep {sound_code}')
            return True
        except Exception:
            return self._play_fallback_sound()
    
    def _play_macos_sound(self, icon_type):
        """Play macOS system sounds"""
        try:
            import subprocess
            sound_map = {
                "info": "Glass",
                "warning": "Sosumi", 
                "error": "Basso",
                "question": "Funk"
            }
            sound_name = sound_map.get(icon_type, "Glass")
            subprocess.run(["afplay", f"/System/Library/Sounds/{sound_name}.aiff"], 
                         check=False, capture_output=True)
        except (ImportError, FileNotFoundError, subprocess.SubprocessError):
            # Fallback to system beep
            try:
                import subprocess
                subprocess.run(["osascript", "-e", "beep"], check=False, capture_output=True)
            except:
                self._play_fallback_sound()
    
    def _play_linux_sound(self, icon_type):
        """Play Linux system sounds"""
        try:
            import subprocess
            
            # Try different sound systems in order of preference
            sound_commands = [
                # PulseAudio/ALSA with paplay
                self._try_paplay_sound,
                # ALSA with aplay
                self._try_aplay_sound,
                # System beep
                self._try_system_beep
            ]
            
            for sound_cmd in sound_commands:
                if sound_cmd(icon_type):
                    return
                    
        except Exception:
            self._play_fallback_sound()
    
    def _try_paplay_sound(self, icon_type):
        """Try to play sound using paplay (PulseAudio)"""
        try:
            import subprocess
            sound_map = {
                "info": "message",
                "warning": "dialog-warning", 
                "error": "dialog-error",
                "question": "dialog-question"
            }
            
            sound_name = sound_map.get(icon_type, "message")
            
            # Common sound file locations
            sound_paths = [
                f"/usr/share/sounds/freedesktop/stereo/{sound_name}.oga",
                f"/usr/share/sounds/ubuntu/stereo/{sound_name}.ogg",
                f"/usr/share/sounds/gnome/default/alerts/{sound_name}.ogg"
            ]
            
            for sound_path in sound_paths:
                try:
                    result = subprocess.run(["paplay", sound_path], 
                                          check=False, capture_output=True, timeout=2)
                    if result.returncode == 0:
                        return True
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            return False
        except:
            return False
    
    def _try_aplay_sound(self, icon_type):
        """Try to play sound using aplay (ALSA)"""
        try:
            import subprocess
            # Try system beep with different frequencies for different types
            freq_map = {
                "info": "800",
                "warning": "1000",
                "error": "400", 
                "question": "600"
            }
            freq = freq_map.get(icon_type, "800")
            
            result = subprocess.run([
                "speaker-test", "-t", "sine", "-f", freq, "-l", "1", "-s", "1"
            ], check=False, capture_output=True, timeout=1)
            
            return result.returncode == 0
        except:
            return False
    
    def _try_system_beep(self, icon_type):
        """Try system beep as fallback"""
        try:
            import subprocess
            # Number of beeps based on type
            beep_count = {
                "info": 1,
                "warning": 2,
                "error": 3,
                "question": 1
            }
            count = beep_count.get(icon_type, 1)
            
            for _ in range(count):
                subprocess.run(["beep"], check=False, capture_output=True, timeout=1)
            return True
        except:
            return False
    
    def _play_fallback_sound(self):
        """Fallback sound using Python's built-in bell character"""
        try:
            # Try terminal bell
            sys.stdout.write('\a')
            sys.stdout.flush()
        except:
            pass