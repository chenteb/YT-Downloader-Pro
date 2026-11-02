# 🎬 YT Downloader Pro

A desktop application developed in Python for Windows that allows you to download videos and audio from multiple platforms easily, quickly, and **verifying the integrity of each file**.

**[Leer en Español](README_esp.md)**

<!-- Optional: Upload a screenshot of your app to GitHub and uncomment the following line -->
<!-- ![App Demo](screenshot.png) -->

## ✨ Features

- **User-Friendly GUI:** Easy to use, no command line required.
- **Multi-platform:** Compatible with thousands of sites (YouTube, Vimeo, Facebook, Twitter, TikTok, etc.) thanks to `yt-dlp`.
- **Auto-Detection:** The built-in analyzer tells you which platform the link comes from.
- **Quality Selection:** Choose from available resolutions or download audio only.
- **Audio Download (MP3):** Extract the audio track in MP3 format at 192 kbps.
- **Playlist Support:** Download complete playlists (saved in a subfolder).
- **Integrity Verification:** Uses a `yt-dlp` plugin and `FFmpeg` to ensure the downloaded file is not corrupted or incomplete.
- **Persistent History:** Keeps a log of completed downloads (`historial.json`).
- **Verification Log:** Generates a text file (`registro_verificacion.txt`) confirming that files passed the integrity test.

## 🚀 Prerequisites

1. **Python 3.9+** (only if running from source).
2. **FFmpeg** (Mandatory): Required to download high resolutions (720p+), convert to MP3, and perform integrity verification. 
   - Download it from [ffmpeg.org](https://ffmpeg.org/download.html) and make sure to add the `bin` folder to your Windows Environment Variables (PATH).

## 🛠️ Installation and Usage (From Source)

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YT-Downloader-Pro.git
   cd YT-Downloader-Pro

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Run the application:
   ```bash
   python yt_downloader_pro_v3.3.py


📦 Compiling as an Executable (.exe)
If you want to generate your own Windows executable file:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller

2. Run the following command in the project root:
   ```bash
   pyinstaller --onefile --noconsole --icon=app_icon.ico --add-data "app_icon.ico;." --name "YTDownloaderPro" yt_downloader_pro_v3.3.py

3. The executable will be available in the dist/ folder.

💡 Notes and Known Limitations
   Empty titles on some platforms: When analyzing certain links (for example, some Facebook Reels or Instagram videos), the platform might not expose the title tag. In these cases, the app will display "(sin título)" [no title] in the interface, but this is not a problem: you can manually type your desired name in the "Name" field before downloading, and the application will respect it perfectly.

   DRM-protected sites: Paid streaming platforms like Netflix, Disney+, or Hulu use DRM protection. This tool cannot download from those sites.

   Platform updates: If a website suddenly stops working, it's likely because they changed their code. Updating yt-dlp (pip install -U yt-dlp) usually fixes the issue.

⚠️ Legal Disclaimer
   This tool is intended for educational purposes and for downloading your own or public domain content. The user is responsible for complying with the Terms of Service of the platforms (such as YouTube) and the copyright laws of their country. The developer is not responsible for any misuse of this software.