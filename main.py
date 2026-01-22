import tkinter as tk
from tkinter import ttk
import requests
import random
import re

root = tk.Tk()
root.title("Moodify: Chat with Music")
root.geometry("300x350")

# Chat Text Widget
chat = tk.Text(root, height=25, width=60, bg="white", font=("Arial", 11), state="disabled", wrap="word")
chat.pack(pady=10)

def write(msg, tag=None):
    chat.config(state="normal")
    chat.insert(tk.END, msg + "\n\n", tag)
    chat.config(state="disabled")
    chat.see(tk.END)

# Intro message
write(
    "Welcome to Moodify!\n\n"
    "This is a mood-based song recommender.\n"
    "Choose how you feel, and I’ll suggest some songs for you!\n\n"
    "Select your mood below:"
)

# Mood selection frame
frame = tk.Frame(root, bg="#f5f5f5")
frame.pack()

tk.Label(frame, text="Select your mood:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=0, padx=5, pady=5)

moods = ["Happy", "Sad", "Relaxed", "Energetic"]
mood_var = tk.StringVar(value=moods[0])
mood_dropdown = ttk.Combobox(frame, textvariable=mood_var, values=moods, state="readonly", width=20)
mood_dropdown.grid(row=0, column=1, padx=5, pady=5)

colors = {
    "Happy": "#FFFACD",
    "Sad": "#DDEEFF",
    "Relaxed": "#E6FFE6",
    "Energetic": "#FFDDEE"
}

def get_songs(mood):
    try:
        mood_keywords = {
            "Happy": ["happy upbeat pop", "joy celebration", "cheerful music"],
            "Sad": ["melancholy ballad", "heartbreak slow", "emotional songs"],
            "Relaxed": ["chill ambient", "calm background", "soft acoustic"],
            "Energetic": ["dance party", "workout pump up", "high energy beats"]
        }
        query = random.choice(mood_keywords.get(mood, [mood]))
        # Get individual keywords to filter titles later
        keywords_to_exclude = set(word.lower() for word in query.split())

        url = f"https://itunes.apple.com/search?term={query}&media=music&limit=100"
        data = requests.get(url, timeout=5).json()

        # Helper to normalize titles
        def normalize(title):
            return re.sub(r'\W+', '', title).lower()

        seen_titles = set()
        picks = []
        for r in data.get("results", []):
            track = r.get("trackName")
            artist = r.get("artistName")
            if track and artist:
                title_norm = normalize(track)
                # Skip titles with overused words
                if "feelgood" in title_norm or "uplifting" in title_norm:
                    continue
                # Skip if title contains any of the search keywords
                if any(word in track.lower() for word in keywords_to_exclude):
                    continue
                if title_norm in seen_titles:
                    continue
                seen_titles.add(title_norm)
                picks.append((track, artist))

        random.shuffle(picks)

        formatted = [f"{track} - {artist}" for track, artist in picks]

        return formatted[:5] if formatted else ["No songs found."]

    except Exception as e:
        print("Error fetching songs:", e)
        return ["Sorry, I couldn’t fetch songs right now."]

def send():
    mood = mood_var.get()
    new_color = colors.get(mood, "#f5f5f5")
    root.configure(bg=new_color)
    frame.configure(bg=new_color)
    chat.configure(bg="white")
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.configure(bg=new_color)

    write(f"You selected: {mood}")
    songs = get_songs(mood)
    write("Here are some songs for you:\n" + "\n".join(f"  ♪ {s}" for s in songs))
    write("------------------------------------------------------------------------------------------")
    write("Want to try another mood? Just select and click again!")

btn = tk.Button(
    frame,
    text="Get Songs",
    font=("Arial", 11, "bold"),
    bg="#4CAF50",
    fg="white",
    activebackground="#45a049",
    activeforeground="white",
    command=send
)
btn.grid(row=0, column=2, padx=10)

root.mainloop()
