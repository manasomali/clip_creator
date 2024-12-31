import auditok
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.resize import resize
import moviepy.video.fx.all as vfx
from moviepy.editor import VideoFileClip
import time
import os
from concurrent.futures import ProcessPoolExecutor as Executor

import uuid

INPUT_PATH: str = "G:/filmes_dub/A Nova Onda do Imperador/part3.mp4"
PREFIX: str = "A.Nova.Onda.do.Imperador_"
ZOOM: float = 1.0
CROP_TOP_BOTTOM: int = 0
VOLUME_BOOST: float = 2

def process_video(start_time: str) -> None:
    id = str(uuid.uuid1()).split("-")[0]
    output_path = f"{PREFIX}{id}.mp4"

    end_time = start_time+60
    
    video: VideoFileClip = VideoFileClip(INPUT_PATH).subclip(start_time, end_time)
    if ZOOM != 1.0:
        new_width: int = int(video.w * ZOOM)
        new_height: int = int(video.h * ZOOM)
        video = resize(video, width=new_width, height=new_height)
    if CROP_TOP_BOTTOM:
        video = video.crop(y1=CROP_TOP_BOTTOM, y2=video.h - CROP_TOP_BOTTOM)
    
    if VOLUME_BOOST != 1.0:
        video = video.volumex(VOLUME_BOOST)
    
    video = video.fx(vfx.colorx, 1.5) 

    output_width: int = 1080
    output_height: int = 1920

    background = resize(video, width=output_width, height=output_height)
    background = background.set_opacity(0.3)
    background = background.fx(vfx.colorx, 0.5) 
    video_position: tuple = ("center", "center")
    
    final_video: CompositeVideoClip = CompositeVideoClip([
        background.set_position(("center", "center")),
        video.set_position(video_position),
    ], size=(output_width, output_height))

    final_video.write_videofile(output_path, codec="libx264", fps=24, threads=4)


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
    POOL_SIZE = os.cpu_count()
    print(f"Getting start times...")
    start_times: list = get_start_times_with_auditok(INPUT_PATH)

    print(f"Processing videos...")
    print(time.time())
    with Executor(max_workers=POOL_SIZE) as executor:
        executor.map(process_video, start_times)
    print(time.time())
    
