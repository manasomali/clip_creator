import PySimpleGUI as sg
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.resize import resize
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.config import change_settings
from moviepy.video.VideoClip import ImageClip
from proglog import ProgressBarLogger
import json
from PIL import Image
import io
import base64

CONFIG_FILE = "clip_creator_config.json"

def load_config():
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {"history": []}

def save_config(config):
    existing_config = load_config()
    history = existing_config.get("history", [])
    history_entry = {
        "input_path": config["-INPUT_PATH-"],
        "output_path": config["-OUTPUT_PATH-"],
        "start_time": config["-START_TIME-"],
        "end_time": config["-END_TIME-"],
        "banner_text": config["-BANNER_TEXT-"].strip(),
        "logo_path": config["-LOGO_PATH-"],
        "zoom": config["-ZOOM-"],
        "font_path": config["-FONT_PATH-"],
        "crop_top_bottom": config["-CROP_TOP_BOTTOM-"],
    }
    history.append(history_entry)
    existing_config["history"] = history
    with open(CONFIG_FILE, "w") as file:
        json.dump(existing_config, file, indent=4)

change_settings({"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe"})

class MyBarLogger(ProgressBarLogger):
    def __init__(self, progress_bar, init_state=None, bars=None, ignored_bars=None, logged_bars='all', min_time_interval=0, ignore_bars_under=0):
        super().__init__(init_state, bars, ignored_bars, logged_bars, min_time_interval, ignore_bars_under)
        self.progress_bar = progress_bar
        
    def callback(self, **changes):
        pass
    
    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        self.progress_bar(current_count=percentage)

def process_video(logger, input_path: str, output_path: str, start_time: str, end_time: str, banner_text: str, logo_path: str, zoom: float = 1.0, font_path: str = "assets/BebasNeue-Regular.ttf", crop_top_bottom=0) -> None:
    video = VideoFileClip(input_path).subclip(start_time, end_time)
    if zoom != 1.0:
        new_width = int(video.w * zoom)
        new_height = int(video.h * zoom)
        video = resize(video, width=new_width, height=new_height)
   
    if crop_top_bottom:
        video = video.crop(y1=crop_top_bottom, y2=video.h - crop_top_bottom)

    output_width = 1080
    output_height = 1920
    
    background = ColorClip(size=(output_width, output_height), color=(0, 0, 0), duration=video.duration)
    
    video_position = ("center", "center")

    banner = TextClip(
        banner_text,
        fontsize=100,
        color='black',
        font=font_path,
        bg_color='white',
        size=(output_width, 275)
    )
    banner = banner.set_duration(video.duration).set_position(("center", 175))

    logo = ImageClip(logo_path).set_duration(video.duration)
    logo_position = ("center", output_height - 400)

    final_video = CompositeVideoClip([
        background,
        video.set_position(video_position),
        banner,
        logo.set_position(logo_position)
    ])

    final_video.write_videofile(output_path, codec="libx264", fps=24, logger=logger)


def generate_preview_frame(input_path: str, start_time: str, banner_text: str, logo_path: str, zoom: float = 1.0, font_path: str = "assets/BebasNeue-Regular.ttf", crop_top_bottom=0):
    hours, minutes, seconds = map(int, start_time.split(":"))
    seconds += 1
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        hours += 1

    end_time = f"{hours:02}:{minutes:02}:{seconds:02}"

    video = VideoFileClip(input_path).subclip(start_time, end_time)
    if zoom != 1.0:
        new_width = int(video.w * zoom)
        new_height = int(video.h * zoom)
        video = resize(video, width=new_width, height=new_height)
    if crop_top_bottom:
        video = video.crop(y1=crop_top_bottom, y2=video.h - crop_top_bottom)

    output_width = 1080
    output_height = 1920
    
    background = ColorClip(size=(output_width, output_height), color=(0, 0, 0), duration=video.duration)
    
    video_position = ("center", "center")

    banner = TextClip(
        banner_text,
        fontsize=100,
        color="black",
        font=font_path,
        bg_color='white',
        size=(1080, 275)
    )
    banner = banner.set_duration(video.duration).set_position(("center", 175))

    logo = ImageClip(logo_path).set_duration(video.duration)
    logo_position = ("center", output_height - 400)

    final_video = CompositeVideoClip([
        background,
        video.set_position(video_position),
        banner,
        logo.set_position(logo_position)
    ])

    midpoint_time = (video.duration / 2)
    frame = final_video.get_frame(midpoint_time)
    
    image = Image.fromarray(frame)
    image=image.resize(size=(int(output_width/5), int(output_height/5)))

    with io.BytesIO() as buffer:
        image.save(buffer, format="PNG")
        img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return img_data

def main():
    sg.theme("DarkBlue")
    config_data = load_config()
    history = config_data.get("history", [])
    history_index = len(history) - 1

    def load_history_entry(index, window):
        if 0 <= index < len(history):
            entry = history[index]
            window["-INPUT_PATH-"].update(entry.get("input_path", ""))
            window["-OUTPUT_PATH-"].update(entry.get("output_path", ""))
            window["-START_TIME-"].update(entry.get("start_time", ""))
            window["-END_TIME-"].update(entry.get("end_time", ""))
            window["-BANNER_TEXT-"].update(entry.get("banner_text", ""))
            window["-LOGO_PATH-"].update(entry.get("logo_path", ""))
            window["-ZOOM-"].update(entry.get("zoom", ""))
            window["-FONT_PATH-"].update(entry.get("font_path", ""))
            window["-CROP_TOP_BOTTOM-"].update(entry.get("crop_top_bottom", ""))

    layout = [
        [sg.Text("Input Video Path:"), sg.InputText(key="-INPUT_PATH-"), sg.FileBrowse(file_types=(("Video Files", "*.mp4;*.mkv;*.webm"),))],
        [sg.Text("Output Video Path:"), sg.InputText(key="-OUTPUT_PATH-")],
        [sg.Text("Start Time (HH:MM:SS):"), sg.InputText(key="-START_TIME-")],
        [sg.Text("End Time (HH:MM:SS):"), sg.InputText(key="-END_TIME-")],
        [sg.Text("Banner Text:"), sg.Multiline(key="-BANNER_TEXT-", size=(40, 3))],
        [sg.Text("Logo Path:"), sg.InputText(key="-LOGO_PATH-"), sg.FileBrowse(file_types=(("Image Files", "*.png;*.jpg;*.jpeg"),))],
        [sg.Text("Font Path:"), sg.InputText(key="-FONT_PATH-"), sg.FileBrowse(file_types=(("Font Files", "*.ttf"),))],
        [sg.Text("Crop top and bottom:"), sg.InputText(key="-CROP_TOP_BOTTOM-")],
        [sg.Text("Zoom Level (1.0 = No Zoom):"), sg.InputText(key="-ZOOM-", default_text="1.0")],
        [sg.ProgressBar(max_value=100, orientation='h', size=(40, 20), key="-PROGRESS-")],
        [sg.Button("<"), sg.Button(">")],
        [sg.Button("Preview")],
        [sg.Button("Process Video"), sg.Button("Exit")],
        [sg.Image(key="-PREVIEW-", expand_x=True)]
    ]


    window = sg.Window("Video Processing Tool", layout, element_justification='c', finalize=True)
    if history:
        load_history_entry(history_index, window)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break

        if event == "<":
            if history_index > 0:
                history_index -= 1
                load_history_entry(history_index, window)
            else:
                sg.popup("No previous entries.")

        if event == ">":
            if history_index < len(history) - 1:
                history_index += 1
                load_history_entry(history_index, window)
            else:
                sg.popup("No next entries.")
        if event == "Preview":
            input_path = values["-INPUT_PATH-"]
            start_time = values["-START_TIME-"]
            banner_text = values["-BANNER_TEXT-"].strip()
            logo_path = values["-LOGO_PATH-"]
            zoom = float(values["-ZOOM-"])
            font_path = values["-FONT_PATH-"]
            crop_top_bottom = int(values["-CROP_TOP_BOTTOM-"])

            if not Path(input_path).is_file():
                sg.popup_error("Invalid input video path.")
                continue
            if not start_time:
                sg.popup_error("Start time is required.")
                continue
            if not banner_text:
                sg.popup_error("Banner text is required.")
                continue
            if not Path(logo_path).is_file():
                sg.popup_error("Invalid logo path.")
                continue
            if not Path(font_path).is_file():
                sg.popup_error("Invalid font path.")
                continue
            if not crop_top_bottom:
                sg.popup_error("Invalid crop top bottom.")
                continue

            preview_data = generate_preview_frame(input_path, start_time, banner_text, logo_path, zoom, font_path, crop_top_bottom)
            window["-PREVIEW-"].update(data=preview_data)
                    
        if event == "Process Video":
            input_path = values["-INPUT_PATH-"]
            output_path = values["-OUTPUT_PATH-"]
            start_time = values["-START_TIME-"]
            end_time = values["-END_TIME-"]
            banner_text = values["-BANNER_TEXT-"].strip()
            logo_path = values["-LOGO_PATH-"]
            zoom = float(values["-ZOOM-"])
            font_path = values["-FONT_PATH-"]
            crop_top_bottom = values["-CROP_TOP_BOTTOM-"]

            save_config(values)

            if not Path(input_path).is_file():
                sg.popup_error("Invalid input video path.")
                continue
            if not output_path:
                sg.popup_error("Output path is required.")
                continue
            if not start_time or not end_time:
                sg.popup_error("Start and end times are required.")
                continue
            if not banner_text:
                sg.popup_error("Banner text is required.")
                continue
            if not Path(logo_path).is_file():
                sg.popup_error("Invalid logo path.")
                continue
            if not Path(font_path).is_file():
                sg.popup_error("Invalid font path.")
                continue
            if not crop_top_bottom:
                sg.popup_error("Invalid crop top bottom.")
                continue

            try:
                progress_bar = window["-PROGRESS-"]
                progress_bar.update(current_count=0)
                logger = MyBarLogger(progress_bar)
                process_video(logger, input_path, output_path, start_time, end_time, banner_text, logo_path, zoom, font_path, crop_top_bottom)
                sg.popup("Video processed successfully!")
            except Exception as e:
                sg.popup_error(f"An error occurred: {e}")

    window.close()

if __name__ == "__main__":
    main()
