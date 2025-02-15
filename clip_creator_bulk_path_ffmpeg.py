import auditok
import os
import subprocess
import random

from tqdm import tqdm

INPUT_PATH: str = "G:/anime_dub/Gobaku Moe Mama Tsurezure"
VOLUME_BOOST: str = "3.0"
SHUTDOWN: bool = True
CUDA: bool = True
# if film
# MIN_DURATION: int = 60
# MAX_START: int = 50
# MAX_END: int = 70
# VIDEO_WIDTH: int = 1890
# if anime
MIN_DURATION: int = 30
MAX_START: int = 20
MAX_END: int = 30
VIDEO_WIDTH = 1512

def process_video(start_time: float, media_file: str, max_start: int, max_end: int) -> None:
    print("Creating clip...")
    start_time = int(start_time)
    output_path = f"{start_time}_{os.path.basename(media_file)}"
    
    if os.path.exists(output_path):
        print(f"Output path already exists: {output_path}. Skipping...")
        return

    if CUDA:
        cmd = [
            "ffmpeg", "-hwaccel", "cuda",
            "-i", media_file,
            "-ss", str(start_time), "-t", str(random.randint(max_start, max_end)),
            "-filter_complex",
            f"[0:v]scale={VIDEO_WIDTH}:1920,setsar=1,gblur=sigma=4,eq=brightness=-0.2[bg];"
            f"[0:v]scale={VIDEO_WIDTH}:-1[ovrl];"
            "[bg][ovrl]overlay=(W-w)/2:(H-h)/2[tmp];"
            "[tmp]crop=1080:1920[v];"
            f"[0:a]volume={VOLUME_BOOST}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "h264_nvenc", "-cq", "20", "-preset", "fast",
            output_path
        ]
    else:
        cmd = [
            "ffmpeg",
            "-i", media_file,
            "-ss", str(start_time), "-t", str(random.randint(max_start, max_end)),
            "-filter_complex",
            f"[0:v]scale={VIDEO_WIDTH}:1920,setsar=1,gblur=sigma=4,eq=brightness=-0.2[bg];"
            f"[0:v]scale={VIDEO_WIDTH}:-1[ovrl];"
            "[bg][ovrl]overlay=(W-w)/2:(H-h)/2[tmp];"
            "[tmp]crop=1080:1920[v];"
            f"[0:a]volume={VOLUME_BOOST}[a]",
            "-map", "[v]", "-map", "[a]",
            output_path
        ]
    
    print(" ".join(cmd))
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

def get_start_times_with_auditok(file_path: str, min_duration: int = 60) -> list:
    print("Auditok splitting...")
    audio_regions = auditok.split(
        file_path,
        energy_threshold=40,
        max_dur=5,
        max_silence=0.05
    )
    subclip_start_times: list = []
    current_start: float = 0.0
    accumulated_duration: float = 0
    
    for region in audio_regions:
        duration: float = region.end - region.start

        if not current_start:
            current_start = region.start

        accumulated_duration += duration

        if accumulated_duration >= min_duration:
            subclip_start_times.append(current_start)
            current_start = None
            accumulated_duration = 0

    return subclip_start_times


if __name__ == "__main__":
    try:
        media_files = []
        for root, dirs, files in os.walk(INPUT_PATH):
            for file in files:
                if file.endswith(('.mp4', '.mkv')):
                    media_files.append(os.path.join(root, file))
        print(f"Found media files: {media_files}")
        
        for media_file in media_files:
            print("Getting start times...", media_file)
            start_times: list = get_start_times_with_auditok(media_file, min_duration=MIN_DURATION)
            print("Processing videos...", media_file)
            for start_time in tqdm(start_times, desc="Processing start times"):
                process_video(start_time, media_file, max_start=MAX_START, max_end=MAX_END)

        if SHUTDOWN:
            os.system("shutdown /s /t 1")
    except Exception as e:
        print(e)
        if SHUTDOWN:
            os.system("shutdown /s /t 1")
