from typing import List
from pydub import AudioSegment
from moviepy.editor import *
import os
import tempfile


def merge_timestamped_wav(audio_files_timestamped: List):
    merged_audio = AudioSegment.empty()

    for sample in audio_files_timestamped:
        start_diff = sample['start']*1000 - len(merged_audio)
        if start_diff>0:
            merged_audio += AudioSegment.silent(duration=start_diff)
        merged_audio += AudioSegment.from_wav(sample['audio'])


    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
        merged_audio.export(fp, format="wav")
        return fp.name


def split_audio_on_transcript_timestamps(audio_file, transcript):
    wav_files_timestamped = []
    AudioSegment.converter = "/absolute/path/to/ffmpeg"
    audio = AudioSegment.from_wav(audio_file)

    for snippet in transcript:
        wav_files_timestamped.append({
            "audio": split_audio(audio, snippet["start"], snippet["duration"]),
            "start": snippet["start"],
            "duration": snippet["duration"]
        })
    return wav_files_timestamped


def split_audio(audio, start, duration):
    split_sound = audio[int(start*1000) : int((start+duration)*1000)]
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
