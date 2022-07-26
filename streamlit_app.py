import streamlit as st

from texttospeech.tts_coqui import *
from translation.translate_huggingface import *
from integrations.youtube import *
from audiovideo.utilities import *
from playsound import playsound



def stt_pipeline():
    pass

def transcript_pipeline(url: str, translation_model: str, voice_model:str):
    print("Downloading video...")
    video = download_video(url)
    print("Downloading audio...")
    audio = download_wav_from_video(url)
    print("Fetching transcribe...")
    _,transcript = download_transcript(url)
    print("Splitting audio based on timestamps...")
    audio_timestamped = split_audio_on_transcript_timestamps(audio, transcript)
    print("Translating text...")
    translated_text = translate_timestamped(transcript, translation_model)
    print("Generating voice...")
    wav_files_timestamped = tts_timestamped(translated_text, voice_model, audio_timestamped)
    print("Merging audio...")
    merged_wav_file = merge_timestamped_wav(wav_files_timestamped)
    print("Merging video with audio...")
    merged_video_file = merge_video_and_wav(video, merged_wav_file)

@st.experimental_singleton
def _download_video(url):
    return download_video(url)

@st.experimental_singleton
def _download_video_and_extract_wav(url):
    return download_video_and_extract_wav(url)

@st.experimental_singleton
def _download_transcript(url):
    return download_transcript(url)

@st.experimental_singleton
def _split_audio_on_transcript_timestamps(audio, transcript):
    return split_audio_on_transcript_timestamps(audio, transcript)

@st.experimental_singleton
def _translate_timestamped(transcript, translation_model):
    return translate_timestamped(transcript, translation_model)

@st.experimental_singleton
def _tts_timestamped(timestamped_text: List, model_name: str, speaker_timestamped: Dict=None, speaker_idx: str=None):
    return tts_timestamped(timestamped_text, model_name, speaker_timestamped, speaker_idx)

@st.experimental_singleton
def _merge_timestamped_wav(wav_files_timestamped):
    return merge_timestamped_wav(wav_files_timestamped)

@st.experimental_singleton
def _merge_video_and_wav(video, merged_wav_file):
    return merge_video_and_wav(video, merged_wav_file)


def main():
    st.title("Translate a YouTube video")
    url = st.text_input("YouTube URL", value="https://www.youtube.com/watch?v=LA8L3IvFBvQ")
    transcript_button = st.checkbox("Get transcript")
    if transcript_button:
        clean_transcript,transcript = _download_transcript(url)
        video, audio = _download_video_and_extract_wav(url)   #TODO: Just get the audio from the video file instead of downloading it seperately, the download size is the same
        audio_timestamped = _split_audio_on_transcript_timestamps(audio, transcript)
        st.header("Transcript")
        for snippet in zip(transcript, audio_timestamped):
            text_snippet = snippet[0]
            audio_snippet = snippet[1]
            st.text_input(str(text_snippet["start"]), value=text_snippet["text"])
            audio_file = open(audio_snippet["audio"], 'rb')
            st.audio(audio_file)

        translate_button = st.checkbox("Translate")
        if translate_button:
            translated_text = _translate_timestamped(transcript, "Helsinki-NLP/opus-mt-en-de")
            for snippet in translated_text:
                st.text_input(str(snippet["start"]), value=str(snippet["text"]))

            voice_button = st.checkbox("Convert to speech")
            if voice_button:
                wav_files_timestamped = _tts_timestamped(translated_text, "de/thorsten/tacotron2-DCA", speaker_timestamped=audio_timestamped)
                for snippet in wav_files_timestamped:
                    st.text(str(snippet["start"]))
                    audio_file = open(snippet["audio"], 'rb')
                    st.audio(audio_file)

                create_video_button = st.checkbox("Create video")
                if create_video_button:
                    merged_wav_file = _merge_timestamped_wav(wav_files_timestamped)
                    merged_video_file = _merge_video_and_wav(video, merged_wav_file)
                    video_file = open(merged_video_file, 'rb')
                    st.video(video_file)
            


    # transcript_pipeline("https://www.youtube.com/watch?v=LA8L3IvFBvQ", "Helsinki-NLP/opus-mt-en-de", "de/thorsten/tacotron2-DCA")

if __name__ == "__main__":
    main()