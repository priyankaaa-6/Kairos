# main file
from pprint import pprint
import requests
from pytube import YouTube
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
import streamlit as st
import json

from dotenv import load_dotenv
import os
load_dotenv()
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# creating Cache folder to store files
path = 'D:\\Github\\Edu-AiX'
cache_folder = os.path.join(path, 'Cache')
os.makedirs(cache_folder, exist_ok=True)
output_path = os.path.abspath(cache_folder)

# func which downloads yt video
def download_youtube_video(youtube_url, output_path='.', resolution='360p'):
    if os.path.exists(r'Cache/video01.mp4'):
        return 
    else:
        try:
            # Create a YouTube object
            youtube = YouTube(youtube_url)

            # Get the stream with the specified resolution
            video_stream = youtube.streams.get_by_resolution(resolution)

            if video_stream:
                # Download the video with the specified file name
                video_stream.download(output_path, filename='video01.mp4')
                print(f"Video download successful in {resolution} resolution! Saved as video01.mp4")
            else:
                print(f"Error: Video stream with {resolution} resolution not available.")
        except Exception as e:
            print(f"Error: {e}")

# func which extracts audio from the downloaded video
def extract_audio(video_path, output_audio_path):
    if os.path.exists(r'Cache\\extracted-audio.mp3'):
        return
    else:    
        try:
            # Load the video clip
            video_clip = VideoFileClip(video_path)

            # Extract audio
            audio_clip = video_clip.audio

            # Save the audio to the specified output path
            output_audio_path = os.path.join(output_audio_path, 'extracted-audio.mp3')
            audio_clip.write_audiofile(output_audio_path)

            print("Audio extraction successful!")
        except Exception as e:
            print(f"Error: {e}")

# func which calls all the api and returns the story and summary
def API():
    res = {}

    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-medium.en"
    headers = {"Authorization": "Bearer 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"}

    def query(filename):
        with open(filename, "rb") as f:
            data = f.read()
        # Add return_timestamps=True to the API request to handle long-form audio
        response = requests.post(API_URL, headers=headers, data=data, params={"return_timestamps": "true"})
        return response.json()
    
    print('done till here')
    if not os.path.exists(r'Cache\\trpt.json'):
        output = query(r"D:\\Github\\Edu-AiX\\Cache\\extracted-audio.mp3")
        
        # Print the response structure for debugging
        print("API Response:", output)
        
        # Ensure the key 'text' exists in the response
        if 'text' in output:
            story = output['text']
        else:
            print("Error: 'text' key not found in the response.")
            story = "No transcription available."

        # Ensure Cache directory exists before writing the file
        cache_dir = r"Cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)  # Create Cache directory if it doesn't exist
        
        # Save the story as a JSON file
        file_path = os.path.join(cache_dir, "trpt.json")
        with open(file_path, "w") as json_file:
            json.dump(story, json_file)
    else:
        print('By-passing due to API issue')
        with open(r'D:\\Github\\Edu-AiX\\Cache\\trpt.json', 'r') as file:
            quiz_data = json.load(file)
        story = quiz_data
    
    return story



# Prompt generation
def poopmt(que, trpt):
    poompt = '''
    I was studying from a youtube video, and I have a question, I am giving you the transcript as context, feel free to use your knowledge to answer my question.
    Answer the question as detailed as possible from the provided context. Make sure to provide all the details. If the answer is not in the provided context, just say, "answer is not available in the context", and don't provide the wrong answer.

    Context: {}
    Question: {}
    '''.format(trpt, que)
    return poompt

@st.cache_data
def AiText(url):
    print(f'Cooking initialized...\n')
    print(f'Stage I: Video download\n')
    download_youtube_video(url, output_path, '360p')
    print(f'\nStage II: Audio Extraction\n')
    extract_audio(r'D:\\Github\\Edu-AiX\\Cache\\video01.mp4', output_path)
    print(f'\nLast stage : APIs Triggered')
    ans = API()
    print(f'\nGot response successfully\nGoodBye\n')

    return ans

# Get answer from the generative AI model
def ans(promt):
    answer = model.generate_content(promt)
    return answer.text

# UI starts from here 
st.set_page_config(layout='wide')

# Hardcoded YouTube video URL which could be changed
yt_url = 'https://www.youtube.com/watch?v=RP2gIgRL6Yw'

# Get response from AI Text extraction function
X = AiText(yt_url)

st.title("Lecture QnA")

# Create two columns with the specified ratio
col1, col2 = st.columns([0.7, 0.3])

# Left column: YouTube video player
with col1:
    st.video(yt_url)

# Right column: Summarize button and bigger text box
with col2:
    input = st.text_input("Input your question ", key="input")
    submit = st.button("Ask the question")

    if submit and input:
        prmt = poopmt(input, X)
        a1 = ans(prmt)
        st.write(a1)
