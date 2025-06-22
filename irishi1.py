import pyttsx3
import speech_recognition as sr
import webbrowser as wb
import time
import requests
import json
from datetime import datetime
import tkinter as tk
from threading import Thread
from vosk import Model, KaldiRecognizer
import pyaudio

# Setup for Text-to-Speech (pyttsx3)
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# API Keys and URLs
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
WEATHER_API_KEY = "449d893ea6d673b268f498a4234c5872"
CITY = "Chennai"

# Functions for the Assistant
def speak(audio: str):
    engine.say(audio)
    engine.runAndWait()

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

def get_date_time():
    now = datetime.now()
    date = now.strftime("%A, %B %d, %Y")
    time = now.strftime("%I:%M %p")
    return date, time

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

def passive_listen_wake_word():
    model = Model("model")  # Ensure to download the Vosk model from https://alphacephei.com/vosk/models
    rec = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Listening for 'irish' wake word...")

    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").lower()
            if "irish" in text:
                print("Wake word detected.")
                speak("Yes, I'm here.")
                break

# GUI Setup with Tkinter
def run_voice_assistant():
    while True:
        passive_listen_wake_word()
        query = take_command()
        if query:
            chat_box.insert(tk.END, "You: " + query + "\n")
            chat_box.yview(tk.END)

            if "open google" in query:
                speak("Opening Google")
                wb.open("https://www.google.com")

            elif "generate 3d model" in query:
                speak("Describe the 3D model.")
                model_desc = take_command()
                meshy_url = f"https://meshy.ai/?query={model_desc.replace(' ', '%20')}"
                wb.open(meshy_url)
                speak(f"Opened Meshy AI for {model_desc}")

            elif "weather" in query:
                info = get_weather()
                speak(info)
                chat_box.insert(tk.END, "Irish: " + info + "\n")

            else:
                ai_response = query_deepseek(query)
                speak(ai_response)
                chat_box.insert(tk.END, "Irish: " + ai_response + "\n")

# Create UI
root = tk.Tk()
root.title("Irish - AI Voice Assistant")
root.geometry("500x600")
root.config(bg="black")

chat_box = tk.Text(root, bg="black", fg="lime", font=("Courier", 12))
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Start assistant in a separate thread
thread = Thread(target=run_voice_assistant)
thread.start()

root.mainloop()
