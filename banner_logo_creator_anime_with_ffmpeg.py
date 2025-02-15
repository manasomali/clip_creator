import os
import subprocess
import re
from tqdm import tqdm

INPUT_DIRECTORY: str = "G:/tiktok_dark/triploedits/edits/Maso Mesu Soap De Aimashou_02_music"
OUTPUT_DIRECTORY: str = "G:/tiktok_dark/triploedits/edits/Maso Mesu Soap De Aimashou_02_music_out"
OVERLAY_IMAGE_PATH = "G:/tiktok_dark/triploedits/edits/assets/today-animations.png"
FONT_PATH="G\:/tiktok_dark/triploedits/edits/assets/BebasNeue-Bold.ttf"
IMG_HEIGHT = 290
TEXT_HEIGHT = 370
FONT_SIZE = 80
CUDA = True

TITLE: str = "Maso Mesu Soap De Aimashou Ep. 02"

def overlay_png_on_videos(input_dir, output_dir, overlay_image):
    """
    Applies FFmpeg overlay command to all MP4 files in input_dir and saves output to output_dir.
    
    Args:
        input_dir (str): Directory containing MP4 files.
        output_dir (str): Directory to save processed videos.
        overlay_image (str): Path to the PNG overlay image.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    mp4_files = [f for f in os.listdir(input_dir) if f.endswith((".mp4", ".mkv"))]
    mp4_files = sorted(mp4_files, key=lambda x:float(re.findall("(\d+)",x)[0]))

    if not mp4_files:
        print("No MP4 files found in the input directory.")
        return
    part = 1
    for file in tqdm(mp4_files, desc="Processing videos", unit="file"):
        input_path = f"{input_dir}/{file}"
        output_path = f"{output_dir}/{file}"

        first_line = TITLE.upper()
        second_line = f"PARTE {part}"

        second_text_height = TEXT_HEIGHT + 120
        if CUDA:
            cmd = [
                "ffmpeg", "-hwaccel", "cuda",
                "-i", input_path,
                "-i", overlay_image,
                "-filter_complex",
                f"[0:v]drawtext=fontfile='{FONT_PATH}':"
                f"text='{first_line}': fontcolor=black: fontsize={FONT_SIZE}: "
                f"box=1: boxcolor=white: boxborderw=40|500: x=(W-tw)/2: y={TEXT_HEIGHT}, "
                f"drawtext=fontfile='{FONT_PATH}':"
                f"text='{second_line}': fontcolor=black: fontsize={FONT_SIZE}: "
                f"box=1: boxcolor=white: boxborderw=40|500: x=(W-tw)/2: y={second_text_height}[txt]; "
                f"[txt][1:v]overlay=x=(W-w)/2:y=(H-h-{IMG_HEIGHT})[out]",
                "-map", "[out]", "-map", "0:a",
                "-c:v", "h264_nvenc", "-cq", "20", "-preset", "fast",
                "-c:a", "copy", output_path, "-y"
            ]
        else:
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-i", overlay_image,
                "-filter_complex",
                f"[0:v]drawtext=fontfile='{FONT_PATH}':"
                f"text='{first_line}': fontcolor=black: fontsize={FONT_SIZE}: "
                f"box=1: boxcolor=white: boxborderw=50|500: x=(W-tw)/2: y={TEXT_HEIGHT}, "
                f"drawtext=fontfile='{FONT_PATH}':"
                f"text='{second_line}': fontcolor=black: fontsize={FONT_SIZE}: "
                f"box=1: boxcolor=white: boxborderw=50|500: x=(W-tw)/2: y={second_text_height}[txt]; "
                f"[txt][1:v]overlay=x=(W-w)/2:y=(H-h-{IMG_HEIGHT})[out]",
                "-map", "[out]", "-map", "0:a",
                "-c:a", "copy", output_path, "-y"
            ]
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        part += 1
    
    print("Processing complete!")


if __name__ == "__main__":
    overlay_png_on_videos(INPUT_DIRECTORY, OUTPUT_DIRECTORY, OVERLAY_IMAGE_PATH)
