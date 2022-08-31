from typing import List
from pydub import AudioSegment
from moviepy.editor import *
import os
import tempfile
from dataclasses import dataclass

@dataclass
class Snippet:
    origional_text: str = ""
    translated_text: str = ""
    origional_audio_path: str = ""
    translated_audion_path: str = ""
    start_time: float = 0
    stop_time: float = 0


def create_data_holder_from_transcript(transcript):
    data_holder = []
    for snippet in transcript:
        data_holder.append(Snippet(
            origional_text = snippet["text"],
            start_time = snippet["start"],
            stop_time= snippet["start"] + snippet["duration"]
        ))
    return data_holder

def create_data_holder_from_translated_transcript(transcript):
    data_holder = []
    for snippet in transcript:
        data_holder.append(Snippet(
            translated_text = snippet["text"],
            start_time = snippet["start"],
            stop_time= snippet["start"] + snippet["duration"]
        ))
    return data_holder

def merge_timestamped_wav(data_holder: List):
    merged_audio = AudioSegment.empty()

    for snippet in data_holder:
        start_diff = snippet.start_time*1000 - len(merged_audio)
        if start_diff>0:
            merged_audio += AudioSegment.silent(duration=start_diff)
        try:
            merged_audio += AudioSegment.from_wav(snippet.translated_audion_path)
        except:
            import pdb; pdb.set_trace()


    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
        merged_audio.export(fp, format="wav")
        return fp.name


def add_translated_transcript(data_holder, translated_transcript):
    for snippet in zip(data_holder, translated_transcript):
        snippet[0].translated_text=snippet[1]["text"]


def split_audio_on_timestamps(audio_file, data_holder):
    AudioSegment.converter = "/absolute/path/to/ffmpeg"
    audio = AudioSegment.from_wav(audio_file)

    for snippet in data_holder:
        snippet.origional_audio_path = _split_and_save_audio(audio, snippet.start_time, snippet.stop_time)

def _split_and_save_audio(audio, start_time, stop_time):
    split_sound = audio[int(start_time*1000) : int(stop_time*1000)]
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
        split_sound.export(fp, format='wav')
        return fp.name


def merge_video_and_wav(video_file: str, audio_file: str):
    videoclip = VideoFileClip(video_file)
    audioclip = AudioFileClip(audio_file)

    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip

    filename, file_extension = os.path.splitext(video_file)
    file_path = filename + "_dubbed" + file_extension
    videoclip.write_videofile(file_path)

    return file_path




def main():
    from playsound import playsound

    test_audio_folder = "test_audio"
    merged_audio = merge_timestamped_wav
    playsound(merged_audio)

if __name__ == "__main__":
    main()
