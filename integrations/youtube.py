import youtube_dl
from youtube_transcript_api import YouTubeTranscriptApi
from playsound import playsound


def get_transcript(url: str):
    video_id = url.split("=")[1]
    video_id = video_id.split("&")[0]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    FinalTranscript = ' '.join([i['text'] for i in transcript])
    return FinalTranscript,transcript

def get_wav_from_video(url: str):
    video_info = youtube_dl.YoutubeDL().extract_info(url=url, download=False)

    options = {
        'audio-format': 'wav',
        'keepvideo': False,
        'outtmpL': f"{video_info['title']}.wav",
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    return f"{video_info['title']}" + "-" + f"{video_info['webpage_url']}".split("=")[-1] + ".wav"

def main():
    url = "https://www.youtube.com/watch?v=LA8L3IvFBvQ" #Explaining the confusion matrix
    wav_file_name = get_wav_from_video(url)
    playsound(wav_file_name)

if __name__ == "__main__":
    main()
