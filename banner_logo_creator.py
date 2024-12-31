import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from moviepy.video.VideoClip import ImageClip
from concurrent.futures import ProcessPoolExecutor as Executor

change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

INPUT_DIRECTORY = "Round.6.S02E03"
OUTPUT_DIRECTORY = "Round.6.S02E03_out"
LOGO_PATH = "assets/logo.png"

def add_text_to_videos(txt_file):
    txt_path = os.path.join(INPUT_DIRECTORY, txt_file)
    video_path = os.path.join(INPUT_DIRECTORY, txt_file.replace(".txt",".mp4"))
    
    output_path = os.path.join(OUTPUT_DIRECTORY, txt_file.replace(".txt",".mp4"))
    if os.path.exists(output_path):
        print("Already done", output_path)
        return

    with open(txt_path, 'r', encoding='utf-8') as file:
        sentence = file.read().strip()
    
    video = VideoFileClip(video_path)
    font_path = "assets/BebasNeue-Regular.ttf"
    banner = TextClip(
        sentence,
        fontsize=100,
        color="black",
        font=font_path,
        bg_color="white",
        size=(1080, 275)
    )
    banner = banner.set_duration(video.duration).set_position(("center", 175))
    
    if LOGO_PATH:
        output_height = 1920
        logo = ImageClip(LOGO_PATH).set_duration(video.duration)
        logo_position = ("center", output_height - 400)
        final_video = CompositeVideoClip([video, banner, logo.set_position(logo_position)])
    else:
        final_video = CompositeVideoClip([video, banner])
        
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    print(f"Processed: {txt_file.replace(".txt",".mp4")}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    POOL_SIZE = os.cpu_count()
    txt_files = [f for f in os.listdir(INPUT_DIRECTORY) if f.endswith('.txt')]
    with Executor(max_workers=POOL_SIZE) as executor:
        executor.map(add_text_to_videos, txt_files)

