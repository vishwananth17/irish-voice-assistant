import pyttsx3
import speech_recognition as sr
import webbrowser as wb
import time
import requests
import json
from datetime import datetime 
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
WEATHER_API_KEY = "449d893ea6d673b268f498a4234c5872 "
CITY = "Chennai" 
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Function to speak output
def speak(audio: str):
    engine.say(audio)
    engine.runAndWait()

# Function to take command using the microphone
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Processing...")
        query = r.recognize_google(audio, language="en-in")
        print("User said:", query)
        return query.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("There is a problem with the speech recognition service.")
        return None

# Get date and time
def get_date_time():
    now = datetime.now()
    date = now.strftime("%A, %B %d, %Y")
    time = now.strftime("%I:%M %p")
    return date, time

# Get weather information
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
            return "Sorry, I couldn't fetch the weather."
    except requests.exceptions.RequestException:
        return "Couldn't connect to the weather service."

# Emotion detection function (example with Deepgram API)
def detect_emotion(text: str) -> str:
    emotion_api_url = "https://api.deepgram.com/v1/analyze"
    headers = {
        "Authorization": f"7c1b0dcbb02e425b7bedd86677fccfaa46ee5bf3",
        "Content-Type": "application/json"
    }
    data = {
        "model": "general",
        "text": text
    }
    
    try:
        response = requests.post(emotion_api_url, headers=headers, json=data)
        response.raise_for_status()
        emotion_data = response.json()
        emotion = emotion_data['results'][0]['emotion']
        return emotion
    except requests.exceptions.RequestException as e:
        return "Emotion detection failed."

# Query DeepSeek AI
def query_deepseek(prompt: str) -> str:
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
        response.raise_for_status()
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"
    except json.JSONDecodeError:
        return "Error decoding response from DeepSeek."

# Main wake word loop
def wait_for_wake_word():
    while True:
        print("Say 'Irish' to activate...")
        command = take_command()
        if command and "irish" in command:
            speak("I am listening")
            return

# Main function to handle assistant logic
if __name__ == "__main__":
    while True:
        wait_for_wake_word()
        query = take_command()

        if query:
            if "open google" in query:
                speak("Opening Google")
                wb.open("https://www.google.com")
                time.sleep(1)

                speak("What do you want to search?")
                search_query = take_command()

                if search_query:
                    print("Searching for:", search_query)
                    search_url = f"https://www.google.com/search?q={search_query}"
                    speak(f"Searching Google for {search_query}")
                    wb.open(search_url)

            elif "generate 3d model" in query:
                speak("Please describe the 3D model you want to generate.")
                model_description = take_command()

                if model_description:
                    print("Generating 3D model for:", model_description)
                    meshy_url = f"https://meshy.ai/?query={model_description.replace(' ', '%20')}"
                    speak(f"Opening Meshy AI for {model_description}")
                    wb.open(meshy_url)

            elif "what's the time" in query or "tell me the time" in query:
                date, current_time = get_date_time()
                speak(f"The time is {current_time}")

            elif "what's the date" in query or "tell me the date" in query:
                date, _ = get_date_time()
                speak(f"Today is {date}")

            elif "what's the weather" in query or "tell me the weather" in query:
                weather_info = get_weather()
                speak(weather_info)

            else:
                ai_response = query_deepseek(query)
                print("irish:", ai_response)
                speak(ai_response)

                # Emotion detection based on user query
                emotion = detect_emotion(query)
                print(f"Detected emotion: {emotion}")
                speak(f"Detected emotion: {emotion}")
