from texttospeech.transform_text import *
from Translation.translate import *
from integrations.youtube import *
from playsound import playsound


TRANSLATION_MODEL_NAME = "Helsinki-NLP/opus-mt-zh-en"
VOICE_MODEL_NAME = "en/ljspeech/tacotron2-DDC_ph"



text = "我叫沃尔夫冈，我住在柏林。"

def merge_video_and_timestamped_audio():
    merged_video_path = ""
    return merged_video_path

def stt_pipeline():
    pass

def transcript_pipeline(url: str, translation_model: str, voice_model:str):
    print("Fetching transcribe...")
    _,transcript = get_transcript(url)
    print("Translating text...")
    translated_text = translate_timestamped(transcript, translation_model)
    print("Generating voice...")
    wav_file_name = tts_timestamped(translated_text, voice_model)
    playsound(wav_file_name)

def main():
    transcript_pipeline("https://www.youtube.com/watch?v=LA8L3IvFBvQ", "Helsinki-NLP/opus-mt-zh-en", "en/ljspeech/tacotron2-DDC_ph")

if __name__ == "__main__":
    main()