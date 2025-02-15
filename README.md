# Scripts for Clip Creation

## Features

- Load and save configuration settings for easy access.
- Process videos by adding customizable text and logos.
- Configurable text, logo and font for flexibility.

## Requirements

To run this project, you need to install the following Python packages:

- auditok==0.3.0

You can install these packages using pip: `pip install -r requirements.txt`.

Also, ffmpeg:

1. Download the FFmpeg build from [FFmpeg's official website](https://ffmpeg.org/download.html).
2. Extract the downloaded zip file.
3. Add the `bin` folder (inside the extracted folder) to your system's PATH environment variable.

### For macOS:
You can install FFmpeg using Homebrew. Run the following command in your terminal:


# clip_creator_bulk_path_ffmpeg.py


# create_hook.py 
This script generates captivating hooks based on video transcriptions. It utilizes an LLM model to create engaging and concise hooks that intrigue viewers, encouraging them to watch the video. The hooks are generated in Brazilian Portuguese and are limited to a maximum of 10 words, ensuring they are impactful and to the point. The script processes all relevant video files in a specified directory, extracting audio, transcribing it, and then generating hooks for each video.

# choose_hook.py
This script allows users to select and keep specific sentences from text files. It processes all `.txt` files in a specified directory, extracting sentences that are numbered. Users can choose one of the extracted sentences, which will then replace the original content of the text file. This functionality is useful for refining text content, ensuring that only the most relevant information is retained for further use.


# banner_logo_creator_with_ffmpeg.py and banner_logo_creator_anime_with_ffmpeg.py
It creates videoS with this format:

```
┍━━━━━━━━━━━━━┑
┃             ┃
┃ text banner ┃
┃             ┃
┃    clip     ┃
┃             ┃
┃    logo     ┃
┃             ┃
┗━━━━━━━━━━━━━┛
```

# add_song_with_ffmpeg.py
This script adds a song to a video using FFmpeg. It takes an input video file and an audio file, then combines them into a new output video file with the audio track added. It is useful for enhancing videos with background music or soundtracks, making them more engaging for viewers. The output video retains the original video quality while incorporating the new audio seamlessly. It adds the a song randomly from the dir and the start time of the song is also random.
