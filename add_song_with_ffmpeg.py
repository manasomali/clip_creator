import subprocess
import os
import random
import math

from tqdm import tqdm

TARGET_DIR = "Maso Mesu Soap De Aimashou/02"
OUTPUT_DIR = "Maso Mesu Soap De Aimashou_02_music"
MUSIC_DIR = "G:/tiktok_dark/triploedits/edits/assets/songs/funk"
SHUTDOWN: bool = False
CUDA: bool = True



def get_duration(file_path):
    print("Getting duration", file_path)
    result = subprocess.run(
        ['ffmpeg', '-i', file_path],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    output = result.stderr
    for line in output.splitlines():
        if "Duration" in line:
            duration_str = line.split("Duration: ")[1].split(",")[0]
            h, m, s = map(float, duration_str.split(":"))
            total_seconds = h * 3600 + m * 60 + s
            return total_seconds
    return None


def add_song_to_videos(input_dir, output_dir, music_files):
    os.makedirs(output_dir, exist_ok=True)

    mp4_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.mkv'))]
    
    if not mp4_files or not music_files:
        print("No MP4 or MP3 files found in the input directory.")
        return
    for file in tqdm(mp4_files, desc="Processing videos", unit="file"):
        random_music = random.choice(music_files)
        
        input_path = f"{input_dir}/{file}"
        output_path = f"{output_dir}/{file}"


        video_duration = get_duration(input_path)
        music_duration = get_duration(random_music)
        
        random_start = random.randint(0, int(music_duration))
        if random_start+video_duration>music_duration:
            random_start = math.floor(music_duration-video_duration)

        if CUDA:
            cmd = [
                "ffmpeg", "-i", input_path, "-i", random_music, 
                "-filter_complex", f"[1:a]atrim=start={random_start},volume=2[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2[a]", 
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", output_path
            ]
        else:
            cmd = [
                "ffmpeg", "-i", input_path, "-i", random_music, 
                "-filter_complex", f"[1:a]atrim=start={random_start},volume=2[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2[a]", 
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", output_path
            ]
        
        print(cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    
    print("Processing complete!")

if __name__ == "__main__":

    mp3_files = [os.path.join(MUSIC_DIR, f) for f in os.listdir(MUSIC_DIR) if f.endswith(".mp3")]
    add_song_to_videos(TARGET_DIR, OUTPUT_DIR, mp3_files)

    if SHUTDOWN:
        os.system("shutdown /s /t 1")
    