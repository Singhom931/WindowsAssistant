from gtts import gTTS
from Setup import save_folder
import speech_recognition as sr
import time
import threading
import tkinter as tk
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from PIL import Image, ImageTk, ImageGrab
import pyautogui
import subprocess
import requests
import PIL 

history = []

def display_text(text, duration):
    # Insert line breaks every 100 characters
    lines = [text[i:i+75] for i in range(0, len(text), 75)]
    formatted_text = '\n'.join(lines)

    # Create the overlay window
    root = tk.Tk()
    root.attributes('-alpha', 0.5)  # Set transparency (0 is fully transparent, 1 is opaque)
    root.attributes('-topmost', True)
    root.update()
    root.overrideredirect(True)  # Remove window decorations

    # Set window size based on the number of lines and length of the longest line
    line_height = 35  # Approximate height of each line
    max_line_length = max(len(line) for line in lines)
    window_width = max_line_length * 15 + 40  # Addin
    window_height = line_height * len(lines) + 40 # Adding padding
    # root.geometry(f'{len(text)*16}x100+100+100')  # Set window size and position
    root.geometry(f'{window_width}x{window_height}+100+100')  # Set window size and position
    root.configure(bg='black')  # Set background color

    # Create a label with the text
    label = tk.Label(root, text=formatted_text, font=('Helvetica', 24), fg='white', bg='black')
    label.pack(pady=1)

    # Function to close the overlay after a delay
    def close_overlay():
        root.after(int(duration * 1000), root.destroy)  # Close after 'duration' seconds

    # Close the overlay after a delay
    close_overlay()

    root.mainloop()
    return root

def speak(text, method=0):
    """Speak and Show specified text (e.g., {speak("Hello, how are you?")} , {speak("Starting Chrome")} , {speak("Should I do ...(task)?")})"""
    if method == 0:
        # Initialize pygame mixer
        pygame.mixer.init()

        # voice="en-US-Journey-F"
        tts = gTTS(text=text, lang='en')
        filename = f'{save_folder}/temp{time.time()}.mp3'
        tts.save(filename)
        
        pygame.mixer.music.load(filename)
        
        audio_duration = pygame.mixer.Sound(filename).get_length()
        pygame.mixer.music.play()

        display_text_thread = threading.Thread(target=display_text, args=([text,audio_duration]))
        display_text_thread.start()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()  # Release resources
        
        os.remove(filename)

    if method == 1:
         # Initialize pygame mixer
        pygame.mixer.init()
        
        pygame.mixer.music.load("spongebob/" + text+".wav")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()  # Release resources

def say(text, method=0):
    """Speak and Show specified text (e.g., {say("Hello, how are you?")} , {say("Starting Chrome")} , {say("Should I do ...(task)?")})"""
    speak(text, method)

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source)
    
    try:
        query = r.recognize_google(audio)
        print(f"User said: {query}")
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        query = None
    except sr.RequestError:
        print("Sorry, my speech service is down.")
        query = None
    
    return query

def launch_app(app):
    """Launches the specified application (e.g., {launch_app("Word")})."""
    pyautogui.press('win')
    time.sleep(0.2)
    pyautogui.write("Apps:"+app)
    time.sleep(0.25)
    pyautogui.press('enter')

def open_browser(url):
    """Open Browser with the url (e.g., {open_browser("https://stackoverflow.com/questions/54246668")})"""
    command = f"start chrome {url}"
    subprocess.run(command, shell=True, capture_output=True, text=True)

def youtube(query):
    """Searches YouTube for your query and plays the first result. (e.g., {youtbe("starman")})."""
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    html = requests.get('https://www.youtube.com/results?search_query='+query, headers=headers).text
    vid = html.split("watch?v=")
    if len(vid)>1:
        vid = vid[1].split("\\u")[0]
    open_browser("https://www.youtube.com/watch?v="+ vid)

def google(query):
    """Searches the web using Google (e.g., {google("best restaurants near me")}).use only when explicitly asked to use google."""
    open_browser("https://www.google.com/search?q="+"%20".join(query.split(" ")))

def capture_screen():
    pyautogui.screenshot("ss.jpg")
    screenshot = Image.open('ss.jpg')
    return screenshot

def typewrite(text):
    """Types the specified text in command-by-command mode. (e.g., {typewrite("Hello, how are you?")})"""
    pyautogui.typewrite(text)

def press(key):
    """Presses the specified key (e.g., {press("enter")} , {press("space")}). **{press("win")} will open Start Menu."""
    pyautogui.press(key)

def press_hotkeys(*args):
    """Press all the specified keys together (e.g., {press_hotkeys("shift", "end")} , {press_hotkeys("ctrl","shift", "end")})"""
    pyautogui.hotkey(*args)

def clear_history():
    global history
    """Clear all chat history, Clear all memory use when user wants to clear chat history or says clear memory."""
    history = []

def extract_commands(response_text):
    commands = [] ; in_command = False ; ignore = False ; command = ""

    for char in response_text:
        if char == '{' and in_command == False:
            in_command = True
            command = ""
            # command += char
        
        elif char == '{' and in_command == True:
            command += char
            ignore = True

        elif char == '}' and in_command == True and ignore == True:
            command += char
            ignore = False

        elif char == '}' and in_command == True and ignore == False:
            in_command = False
            commands.append(command)

        elif in_command == True:
            command += char
    return commands

if __name__ == "__main__":
    speak("Hello! This is Test.")