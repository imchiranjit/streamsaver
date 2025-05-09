import yt_dlp
from PyQt5.QtCore import QThread, pyqtSignal

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