import streamlit as st

from texttospeech.tts_coqui import *
from translation.translate_huggingface import *
from integrations.youtube import *
from audiovideo.utilities import *
from playsound import playsound

LANGUAGES = {
    "English": {"model": "en", "youtube":"en"},
    "French": {"model": "fr-fr", "youtube":"fr"},
    "Portuguese": {"model": "pt-br", "youtube":"pt"}
}

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
def _download_video_and_extract_wav(url, _progress_hooks=[]):
    return download_video_and_extract_wav(url, _progress_hooks)

def _download_transcript(url, from_language='fr'):
    return download_transcript(url, from_language)

def _split_audio_on_timestamps(audio, data_holder):
    return split_audio_on_timestamps(audio, data_holder)

def _translate_timestamped(transcript, translation_model):
    return translate_timestamped(transcript, translation_model)

def _fetch_translated_transcript(url, to_language='en'):
    return fetch_translated_transcript(url, to_language)

def _tts_timestamped(data_holder: List, model_name: str, update_progress: Function, speaker_idx: str=None, language: str="en"):
    return tts_timestamped(data_holder, model_name, update_progress, speaker_idx, language)

def _merge_timestamped_wav(data_holder):
    return merge_timestamped_wav(data_holder)

def _merge_video_and_wav(video, merged_wav_file):
    return merge_video_and_wav(video, merged_wav_file)

def _create_data_holder_from_transcript(transcript):
    return create_data_holder_from_transcript(transcript)

def _create_data_holder_from_translated_transcript(transcript):
    return create_data_holder_from_translated_transcript(transcript)


def main_dev():
    st.title("Translate a YouTube video")
    url = st.text_input("YouTube URL", value="https://www.youtube.com/watch?v=LA8L3IvFBvQ")
    transcript_button = st.checkbox("Get transcript")
    if transcript_button:
        clean_transcript,transcript = _download_transcript(url)
        video, audio = _download_video_and_extract_wav(url)   #TODO: Just get the audio from the video file instead of downloading it seperately, the download size is the same
        audio_timestamped = _split_audio_on_timestamps(audio, transcript)
        st.header("Transcript")
        for snippet in zip(transcript, audio_timestamped):
            text_snippet = snippet[0]
            audio_snippet = snippet[1]
            st.text_input(str(text_snippet["start"]), value=text_snippet["text"], key=hash("transcript"+str(text_snippet["start"])))
            audio_file = open(audio_snippet["audio"], 'rb')
            st.audio(audio_file)

        translate_button = st.checkbox("Translate")
        if translate_button:
            translated_text = _translate_timestamped(transcript, "SEBIS/legal_t5_small_trans_en_sv_small_finetuned")
            for snippet in translated_text:
                st.text_input(str(snippet["start"]), value=str(snippet["text"]), key=hash("translation"+str(snippet["start"])))

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

def main():
    st.title("Translate a YouTube video")
    url = st.text_input("YouTube URL", value="https://www.youtube.com/watch?v=u_XIDO79zaQ")
    from_language_dropdown = st.selectbox("From language: ", list(LANGUAGES.keys()))
    to_language_dropdown = st.selectbox("To language: ", list(LANGUAGES.keys()))

    if st.button("Translate!"):
        # Get a translated transcript
        try:
            translated_transcript = _fetch_translated_transcript(url, to_language=LANGUAGES[to_language_dropdown]["youtube"])
            # Create a data holder to keep track of all data throughout the process
            data_holder = _create_data_holder_from_translated_transcript(translated_transcript)
        except:
            transcript = _download_transcript(url, from_language=LANGUAGES[from_language_dropdown]["youtube"])
            # Create a data holder to keep track of all data throughout the process
            data_holder = _create_data_holder_from_transcript(transcript)
            translated_transcript = _translate_timestamped(transcript, "SEBIS/legal_t5_small_trans_en_sv_small_finetuned")
            add_translated_transcript(data_holder, translated_transcript)

        # Download audio and video
        download_progress = st.progress(0)
        download_progress_message = st.empty()
        def update_download_progress(d):
            if d['status'] == 'downloading':
                p = d['_percent_str']
                p = p.replace('%','')
                download_progress.progress(float(p))
                download_progress_message.markdown(d['filename'], d['_percent_str'], d['_eta_str'])

        video, audio = _download_video_and_extract_wav(url, [update_download_progress])

        del download_progress
        del download_progress_message
        
        # Split audio into timestamps
        _split_audio_on_timestamps(audio, data_holder)

        # Run TTS to generate new audio
        tts_progress = st.progress(0)
        translation_progress_message = st.empty()
        def progressbar_update(progress, message):
            tts_progress.progress(progress)
            translation_progress_message.markdown(message)

        _tts_timestamped(data_holder, "de/thorsten/tacotron2-DCA", progressbar_update, language=LANGUAGES[to_language_dropdown]["model"])

        # Merge the new audio with the video
        merged_wav_file = _merge_timestamped_wav(data_holder)
        merged_video_file = _merge_video_and_wav(video, merged_wav_file)

        #Display the new video
        video_file = open(merged_video_file, 'rb')
        st.video(video_file)



if __name__ == "__main__":
    main()