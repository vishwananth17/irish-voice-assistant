import streamlit as st
import pyttsx3
import speech_recognition as sr
import webbrowser as wb
import time
import requests
import json
from datetime import datetime

# Replace your existing API keys and variables
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
WEATHER_API_KEY = "449d893ea6d673b268f498a4234c5872"
CITY = "Chennai"

# Initialize the pyttsx3 engine for voice
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        st.info("🔍 Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        st.success(f"🗣 You said: {query}")
        return query.lower()
    except:
        st.warning("Sorry, I didn't catch that.")
        return ""

# Your existing functions
def get_date_time():
    now = datetime.now()
    date = now.strftime("%A, %B %d, %Y")
    time_now = now.strftime("%I:%M %p")
    return date, time_now

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]
            return f"The current temperature in {CITY} is {temp}°C with {weather_desc}."
        else:
            return "Sorry, couldn't fetch weather."
    except:
        return "Error connecting to weather API."

def query_deepseek(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "DeepSeek couldn't respond."

# Streamlit UI
st.set_page_config(page_title="Irish - Voice Assistant", page_icon="🎤")
st.title("🤖 Irish - Your AI Voice Assistant")

if st.button("🎙 Speak Now"):
    query = take_command()
    response = ""

    # Here you can match different conditions based on the query
    if "open google" in query:
        speak("Opening Google.")
        wb.open("https://www.google.com")
        speak("What do you want to search?")
        search_query = take_command()
        if search_query:
            search_url = f"https://www.google.com/search?q={search_query}"
            wb.open(search_url)
            response = f"Searching Google for {search_query}."

    elif "generate 3d model" in query:
        speak("Please describe the 3D model you want.")
        model_description = take_command()
        if model_description:
            url = f"https://meshy.ai/?query={model_description.replace(' ', '%20')}"
            wb.open(url)
            response = f"Generating 3D model for {model_description}"

    elif "time" in query:
        _, time_now = get_date_time()
        response = f"The time is {time_now}"

    elif "date" in query:
        date, _ = get_date_time()
        response = f"Today's date is {date}"

    elif "weather" in query:
        response = get_weather()

    elif query:
        response = query_deepseek(query)

    st.success(f"🤖 Irish says: {response}")
    speak(response)
