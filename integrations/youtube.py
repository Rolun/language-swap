from typing import List
import youtube_dl #TODO: Change to yt-dlp 
from youtube_transcript_api import YouTubeTranscriptApi
from playsound import playsound


def download_audio_video(url: str):
    audio_path = download_wav_from_video(url=url)
    video_path = download_video(url=url)

    return audio_path, video_path

def download_transcript(url: str, from_language: str='fr'):
    video_id = url.split("=")[1]
    video_id = video_id.split("&")[0]

    transcript = YouTubeTranscriptApi.get_transcript(video_id, [from_language])
    FinalTranscript = ' '.join([i['text'] for i in transcript])
    return transcript


def fetch_translated_transcript(url: str, to_language: str = 'en'):
    video_id = url.split("=")[1]
    video_id = video_id.split("&")[0]

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, [to_language])
        FinalTranscript = ' '.join([i['text'] for i in transcript])
    except:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(["en"])
        translated_transcript = transcript.translate(to_language)
        transcript = translated_transcript.fetch()
        FinalTranscript = ' '.join([i['text'] for i in transcript])

    return transcript


def download_video(url: str, progress_hooks: List=[]):
    video_info = youtube_dl.YoutubeDL().extract_info(url=url, download=False)

    video_path = f"{video_info['title']}.mp4"

    options = {
        'noplaylist' : True, 
        'outtmpl': video_path,
        'progress_hooks': progress_hooks,
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    return video_path

def download_video_and_extract_wav(url: str, progress_hooks: List=[]):
    video_info = youtube_dl.YoutubeDL().extract_info(url=url, download=False)

    options = {
        'noplaylist' : True, 
        'format': 'mp4',
        'progress_hooks': progress_hooks,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': f"{video_info['title']}.mp4",
        'keepvideo': True,
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    return f"{video_info['title']}.mp4", f"{video_info['title']}.wav"

def download_wav_from_video(url: str):
    video_info = youtube_dl.YoutubeDL().extract_info(url=url, download=False)

    options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        # 'audio-format': 'wav',
        # 'keepvideo': False,
        'outtmpl': f"{video_info['title']}.wav",
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    return f"{video_info['title']}.wav"

def main():
    url = "https://www.youtube.com/watch?v=LA8L3IvFBvQ" #Explaining the confusion matrix
    file_name = download_video_and_extract_wav(url)
    print(file_name)

if __name__ == "__main__":
    main()
