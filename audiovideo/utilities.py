from pydub import AudioSegment
import tempfile


def merge_timestamped_wav(audio_files_timestamped: dict):
    merged_audio = AudioSegment.empty()

    for sample in audio_files_timestamped:
        start_diff = sample['start']*1000 - len(merged_audio)
        if start_diff>0:
            merged_audio += AudioSegment.silent(duration=start_diff)
        merged_audio += AudioSegment.from_wav(sample['audio'])

    import pdb; pdb.set_trace()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
        merged_audio.export(fp, format="wav")
        return fp.name




def merge_video_and_wav(video_file: str, audio_file: str):
    merged_video_path = ""
    return merged_video_path




def main():
    from playsound import playsound

    test_audio_folder = "test_audio"
    merged_audio = merge_timestamped_wav
    playsound(merged_audio)

if __name__ == "__main__":
    main()
