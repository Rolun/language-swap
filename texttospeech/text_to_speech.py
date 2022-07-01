from bdb import set_trace
import tempfile
from typing import List, Optional
from TTS.config import load_config
import gradio as gr
import numpy as np
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer


MAX_TXT_LEN = 100

manager = ModelManager()


def tts_timestamped(timestamped_text: List, model_name: str, speaker_idx: str=None):
    wav_files_timestamped = []
    for snippet in timestamped_text:
        print(snippet['text'])
        wav_files_timestamped.append({
            "audio": tts(snippet['text'], model_name, speaker_idx),
            "start": snippet["start"],
            "duration": snippet["duration"]
        })
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

def tts(text: str, model_name: str, speaker_idx: str=None):
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

