from texttospeech.text_to_speech import *
from translation.translate import *
from integrations.youtube import *
from audiovideo.utilities import *
from playsound import playsound



def stt_pipeline():
    pass

def transcript_pipeline(url: str, translation_model: str, voice_model:str):
    print("Fetching transcribe...")
    _,transcript = get_transcript(url)
    print("Translating text...")
    translated_text = translate_timestamped(transcript, translation_model)
    print("Generating voice...")
    wav_files_timestamped = tts_timestamped(translated_text, voice_model)
    print("Merging audio...")
    merged_wav_file = merge_timestamped_wav(wav_files_timestamped)
    
    playsound(merged_wav_file)

def main():
    transcript_pipeline("https://www.youtube.com/watch?v=LA8L3IvFBvQ", "Helsinki-NLP/opus-mt-en-de", "de/thorsten/tacotron2-DCA")

if __name__ == "__main__":
    main()