import os
import subprocess
from tqdm import tqdm

INPUT_DIRECTORY = "G:/tiktok_dark/triploedits/edits/Como Não Perder Essa Mulher"
OUTPUT_DIRECTORY = "G:/tiktok_dark/triploedits/edits/Como Não Perder Essa Mulher_out_triploedits"
OVERLAY_IMAGE_PATH = "G:/tiktok_dark/triploedits/edits/assets/triploedits.png"
#IMG_HEIGHT = 175
IMG_HEIGHT = 270
#TEXT_HEIGHT = 230
TEXT_HEIGHT = 350
FONT_PATH="G\:/tiktok_dark/triploedits/edits/assets/BebasNeue-Bold.ttf"
FONT_SIZE = 80
CUDA = True

def overlay_png_on_videos(input_dir, output_dir, overlay_image):
    """
    Applies FFmpeg overlay command to all MP4 files in input_dir and saves output to output_dir.
    
    Args:
        input_dir (str): Directory containing MP4 files.
        output_dir (str): Directory to save processed videos.
        overlay_image (str): Path to the PNG overlay image.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    mp4_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.mkv'))]
    
    if not mp4_files:
        print("No MP4 files found in the input directory.")
        return
    for file in tqdm(mp4_files, desc="Processing videos", unit="file"):
        input_path = f"{input_dir}/{file}"
        output_path = f"{output_dir}/{file}"
        txt_path = f"{input_dir}/{file.replace(".mp4",".txt").replace(".mkv",".txt")}"

        with open(txt_path, 'r', encoding='utf-8') as file:
            sentence = file.read().strip()
        
        uppercase_text = sentence.upper()
        words = uppercase_text.split()
        middle_index = len(words) // 2
        first_line = " ".join(words[:middle_index])
        second_line = " ".join(words[middle_index:])

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
    
    print("Processing complete!")


if __name__ == "__main__":
    overlay_png_on_videos(INPUT_DIRECTORY, OUTPUT_DIRECTORY, OVERLAY_IMAGE_PATH)
