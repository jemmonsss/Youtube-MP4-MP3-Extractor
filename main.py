#!/usr/bin/env python3
import sys
import os
import subprocess
import zipfile
import io
import shutil
import platform
import requests  # pip install requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QRadioButton, QFileDialog, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import yt_dlp

def ensure_ffmpeg():
    """
    Ensure that ffmpeg.exe exists in the 'scripts' directory relative to this script.
    If not found, download and extract it from a prebuilt Windows release.
    Returns the path to ffmpeg.exe or None on failure.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(script_dir, "scripts")
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path

    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    # URL for the FFmpeg essentials build (from Gyan's builds)
    zip_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    try:
        print("Downloading FFmpeg...")
        response = requests.get(zip_url)
        if response.status_code != 200:
            raise Exception("Failed to download FFmpeg: status code " + str(response.status_code))
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            candidate = None
            for f in z.namelist():
                if f.endswith("ffmpeg.exe") and ("bin/" in f or "bin\\" in f):
                    candidate = f
                    break
            if candidate is None:
                raise Exception("ffmpeg.exe not found in the downloaded zip archive.")
            
            z.extract(candidate, path=ffmpeg_dir)
            extracted_path = os.path.join(ffmpeg_dir, candidate)
            shutil.move(extracted_path, ffmpeg_path)
            extracted_folder = os.path.join(ffmpeg_dir, candidate.split("/")[0])
            if os.path.exists(extracted_folder):
                shutil.rmtree(extracted_folder, ignore_errors=True)
        print("FFmpeg downloaded and installed to:", ffmpeg_path)
        return ffmpeg_path
    except Exception as e:
        print("Error downloading FFmpeg:", e)
        return None

class DownloadWorker(QThread):
    progress = pyqtSignal(float)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, download_format, output_path, ffmpeg_path):
        super().__init__()
        self.url = url
        self.download_format = download_format
        self.output_path = output_path
        self.ffmpeg_path = ffmpeg_path
        self.cancelled = False  # Cancellation flag

    def cancel(self):
        self.cancelled = True

    def run(self):
        ydl_opts = {
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.my_hook],
            'quiet': True,
            'ffmpeg_location': self.ffmpeg_path
        }
        if self.download_format == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif self.download_format == 'mp4':
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit("Download finished!")
        except Exception as e:
            if "Download cancelled by user" in str(e):
                self.finished.emit("Download cancelled.")
            else:
                self.error.emit(str(e))

    def my_hook(self, d):
        if self.cancelled:
            # Raise an exception to cancel the download gracefully
            raise Exception("Download cancelled by user.")
        if d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total:
                progress_value = d.get('downloaded_bytes', 0) / total * 100
                self.progress.emit(progress_value)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None  # To hold the current download thread
        self.setWindowTitle("Media Downloader")
        self.setGeometry(300, 300, 600, 450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # URL Input
        self.url_label = QLabel("Enter URL:")
        self.url_input = QLineEdit()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # Format Selection
        format_layout = QHBoxLayout()
        self.mp3_radio = QRadioButton("MP3")
        self.mp3_radio.setChecked(True)
        self.mp4_radio = QRadioButton("MP4")
        format_layout.addWidget(QLabel("Select Format:"))
        format_layout.addWidget(self.mp3_radio)
        format_layout.addWidget(self.mp4_radio)
        layout.addLayout(format_layout)

        # Output Directory
        out_layout = QHBoxLayout()
        self.out_label = QLabel("Save to:")
        self.out_path = QLineEdit(os.getcwd())
        self.out_button = QPushButton("Browse")
        self.out_button.clicked.connect(self.browse_folder)
        out_layout.addWidget(self.out_label)
        out_layout.addWidget(self.out_path)
        out_layout.addWidget(self.out_button)
        layout.addLayout(out_layout)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        btn_layout.addWidget(self.download_button)
        
        self.cancel_button = QPushButton("Cancel Download")
        self.cancel_button.clicked.connect(self.cancel_download)
        btn_layout.addWidget(self.cancel_button)
        
        self.info_button = QPushButton("Fetch Info")
        self.info_button.clicked.connect(self.fetch_info)
        btn_layout.addWidget(self.info_button)
        
        layout.addLayout(btn_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        # Modern black and purple-themed stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #000;
                color: #e0e0e0;
                font-family: Arial, sans-serif;
            }
            QLineEdit, QTextEdit {
                background-color: #333;
                border: 1px solid #555;
                padding: 5px;
            }
            QPushButton {
                background-color: #660066;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #990099;
            }
            QProgressBar {
                border: 1px solid #555;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #800080;
            }
        """)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.out_path.text())
        if folder:
            self.out_path.setText(folder)

    def start_download(self):
        self.log_output.append("Checking for FFmpeg in the scripts directory...")
        ffmpeg_path = ensure_ffmpeg()
        if ffmpeg_path is None:
            self.log_output.append("Error: FFmpeg could not be installed automatically.")
            return

        try:
            subprocess.run([ffmpeg_path, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            self.log_output.append("FFmpeg check passed using the scripts directory.")
        except Exception as e:
            self.log_output.append("Error: FFmpeg is not accessible from the scripts directory. " + str(e))
            return

        url = self.url_input.text().strip()
        if not url:
            self.log_output.append("Please enter a valid URL.")
            return

        download_format = 'mp3' if self.mp3_radio.isChecked() else 'mp4'
        output_path = self.out_path.text().strip()

        self.worker = DownloadWorker(url, download_format, output_path, ffmpeg_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.download_finished)
        self.worker.error.connect(self.download_error)
        self.worker.start()
        self.log_output.append("Starting download...")

    def cancel_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()  # Set the cancellation flag
            self.log_output.append("Cancelling download...")
        else:
            self.log_output.append("No active download to cancel.")

    def fetch_info(self):
        url = self.url_input.text().strip()
        if not url:
            self.log_output.append("Please enter a valid URL to fetch info.")
            return
        try:
            self.log_output.append("Fetching video info...")
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            title = info.get('title', 'N/A')
            uploader = info.get('uploader', 'N/A')
            duration = info.get('duration', 0)
            self.log_output.append(f"Title: {title}\nUploader: {uploader}\nDuration: {duration} seconds")
        except Exception as e:
            self.log_output.append("Error fetching info: " + str(e))

    def update_progress(self, value):
        self.progress_bar.setValue(int(value))
        self.log_output.append(f"Download progress: {value:.2f}%")

    def download_finished(self, message):
        self.log_output.append(message)
        self.progress_bar.setValue(100)

    def download_error(self, error_message):
        self.log_output.append("Error: " + error_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
