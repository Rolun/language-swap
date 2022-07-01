from typing import List
from transformers import pipeline


def translate_timestamped(timestamped_text: List, model_name: str):
    translated_timestamped = []

    cleaned_text = [i['text'] for i in timestamped_text]
    translated_text = translate(cleaned_text, model_name)
    for snippet in zip(timestamped_text, translated_text):
        translated_timestamped.append({
            "text": snippet[1],
            "start": snippet[0]["start"],
            "duration": snippet[0]["duration"]
        })

    print(translated_timestamped)
    return translated_timestamped

def translate(text, model_name: str):
    translator = pipeline("translation", model=model_name)
    translated_text = translator(text)
    output = [i['translation_text'] for i in translated_text]
    return output


def main():
    TRANSLATION_MODEL_NAME = "Helsinki-NLP/opus-mt-zh-en"
    text = "我叫沃尔夫冈，我住在柏林。"
    new_text = translate(text, TRANSLATION_MODEL_NAME)
    print(new_text)

if __name__ == "__main__":
    main()