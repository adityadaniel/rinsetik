# Video Download and Remix Tool

A Python toolkit for downloading videos and applying random transformations to create unique remixed versions.

## Features

### Video Downloader (`batch_download.py`)
- Batch download videos from URLs listed in a text file
- Support for audio-only downloads
- Quality selection (720p, 1080p, best)
- Automatic retry on failures
- Comment support in URL files

### Video Remixer (`remix_videos.py`)
- Apply random transformations to videos:
  - **Visual Effects**: Zoom, brightness, contrast, saturation, hue shift
  - **Audio Effects**: Volume adjustment, speed changes
  - **Advanced Effects**: Noise, sharpness, horizontal flip, padding
  - **Encoding Variations**: Bitrate adjustments, frame blending
- Metadata stripping for privacy
- Batch processing of multiple videos
- Parameter logging in JSON format

## Requirements

- Python 3.6+
- FFmpeg (for video processing)
- exiftool (optional, for enhanced metadata removal)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rinsetik.git
cd rinsetik
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install system dependencies:
```bash
# macOS
brew install ffmpeg exiftool

# Ubuntu/Debian
sudo apt-get install ffmpeg libimage-exiftool-perl

# Windows
# Download FFmpeg from https://ffmpeg.org/download.html
# Download ExifTool from https://exiftool.org/
```

## Usage

### Downloading Videos

Create a text file with URLs (one per line):
```text
https://example.com/video1
https://example.com/video2
# This is a comment
https://example.com/video3
```

Run the downloader:
```bash
# Basic usage
python batch_download.py urls.txt

# Specify output directory
python batch_download.py urls.txt -o my_videos

# Download audio only
python batch_download.py urls.txt --audio-only

# Specify quality
python batch_download.py urls.txt --quality 720
```

### Remixing Videos

Process all videos in the downloads folder:
```bash
# Process all videos in default directory
python remix_videos.py

# Specify input and output directories
python remix_videos.py -i downloads -o remixed_videos

# Process a single video
python remix_videos.py --single video.mp4

# Preview random parameters without processing
python remix_videos.py --show-params
```

## Transformation Parameters

The remixer applies random values within these ranges:

| Parameter | Range | Description |
|-----------|-------|-------------|
| zoom_factor | 1.02-1.08 | Zoom level |
| playback_speed | 0.92-1.08 | Video speed |
| saturation | 0.92-1.08 | Color saturation |
| brightness | -0.08-0.08 | Brightness adjustment |
| contrast | 0.92-1.08 | Contrast level |
| volume | 0.92-1.08 | Audio volume |
| hue_shift | -5-5 | Color hue rotation |
| noise | 0-0.02 | Visual noise |
| sharpness | 0.95-1.05 | Edge sharpness |

## Output

- **Downloaded videos**: Saved in `downloads/` directory
- **Remixed videos**: Saved in `remixed/` directory
- **Parameter logs**: JSON files with applied transformations
- **Metadata**: All metadata is stripped from remixed videos

## Project Structure

```
rinsetik/
├── batch_download.py    # Video downloader script
├── remix_videos.py       # Video remixer script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── downloads/           # Default download directory (created automatically)
└── remixed/            # Default output directory (created automatically)
```

## Notes

- The remixer creates unique versions of videos by applying random transformations
- All metadata is stripped from remixed videos for privacy
- Each remix includes a JSON file documenting the applied parameters
- Processing time depends on video length and selected transformations