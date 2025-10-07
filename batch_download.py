#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "yt-dlp",
# ]
# ///
import os
import sys
import argparse
from pathlib import Path
import yt_dlp

def download_videos(urls_file, output_dir="downloads"):
    """
    Download videos from URLs listed in a text file
    
    Args:
        urls_file: Path to text file containing URLs (one per line)
        output_dir: Directory where videos will be saved
    """
    if not os.path.exists(urls_file):
        print(f"Error: File '{urls_file}' not found")
        return False
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("No URLs found in the file")
        return False
    
    print(f"Found {len(urls)} URLs to download")
    print(f"Saving to: {output_dir}/")
    print("-" * 50)
    
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s-%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,
        'continue': True,
    }
    
    successful = 0
    failed = 0
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Downloading: {url}")
            try:
                ydl.download([url])
                successful += 1
            except Exception as e:
                print(f"   Error: {str(e)}")
                failed += 1
    
    print("\n" + "=" * 50)
    print(f"Download complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Download videos from URLs listed in a text file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python batch_download.py urls.txt
  python batch_download.py urls.txt -o my_videos
  python batch_download.py urls.txt --audio-only
  python batch_download.py urls.txt --quality 720

Text file format:
  - One URL per line
  - Lines starting with # are ignored (comments)
  - Empty lines are ignored
        """
    )
    
    parser.add_argument('urls_file', help='Path to text file containing URLs')
    parser.add_argument('-o', '--output', default='downloads', 
                        help='Output directory (default: downloads)')
    parser.add_argument('--audio-only', action='store_true',
                        help='Download audio only')
    parser.add_argument('--quality', type=str, default='best',
                        help='Video quality (e.g., 720, 1080, best)')
    
    args = parser.parse_args()
    
    if args.audio_only:
        print("Note: Audio-only mode enabled")
        ydl_opts = {
            'outtmpl': os.path.join(args.output, '%(title)s-%(id)s.%(ext)s'),
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'continue': True,
        }
    elif args.quality != 'best':
        ydl_opts = {
            'outtmpl': os.path.join(args.output, '%(title)s-%(id)s.%(ext)s'),
            'format': f'best[height<={args.quality}]/best',
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'continue': True,
        }
    else:
        ydl_opts = None
    
    if ydl_opts:
        Path(args.output).mkdir(parents=True, exist_ok=True)
        
        with open(args.urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not urls:
            print("No URLs found in the file")
            return
        
        print(f"Found {len(urls)} URLs to download")
        print(f"Saving to: {args.output}/")
        print("-" * 50)
        
        successful = 0
        failed = 0
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}] Downloading: {url}")
                try:
                    ydl.download([url])
                    successful += 1
                except Exception as e:
                    print(f"   Error: {str(e)}")
                    failed += 1
        
        print("\n" + "=" * 50)
        print(f"Download complete!")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
    else:
        download_videos(args.urls_file, args.output)

if __name__ == "__main__":
    main()