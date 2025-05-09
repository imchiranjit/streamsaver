import yt_dlp
from PyQt5.QtCore import QThread, pyqtSignal

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