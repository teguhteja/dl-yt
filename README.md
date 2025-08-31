# dl-yt - YouTube Video Downloader

A Python script for downloading YouTube videos with advanced features including fallback format selection, transcript download, and robust error handling.

## Features

- **Multiple Format Support**: Downloads audio (m4a) and video (mp4) separately, then combines them
- **Smart Fallback**: Automatically tries different quality codes if primary ones fail
- **Format Detection**: Uses `--list-formats` to find the best available quality
- **Transcript Download**: Support for TXT and SRT subtitle formats using YouTube Transcript API
- **Error Handling**: Handles HTTP 403 errors and other download failures gracefully
- **Batch Processing**: Process multiple YouTube links from a text file
- **Cookie Support**: Uses cookies for authenticated downloads

## Installation

1. Install required dependencies:
```bash
pip install youtube-transcript-api
```

2. Install yt-dlp:
```bash
pip install yt-dlp
```

3. Install ffmpeg (for combining audio/video):
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## Usage

### Basic Usage
```bash
python dl-yt-720.py -f your-links.txt
```

### Command Line Options

- `-f, --file`: File containing YouTube links (default: t-yt-dl.txt)
- `--folder`: Working directory (default: current directory)
- `-sl, --sub-lang`: Subtitle language (default: en)
- `-c, --cookies`: Path to cookies file (default: ./cookies.txt)
- `-ca, --code-audio`: Audio format code (default: 140)
- `-cv, --code-video`: Video format code (default: 136)
- `-ea, --ext-audio`: Audio file extension (default: m4a)
- `-ev, --ext-video`: Video file extension (default: mp4)
- `--download-txt`: Download transcripts as TXT format
- `--download-srt`: Download transcripts as SRT format
- `-is, --is-search`: Enable format search mode

### Example Commands

```bash
# Basic download
python dl-yt-720.py -f my-videos.txt

# Download with transcripts
python dl-yt-720.py -f my-videos.txt --download-srt --download-txt

# Custom cookies and language
python dl-yt-720.py -f my-videos.txt -c /path/to/cookies.txt -sl id

# Specify working folder
python dl-yt-720.py --folder /path/to/downloads -f links.txt
```

## File Format

Create a text file with YouTube URLs (one per line):
```
https://www.youtube.com/watch?v=VIDEO_ID1
https://www.youtube.com/watch?v=VIDEO_ID2
https://www.youtube.com/watch?v=VIDEO_ID3
```

## How It Works

1. **Primary Download**: Tries to download with codes 140 (audio) and 136 (video)
2. **Fallback**: If primary codes fail, runs `--list-formats` to find available formats
3. **Smart Selection**: Chooses the highest quality available:
   - Audio: Prefers code 234 over 140 (higher bitrate mp4)
   - Video: Prefers code 398 over 298 (720p60 mp4_dash with highest code)
4. **Combination**: Uses ffmpeg to combine audio and video into final MP4
5. **Cleanup**: Removes temporary audio/video files and comments out processed links

## Error Handling

- **HTTP 403 Errors**: Automatically skips videos with access restrictions
- **Missing Formats**: Falls back to available quality options
- **Failed Downloads**: Provides detailed error messages and continues to next video
- **File Conflicts**: Handles existing files and temporary file management

## Requirements

- Python 3.6+
- yt-dlp
- ffmpeg
- youtube-transcript-api

## Notes

- Processed YouTube links are commented out in the input file to prevent re-downloading
- Failed downloads are not commented out, allowing for retry attempts
- Cookies file is recommended for accessing private/restricted videos
- The script automatically creates temporary files during the combination process
