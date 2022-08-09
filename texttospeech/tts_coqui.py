from bdb import set_trace
from pyclbr import Function
import tempfile
from typing import Dict, List, Optional
from TTS.config import load_config
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
import os


MAX_TXT_LEN = 100

manager = ModelManager()


def tts_timestamped(timestamped_text: List, model_name: str, update_progress: Function, speaker_timestamped: Dict=None, speaker_idx: str=None, language: str="en"):
    wav_files_timestamped = []
    loading_length = len(timestamped_text)
    current_iteration = 0

    for snippet in zip(timestamped_text,speaker_timestamped):
        text_snippet = snippet[0]
        speaker_snippet = snippet[1]
        
        print(text_snippet['text'])
        update_progress(current_iteration/loading_length, text_snippet['text'])

        wav_files_timestamped.append({
            "audio": tts(text_snippet['text'], model_name, speaker_snippet["audio"], speaker_idx, language),
            "start": text_snippet["start"],
            "duration": text_snippet["duration"]
        })

        current_iteration+=1
    return wav_files_timestamped

def fetch_models():
    MODEL_NAMES = manager.list_tts_models()

    # filter out multi-speaker models and slow wavegrad vocoders
    filters = ["vctk", "your_tts", "ek1"]
    MODEL_NAMES = [model_name for model_name in MODEL_NAMES if not any(f in model_name for f in filters)]

    # reorder models
    MODEL_NAMES[0], MODEL_NAMES[1], MODEL_NAMES[2]= MODEL_NAMES[1], MODEL_NAMES[2], MODEL_NAMES[0]
    print(MODEL_NAMES)
    return MODEL_NAMES


def tts(text: str, model_name: str, speaker_wav: str=None, speaker_idx: str=None, language="en"):
    if speaker_wav:
        return tts_cloning(text, model_name, speaker_wav, language)
    else:
        return tts_static(text, model_name, speaker_idx)

def tts_cloning(text: str, model_name: str, speaker_wav: str, language="en"):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
        os.system('tts --text "'+text+'" --model_name tts_models/multilingual/multi-dataset/your_tts --speaker_wav '+speaker_wav+' --language_idx "'+language+'" --out_path '+fp.name)
        return fp.name

def tts_static(text: str, model_name: str, speaker_idx: str=None):
    if len(text) > MAX_TXT_LEN:
        text = text[:MAX_TXT_LEN]
        print(f"Input text was cutoff since it went over the {MAX_TXT_LEN} character limit.")
    print(text, model_name)
    # download model
    model_path, config_path, model_item = manager.download_model(f"tts_models/{model_name}")
    vocoder_name: Optional[str] = model_item["default_vocoder"]
    # download vocoder
    vocoder_path = None
    vocoder_config_path = None
    if vocoder_name is not None:
        vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)
    # init synthesizer
    synthesizer = Synthesizer(
        model_path, config_path, None, None, vocoder_path, vocoder_config_path,
    )
    # synthesize
    if synthesizer is None:
        raise NameError("model not found")
    if text[-1]!=".":
        text+="."
    wavs = synthesizer.tts(text, speaker_idx)
    # return output
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
        synthesizer.save_wav(wavs, fp)
        return fp.name

def main():
    from playsound import playsound
    fetch_models()
    MODEL_NAME = "de/thorsten/tacotron2-DCA"
    TEXT = "das ist ein test"

    wav_file_name = tts(TEXT, MODEL_NAME)
    playsound(wav_file_name)

if __name__ == "__main__":
    main()

