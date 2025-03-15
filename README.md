Below is a sample README.md you can include in your GitHub repository:

---

# Youtube MP4/MP3 Extractor

This application lets you download and convert videos from a provided URL to MP3 or MP4 format using a modern, dark-themed GUI. It uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for media extraction and automatically handles FFmpeg installation if needed.

## Features

- **Download Options:** Choose between MP3 (audio only) and MP4 (video) downloads.
- **Modern GUI:** Enjoy a sleek black and purple-themed interface.
- **Automatic FFmpeg Setup:** If running from the source, the app will install FFmpeg on first download.
- **Fetch Video Info:** View video title, uploader, and duration before downloading.
- **Graceful Cancellation:** Cancel an in-progress download safely.
- **Standalone Executable:** A pre-built executable is available for those who prefer not to build from source.

## Getting Started

### Using the Pre-built Executable

If you prefer not to build the project yourself, you can download the executable from our [Releases page](https://github.com/jemmonsss/Youtube-MP4-MP3-Extractor/releases/download/tag/Youtube-MP4-MP3-Extractor.exe).

- **Note:** The EXE from the Releases already has FFmpeg bundled. Simply run the EXE and you’re ready to go!

### Building from Source

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/jemmonsss/Youtube-MP4-MP3-Extractor.git
   cd Youtube-MP4-MP3-Extractor
   ```

2. **Install Dependencies:**

   Make sure you have Python installed. Then run:
   
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**

   ```bash
   python main.py
   ```

   When running from the main branch, click the **Download** button once to trigger the FFmpeg installation. This step ensures that FFmpeg is automatically downloaded into the `scripts` folder if it isn’t already present.

## Packaging to an Executable

You can build your own executable using [PyInstaller](https://pyinstaller.org/). For example, run:

```bash
python -m PyInstaller --onefile --windowed --add-data "scripts;scripts" --icon="jslogo.png" main.py
```

This command bundles the application and its resources (including the `scripts` folder containing FFmpeg) into a single executable.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests with improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).

---

This README explains the project, provides instructions for both using the pre-built executable and building from source, and clarifies the FFmpeg installation behavior. You can adjust the text as needed for your project.
