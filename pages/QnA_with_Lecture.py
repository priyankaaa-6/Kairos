# Importing libraries
from pprint import pprint  # Used for formatted, readable printing of data.
import requests  # Library for making HTTP requests to APIs.
from pytube import YouTube  # Library for downloading YouTube videos.
import os  # Provides functions to interact with the operating system.
from moviepy.video.io.VideoFileClip import VideoFileClip  # Handles video manipulation (e.g., audio extraction).
import streamlit as st  # A framework for building web applications.
import json  # Library for working with JSON files.

from dotenv import load_dotenv  # Loads environment variables from a `.env` file.
load_dotenv()  # Loads all the environment variables from the `.env` file.
import google.generativeai as genai  # Library for interacting with Google Generative AI API.
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Configures the API key for Google Generative AI.
model = genai.GenerativeModel('gemini-pro')  # Initializes a specific AI model.


# Creating a cache folder to store temporary files
path = 'D:\\Github\\Edu-AiX'  # Defines the base project path.
cache_folder = os.path.join(path, 'Cache')  # Creates a subfolder named `Cache`.
os.makedirs(cache_folder, exist_ok=True)  # Creates the `Cache` folder if it does not exist.
output_path = os.path.abspath(cache_folder)  # Converts the path to an absolute path.

# Function to download a YouTube video
def download_youtube_video(youtube_url, output_path='.', resolution='360p'):
    if os.path.exists(r'Cache/video01.mp4'):  # If the video already exists, skip downloading.
        return 
    else:
        try:
            youtube = YouTube(youtube_url)  # Initializes the YouTube video object.
            video_stream = youtube.streams.get_by_resolution(resolution)  # Gets the video stream for the desired resolution.
            if video_stream:
                video_stream.download(output_path, filename='video01.mp4')  # Downloads the video as `video01.mp4`.
                print(f"Video download successful in {resolution} resolution! Saved as video01.mp4")
            else:
                print(f"Error: Video stream with {resolution} resolution not available.")  # Handles missing resolution cases.
        except Exception as e:
            print(f"Error: {e}")  # Handles exceptions during video download.

# Function to extract audio from the downloaded video
def extract_audio(video_path, output_audio_path):
    if os.path.exists(r'Cache/extracted-audio.mp3'):  # If audio already exists, skip extraction.
        return
    else:    
        try:
            video_clip = VideoFileClip(video_path)  # Loads the video for processing.
            audio_clip = video_clip.audio  # Extracts audio from the video.
            output_audio_path = os.path.join(output_audio_path, 'extracted-audio.mp3')  # Sets output file name.
            audio_clip.write_audiofile(output_audio_path)  # Saves the audio as an MP3 file.
            print("Audio extraction successful!")
        except Exception as e:
            print(f"Error: {e}")  # Handles exceptions during audio extraction.

# Function to interact with an external API for audio transcription
def API():
    res = {}  # Placeholder for API response data.

    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-medium.en"  # Endpoint for transcription API.
    headers = {"Authorization": "Bearer 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"}  # Authorization header.

    def query(filename):  # Sub-function to send audio file to the API.
        with open(filename, "rb") as f:
            data = f.read()  # Reads the audio file.
        response = requests.post(API_URL, headers=headers, data=data)  # Sends POST request to the API.
        return response.json()  # Returns the JSON response.

    print('done till here')  # Debug message.
    if not os.path.exists(r'Cache/trpt.json'):  # Checks if the transcript file already exists.
        output = query(r"D:\\Github\\Edu-AiX\\Cache\\extracted-audio.mp3")  # Sends the audio file for transcription.
        story = output['text']  # Extracts text (transcription) from the API response.
        file_path = r"Cache/trpt.json"  # File path to store the transcript.
        with open(file_path, "w") as json_file:
            json.dump(story, json_file)  # Writes the transcription to a JSON file.
    else:
        print('By-passing due to API issue')  # Debug message for skipping API call.
        with open(r'D:\\Github\\Edu-AiX\\Cache\\trpt.json', 'r') as file:
            quiz_data = json.load(file)  # Reads the existing transcript.
        story = quiz_data
    return story  # Returns the transcript.


# Function to create a prompt for the AI
def poopmt(que, trpt):
    poompt = '''
    I was studying from a youtube video, and I have a question, I am giving you transcript as context. Feel free to use your knowledge to answer my question.
    Answer the question as detailed as possible from the provided context. If the answer is not in
    provided context, just say, "Answer is not available in the context", don't provide the wrong answer.\n\n
    Context: {}\nQuestion: {}
    '''.format(trpt, que)  # Inserts transcript and question into the template.
    return poompt  # Returns the formatted prompt.

# Function to process the video and extract content using the AI
@st.cache_data  # Caches the function output to avoid repetitive computations.
def AiText(url):
    print(f'Cooking initialized...\n')  # Debug message.
    print(f'Stage I: Video download\n')
    download_youtube_video(url, output_path, '360p')  # Downloads the video.
    print(f'\nStage II: Audio Extraction\n')
    extract_audio(r'D:\\Github\\Edu-AiX\\Cache\\video01.mp4', output_path)  # Extracts audio from the video.
    print(f'\nLast stage: APIs Triggered')
    ans = API()  # Calls the API for transcription.
    print(f'\nGot response successfully\nGoodbye\n')
    return ans  # Returns the transcription.

# Function to get an AI-generated answer
def ans(promt):
    answer = model.generate_content(promt)  # Generates content using the AI model.
    return answer.text  # Returns the generated text.

# Streamlit UI configuration and logic
st.set_page_config(layout='wide')  # Sets the web app layout to "wide".

# Hardcoded YouTube video URL (can be replaced).
yt_url = 'https://www.youtube.com/watch?v=RP2gIgRL6Yw'

# Process the YouTube video and get the transcript.
X = AiText(yt_url)

# Sets the title for the web app.

# Page Configurations
#.set_page_config(page_title="Kairos", layout="wide")  # Sets the page title and layout configuration
st.title("AI-Powered Learning Companion - Kairos!")  # App header
st.title("Lecture QnA")
# Create two columns with specific proportions.
col1, col2 = st.columns([0.7, 0.3])

# Display the video in the left column.
with col1:
    st.video(yt_url)

# Display user input and response logic in the right column.
with col2:
    input = st.text_input("Input your question", key="input")  # Text box for user question.
    submit = st.button("Ask the question")  # Button to submit the question.

    if submit and input:  # Checks if button is clicked and input is provided.
        prmt = poopmt(input, X)  # Creates a prompt using the transcript and user question.
        a1 = ans(prmt)  # Gets AI's response.
        st.write(a1)  # Displays the AI response.

# Footer with Project Description
st.markdown(
    """
    <div style="position: fixed; bottom: 20px; right: 20px; font-size: 12px; color: grey; text-align: right;">
        <b>About Kairos:</b> An AI-powered educational tool for PDF analysis, quiz generation, and enhanced learning.
    </div>
    """,
    unsafe_allow_html=True
)
