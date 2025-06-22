import tkinter as tk
from tkinter import ttk
import threading
import math
from irish import take_command, speak, query_deepseek, get_weather, get_date_time, wait_for_wake_word

root = tk.Tk()
root.title("Irish - Voice Assistant")
root.geometry("400x700")
root.configure(bg="white")

# Canvas for animation
canvas = tk.Canvas(root, width=300, height=300, bg='white', highlightthickness=0)
canvas.pack(pady=60)

# Initial size
radius = 100
circle = canvas.create_oval(
    150 - radius, 150 - radius,
    150 + radius, 150 + radius,
    fill="#d6f0ff", outline="#d6f0ff"
)

# Pulse animation function
def animate_circle(step=0):
    pulse = 20 * math.sin(step / 10)  # creates smooth wave
    new_radius = 100 + pulse
    canvas.coords(circle,
        150 - new_radius, 150 - new_radius,
        150 + new_radius, 150 + new_radius
    )
    root.after(30, lambda: animate_circle(step + 1))

# Start pulsing
animate_circle()

# Voice interaction
def run_voice_assistant():
    speak("Say Irish to activate me")
    wait_for_wake_word()
    query = take_command()

    if query:
        if "weather" in query:
            response = get_weather()
        elif "time" in query or "date" in query:
            date, current_time = get_date_time()
            response = f"It's {current_time} on {date}"
        else:
            response = query_deepseek(query)

        speak(response)

# Thread wrapper
def start_thread():
    threading.Thread(target=run_voice_assistant, daemon=True).start()

# Mic Button
mic_btn = ttk.Button(root, text="Speak", command=start_thread)
mic_btn.pack(pady=20)

# Exit Button
exit_btn = ttk.Button(root, text="Close", command=root.destroy)
exit_btn.pack(pady=10)

root.mainloop()