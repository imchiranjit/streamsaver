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
            raise Exception("Download cancelled by user")
            
        if d['status'] == 'downloading':
            size = d.get('total_bytes', d.get('total_bytes_estimate', 0))
            percent = d.get('downloaded_bytes', 0) / size * 100
            if percent:
                # Convert to float if it's not None and clamp between 0-100
                percent = float(percent) if percent is not None else 0
                percent = max(0, min(percent, 100))
                
                # Format download info
                speed = d.get('speed', 0)
                if speed:
                    # Convert speed to MB/s or KB/s or Bytes/s
                    if speed > 1024 * 1024 * 1024:
                        speed_str = f"{speed/1024/1024/1024:.2f} GiB/s"
                    elif speed > 1024 * 1024:
                        speed_str = f"{speed/1024/1024:.2f} MiB/s"
                    elif speed > 1024:
                        speed_str = f"{speed/1024:.2f} KiB/s"
                    else:
                        speed_str = f"{speed:.2f} Bytes/s"
                else:
                    speed_str = "calculating..."

                if size:
                    # Convert size to MiB or GiB or KiB or Bytes
                    if size > 1024 * 1024 * 1024:
                        size_str = f"{size/1024/1024/1024:.2f} GiB"
                    elif size > 1024 * 1024:
                        size_str = f"{size/1024/1024:.2f} MiB"
                    elif size > 1024:
                        size_str = f"{size/1024:.2f} KiB"
                    else:
                        size_str = f"{size:.2f} Bytes"
                else:
                    size_str = "calculating..."
                
                eta = int(d.get('eta', 0))
                if eta:
                    # Convert eta to (seconds or minutes seconds or hours minutes)
                    if eta > 3600:
                        eta_str = f"ETA: {eta//3600}h {eta%3600//60}m"
                    elif eta > 60:
                        eta_str = f"ETA: {eta//60}m {eta%60}s"
                    else:
                        eta_str = f"ETA: {eta}s"
                else:
                    eta_str = "calculating..."
                
                status = f"{percent:.1f}% ~ {size_str} | {speed_str} | {eta_str}"
                self.progress.emit(percent, status)