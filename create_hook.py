import os
from moviepy.editor import VideoFileClip
from gpt4all import GPT4All
import whisperx
from typing import List

TARGET_DIR: str = "Acampamento.do.Pecado"
NAME: str = "Yes, God, Yes"
TYPE: str = "coming-of-age comedy-drama"
OPTIONS: str = "three"
SHUTDOWN: bool = False
MODEL_PATH: str = "G:/models/gpt4all"

device: str = "cuda" 
audio_file: str = "audio.mp3"
batch_size: int = 16
compute_type: str = "int8"

model = whisperx.load_model("large-v2", device, compute_type=compute_type, download_root="G:/models/")

def create_txt_files_for_mp4s(target_dir: str) -> None:
    if not os.path.isdir(target_dir):
        print(f"Error: The directory '{target_dir}' does not exist.")
        return
    
    mp4_files = [f for f in os.listdir(target_dir) if f.endswith('.mp4') or f.endswith('.mkv')]
    
    if not mp4_files:
        print("No .mp4 files found in the directory.")
        return
    
    for mp4_file in mp4_files:
        txt_file = os.path.splitext(mp4_file)[0] + '.txt'
        txt_path = os.path.join(target_dir, txt_file)
        
        if not os.path.exists(txt_path):
            with open(txt_path, 'w') as f:
                pass
            print(f"Created: {txt_path}")
        else:
            print(f"Already exists: {txt_path}")

def extract_audio(video_path: str, audio_path: str) -> None:
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    clip.close()

def transcribe_audio(audio_path: str) -> str:
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=batch_size)
    print(result["segments"])
    texts: List[str] = []
    for segment in result.get("segments", []):
        texts.append(segment.get("text", ""))
    return " ".join(texts)

def generate_hook(transcription: str) -> str:
    gpt = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", model_path=MODEL_PATH)
    prompt = (
        f"The following is a transcription of a video: \n{transcription}\n. It is a short transcription from {NAME}, {TYPE}."
        f"Based on this transcription, write {OPTIONS} captivating hooks."
        "The hook should intrigue viewers and encourage them to keep watching. Output only the hook and make it 10 words max and brazilian portugues."
    )
    response = gpt.generate(prompt)
    return response.strip()

def process_video_files(target_dir: str) -> None:
    for filename in os.listdir(target_dir):
        if filename.endswith(".mp4") or filename.endswith(".mkv"):
            print(f"Processing {filename}...")
            video_path = os.path.join(target_dir, filename)
            audio_path = os.path.join(target_dir, "temp.wav")
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(target_dir, txt_filename)
            if os.path.getsize(txt_path) > 0:
                print(f"{txt_filename} already has content. Skipping...")
                continue

            extract_audio(video_path, audio_path)

            transcription = transcribe_audio(audio_path)
            print(f"Transcription for {filename}:\n", transcription)

            transcription_txt_path = os.path.join(target_dir, os.path.splitext(filename)[0] + "_transcription.txt")
            with open(transcription_txt_path, "w", encoding="utf-8") as f:
                f.write(transcription)

            hook = generate_hook(transcription)
            print(f"\nGenerated Hook for {filename}:\n", hook)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(hook)

if __name__ == "__main__":
    create_txt_files_for_mp4s(TARGET_DIR)
    process_video_files(TARGET_DIR)

    if SHUTDOWN:
        os.system("shutdown /s /t 1")