#!/usr/bin/env python3
import os
import random
import string
import subprocess
import json
from pathlib import Path
import shutil
from datetime import datetime
import argparse

class VideoRemixer:
    def __init__(self, input_dir="downloads", output_dir="remixed"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def get_random_parameters(self):
        """Generate random parameters similar to RinseTok"""
        params = {
            # Basic Adjustments
            "zoom_factor": round(random.uniform(1.02, 1.08), 2),
            "playback_speed": round(random.uniform(0.92, 1.08), 2),
            "saturation": round(random.uniform(0.92, 1.08), 2),
            "brightness": round(random.uniform(-0.08, 0.08), 2),
            "contrast": round(random.uniform(0.92, 1.08), 2),
            "volume": round(random.uniform(0.92, 1.08), 2),
            
            # Algorithm Fingerprint - Color Adjustments
            "hue_shift": round(random.uniform(-5, 5), 1),
            "gamma": round(random.uniform(0.95, 1.05), 2),
            "temperature": round(random.uniform(0.95, 1.05), 2),
            
            # Pixel Adjustments
            "noise": round(random.uniform(0, 0.02), 2),
            "sharpness": round(random.uniform(0.95, 1.05), 2),
            "blend": round(random.uniform(0, 0.01), 2),
            
            # Encoding Adjustments
            "bitrate_variation": round(random.uniform(0.95, 1.05), 2),
            "frame_blending": round(random.uniform(0, 0.25), 2),
            "time_shift": round(random.uniform(-5, 5), 1),
            
            # Additional transformations
            "remove_audio": False,  # Keep audio by default
            "flip_horizontal": random.choice([True, False]) if random.random() < 0.1 else False,
            "add_padding": random.choice([2, 4, 6, 8]) if random.random() < 0.3 else 0,
        }
        return params
    
    def build_ffmpeg_filters(self, params):
        """Build FFmpeg filter string from parameters"""
        filters = []
        
        # Zoom (crop and scale)
        if params["zoom_factor"] != 1.0:
            filters.append(f"scale=iw*{params['zoom_factor']}:ih*{params['zoom_factor']},crop=iw/{params['zoom_factor']}:ih/{params['zoom_factor']}")
        
        # Color adjustments
        eq_parts = []
        if params["brightness"] != 0:
            eq_parts.append(f"brightness={params['brightness']}")
        if params["contrast"] != 1.0:
            eq_parts.append(f"contrast={params['contrast']}")
        if params["saturation"] != 1.0:
            eq_parts.append(f"saturation={params['saturation']}")
        if params["gamma"] != 1.0:
            eq_parts.append(f"gamma={params['gamma']}")
        
        if eq_parts:
            filters.append(f"eq={':'.join(eq_parts)}")
        
        # Hue shift
        if params["hue_shift"] != 0:
            filters.append(f"hue=h={params['hue_shift']}")
        
        # Sharpness
        if params["sharpness"] != 1.0:
            unsharp_val = params["sharpness"] - 1.0
            if unsharp_val > 0:
                filters.append(f"unsharp=5:5:{unsharp_val}:5:5:0")
            else:
                filters.append(f"smartblur=1.5:{abs(unsharp_val)}:0")
        
        # Noise
        if params["noise"] > 0:
            filters.append(f"noise=alls={int(params['noise']*100)}:allf=t")
        
        # Flip horizontal
        if params["flip_horizontal"]:
            filters.append("hflip")
        
        # Add padding (letterbox effect)
        if params["add_padding"] > 0:
            pad = params["add_padding"]
            filters.append(f"pad=iw:ih+{pad*2}:0:{pad}:black")
        
        # Speed adjustment (requires setpts filter)
        if params["playback_speed"] != 1.0:
            pts_value = 1.0 / params["playback_speed"]
            filters.append(f"setpts={pts_value}*PTS")
        
        return ",".join(filters) if filters else None
    
    def build_audio_filters(self, params):
        """Build FFmpeg audio filter string"""
        audio_filters = []
        
        # Volume adjustment
        if params["volume"] != 1.0:
            audio_filters.append(f"volume={params['volume']}")
        
        # Audio speed adjustment (to match video speed)
        if params["playback_speed"] != 1.0:
            audio_filters.append(f"atempo={params['playback_speed']}")
        
        return ",".join(audio_filters) if audio_filters else None
    
    def strip_metadata(self, video_path):
        """Strip all metadata from video using exiftool"""
        try:
            # First, remove all metadata with exiftool
            exif_cmd = [
                "exiftool",
                "-all=",
                "-overwrite_original",
                str(video_path)
            ]
            
            result = subprocess.run(exif_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ Metadata stripped with exiftool")
                return True
            else:
                print(f"  ⚠ Warning: Could not strip metadata with exiftool: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ⚠ Warning: exiftool not available or error: {str(e)}")
            return False
    
    def process_video(self, input_path, params=None):
        """Process a single video with FFmpeg and strip metadata"""
        if params is None:
            params = self.get_random_parameters()
        
        input_file = Path(input_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        output_filename = f"remix_{timestamp}_{random_suffix}.mp4"
        output_path = self.output_dir / output_filename
        
        # Build FFmpeg command with metadata stripping options
        cmd = ["ffmpeg", "-i", str(input_file), "-y"]
        
        # Add metadata stripping options for FFmpeg
        cmd.extend([
            "-map_metadata", "-1",  # Strip all metadata
            "-fflags", "+bitexact",  # Make output deterministic
            "-flags:v", "+bitexact",
            "-flags:a", "+bitexact",
        ])
        
        # Add video filters
        video_filters = self.build_ffmpeg_filters(params)
        if video_filters:
            cmd.extend(["-vf", video_filters])
        
        # Add audio filters or remove audio
        if params["remove_audio"]:
            cmd.append("-an")
        else:
            audio_filters = self.build_audio_filters(params)
            if audio_filters:
                cmd.extend(["-af", audio_filters])
        
        # Encoding parameters with bitrate variation
        base_bitrate = "2M"
        if params["bitrate_variation"] != 1.0:
            # Adjust bitrate
            bitrate_value = int(2000 * params["bitrate_variation"])
            base_bitrate = f"{bitrate_value}k"
        
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", str(random.randint(20, 24)),
            "-b:v", base_bitrate,
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            # Additional metadata stripping
            "-metadata", "title=",
            "-metadata", "author=",
            "-metadata", "comment=",
            "-metadata", "description=",
            "-metadata", "synopsis=",
            "-metadata", "show=",
            "-metadata", "episode_id=",
            "-metadata", "network=",
            "-metadata", "company=",
            str(output_path)
        ])
        
        print(f"\nProcessing: {input_file.name}")
        print(f"Output: {output_filename}")
        print("\nApplied parameters:")
        for key, value in params.items():
            if value != 1.0 and value != 0 and value is not False:
                print(f"  {key}: {value}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Successfully processed: {output_filename}")
                
                # Strip metadata with exiftool as a second pass
                self.strip_metadata(output_path)
                
                # Save parameters to JSON for reference
                params_file = self.output_dir / f"{output_filename}.json"
                with open(params_file, 'w') as f:
                    json.dump(params, f, indent=2)
                
                return True, output_path
            else:
                print(f"✗ Error processing video: {result.stderr}")
                return False, None
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False, None
    
    def process_all_videos(self):
        """Process all videos in the input directory"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(self.input_dir.glob(f"*{ext}"))
        
        if not video_files:
            print(f"No video files found in {self.input_dir}")
            return
        
        print(f"Found {len(video_files)} video(s) to process")
        print("=" * 50)
        
        successful = 0
        failed = 0
        
        for video_file in video_files:
            success, _ = self.process_video(video_file)
            if success:
                successful += 1
            else:
                failed += 1
            print("-" * 50)
        
        print("\n" + "=" * 50)
        print(f"Processing complete!")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Output directory: {self.output_dir}")

def main():
    parser = argparse.ArgumentParser(
        description='Remix TikTok videos by applying random transformations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script applies random transformations to videos similar to RinseTok:
- Adjusts zoom, playback speed, colors, and audio
- Adds noise, sharpness, and other effects
- Modifies encoding parameters
- STRIPS ALL METADATA using FFmpeg and exiftool
- Saves remixed videos with completely clean metadata

Examples:
  python remix_videos.py
  python remix_videos.py -i downloads -o remixed_videos
  python remix_videos.py --single video.mp4
  python remix_videos.py --show-params
        """
    )
    
    parser.add_argument('-i', '--input', default='downloads',
                        help='Input directory containing videos (default: downloads)')
    parser.add_argument('-o', '--output', default='remixed',
                        help='Output directory for remixed videos (default: remixed)')
    parser.add_argument('--single', type=str,
                        help='Process a single video file')
    parser.add_argument('--show-params', action='store_true',
                        help='Show random parameters without processing')
    
    args = parser.parse_args()
    
    remixer = VideoRemixer(args.input, args.output)
    
    if args.show_params:
        params = remixer.get_random_parameters()
        print("Random parameters that would be applied:")
        print(json.dumps(params, indent=2))
    elif args.single:
        if not os.path.exists(args.single):
            print(f"Error: File '{args.single}' not found")
            return
        remixer.process_video(args.single)
    else:
        remixer.process_all_videos()

if __name__ == "__main__":
    main()