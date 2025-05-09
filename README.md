# 📺 Stream Saver

A desktop application for downloading YouTube videos easily with a modern Material Design interface. ✨

<!-- ![Stream Saver](https://i.imgur.com/placeholder.png) Replace with actual screenshot -->

## ✅ Features

- 🎯 Simple and intuitive user interface with Material Design
- 🎬 Download YouTube videos in various qualities
- 🔊 Option to download video-only or audio-only formats
- 📊 Display download progress with speed and ETA information
- ⏹️ Cancel downloads in progress
- 📂 Select custom download location

## 💿 Installation

### Prerequisites

Before installing Stream Saver, make sure you have:

- 🎬 **FFmpeg** - Required for video/audio processing
  - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html) and add to PATH
  - **macOS**: Install with `brew install ffmpeg`
  - **Linux**: Install with your package manager (e.g., `sudo apt install ffmpeg`)

### Pre-built Executable

You can download the pre-built executable from the releases page:

1. 🔗 Go to the [Releases](https://github.com/imchiranjit/streamsaver/releases) page
2. ⬇️ Download the latest `StreamSaver.zip` file
3. 📦 Extract and run `app.exe`

### From Source

To run from source, you need Python 3.6 or newer:

1. 📋 Clone this repository
```
git clone https://github.com/imchiranjit/streamsaver.git cd streamsaver
```

2. 🔧 Install dependencies
```
pip install -r requirements.txt
```

3. 🚀 Run the application
```
python main.py
```

## 📝 How to Use

1. 🖱️ Launch the application
2. 📋 Paste a YouTube URL into the input field
3. 🔍 Click "Fetch" to retrieve video information
4. 🎛️ Select your preferred video quality (and audio quality if needed)
5. 📁 Choose a download location
6. ⏬ Click "Download" to start the download
7. 📈 Monitor the progress or cancel if needed

## 🧰 Dependencies

- [PyQt5](https://pypi.org/project/PyQt5/) - GUI framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube download library

## ⚖️ License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) team for the excellent YouTube download library
- Material Design for the UI inspiration

## 📬 Contact Us

Have questions, suggestions, or facing issues? We're here to help!

- 📧 Email: [im.chiranjit@outlook.com](mailto:im.chiranjit@outlook.com)
- 🌐 GitHub Issues: [Report a bug](https://github.com/imchiranjit/streamsaver/issues)