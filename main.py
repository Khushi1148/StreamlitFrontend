import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch API URLs from environment variables
BACKEND_URL = os.getenv("BACKEND_URL")
FETCH_SUMMARIZE_ENDPOINT = os.getenv("FETCH_SUMMARIZE_ENDPOINT")
TTS_ENDPOINT = os.getenv("TTS_ENDPOINT")
IMAGE_GEN_ENDPOINT = os.getenv("IMAGE_GEN_ENDPOINT")

# Function to fetch and summarize news
def fetch_and_summarize(query, tone, platform, language="en"):
    payload = {
        "query": query,
        "language": language,
        "tone": tone,
        "platform": platform
    }
    try:
        response = requests.post(BASE_URL + FETCH_SUMMARIZE_ENDPOINT, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching news: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend: {e}")
        return None

# Function to convert text to speech
def convert_text_to_speech(text):
    payload = {"text": text}
    try:
        response = requests.post(BASE_URL + TTS_ENDPOINT, json=payload)
        if response.status_code == 200:
            return response.json().get("audio_file_path")
        else:
            st.error(f"Error in text-to-speech conversion: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend: {e}")
        return None

# Function to generate image from text
def generate_image_from_summary(text):
    payload = {"text": text}
    try:
        response = requests.post(BASE_URL + IMAGE_GEN_ENDPOINT, json=payload)
        if response.status_code == 200:
            return response.json().get("image_urls", [])
        else:
            st.error(f"Error in image generation: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend: {e}")
        return []

# Initialize session state for storing the summary
if "news_summary" not in st.session_state:
    st.session_state["news_summary"] = ""

# App title and description
st.markdown("<h1 style='text-align: center; font-size: 45px;'>Accessible Times</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px;'>An AI-powered news summarizer and text-to-speech app for daily updates</p>", unsafe_allow_html=True)

# User input for query
query = st.text_input("Enter your news search query:", placeholder="e.g., AI breakthroughs in 2024")

# Layout to make tone and platform selection side by side
col1, col2 = st.columns(2)
with col1:
    tone = st.selectbox("Select Tone", ["Professional", "Casual", "Humour"])
with col2:
    platform = st.selectbox("Select Platform", ["LinkedIn", "Instagram", "Twitter"])

# Generate button
if st.button("Generate"):
    if query:
        result = fetch_and_summarize(query, tone, platform)
        if result:
            # Store the summary in session state
            st.session_state["news_summary"] = result["summary"]

            # Display news summary
            st.subheader("News Summary:")
            st.write(result["summary"])

            # Display individual articles
            st.subheader("Articles:")
            for article in result["articles"]:
                st.markdown(f"*{article['title']}*")
                st.markdown(f"{article['description']}")
                st.markdown(f"[Read more]({article['url']})", unsafe_allow_html=True)

    else:
        st.error("Please enter a news query.")

# Convert summary to speech button
if st.session_state["news_summary"]:
    if st.button("Convert Summary to Speech"):
        audio_file_path = convert_text_to_speech(st.session_state["news_summary"])
        if audio_file_path:
            st.audio(audio_file_path, format="audio/mp3")
        else:
            st.error("Failed to generate speech audio.")

# Generate image from summary button
if st.session_state["news_summary"]:
    if st.button("Generate Image from Summary"):
        image_urls = generate_image_from_summary(st.session_state["news_summary"])
        if image_urls:
            st.subheader("Generated Image:")
            for url in image_urls:
                st.image(url)
        else:
            st.error("Failed to generate image.")
