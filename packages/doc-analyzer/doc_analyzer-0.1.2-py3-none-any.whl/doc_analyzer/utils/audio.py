import io
import requests
import os
from moviepy.editor import *
from pydub import AudioSegment
import shutil
from urllib.parse import urlparse


def copy_audio(uri, destination_path):
    parsed_uri = urlparse(uri)

    if os.path.exists(destination_path):
        print("File already exists, skipping")
        return

    # Check if it's an HTTP or HTTPS link
    if parsed_uri.scheme in ["http", "https"]:
        download_audio(uri, destination_path) 
    # Check if it's a local path
    elif os.path.exists(uri):
        print("Found local file, copying")
        shutil.copy(uri, destination_path)
    else:
        return print("Not sure how to access file") 
        raise


def download_audio(url, output_file):
    response = requests.get(url)
    
    if response.status_code == 200:
        audio_data = response.content
        if 'mp4' in url:
            print("Found video, extracting audio")
            extract_audio_from_video(audio_data, output_file)
        elif 'mp3' in url:
            print("Found audio, saving")
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            #with open(output_file, "wb") as f:
            #    f.write(audio_data)
            audio.export(output_file, format="mp3")  # Export the audio directly to the desired format
        
        print(f"Audio downloaded and saved as {output_file}")
    else:
        print("Failed to download audio")


def extract_audio_from_video(video_data, output_file):
    video = VideoFileClip(video_data)
    print("Got video clip")

    # Extract the audio
    audio = video.audio

    # Save the audio as an MP3 to a BytesIO object
    audio_data = io.BytesIO()
    audio.write_audiofile(audio_data, format="mp3")    
    # Write the file
    with open(output_file, "wb") as f:
        f.write(audio_data.getvalue())

    # Close the clips
    audio.close()
    video.close()





