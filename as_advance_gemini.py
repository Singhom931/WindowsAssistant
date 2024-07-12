import os
#import shutil
import speech_recognition as sr
from gtts import gTTS
import pygame
import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk, ImageGrab
import threading
import pyautogui
import time
import requests
import PIL
import subprocess
import pytesseract
# import webbrowser

def get_api_key(location):
    def display_text_and_close():
        print(f"You entered: {text_entry.get()}")
        with open(location, "w") as f:
            f.write(text_entry.get())
        root.destroy()

    root = tk.Tk()
    tk.Label(root, text="Enter Gemini API key:").pack(pady=5)
    text_entry = tk.Entry(root, width=30)
    text_entry.pack(pady=5)
    tk.Button(root, text="Submit", command=display_text_and_close).pack(pady=5)
    root.mainloop()

def clear_temp_mp3_files(folder_path):
    # List all files in the specified folder
    files = os.listdir(folder_path)
    # Iterate through the files
    for file in files:
        # Check if the file starts with 'temp' and ends with '.mp3'
        if file.startswith('temp') and file.endswith('.mp3'):
            file_path = os.path.join(folder_path, file)
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

save_folder = r'C:\Assistant'
save_location = r'C:\Assistant\api.key.txt'

clear_temp_mp3_files(save_folder)

if not os.path.exists(os.path.dirname(save_location)):
    try:
        os.makedirs(os.path.dirname(save_location))
    except OSError as exc: # Guard against race condition
        exit()
if not os.path.isfile(save_location):
    get_api_key(save_location)
    


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

screen_width, screen_height = pyautogui.size()

def capture_screen():
    # Capture the screen using PIL's ImageGrab
    screenshot = ImageGrab.grab()
    return screenshot

def locate_text_on_screen(text_to_find,screenshot):
    text_to_find = text_to_find.lower()
    
    # Capture the screen
    # screenshot = capture_screen()
    
    # Perform OCR on the screenshot
    data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
    
    # List to store all occurrences' coordinates
    occurrences = []
    for_each_word = []
    y_check = []
    group_words = []
    # Iterate through OCR data to find all occurrences of the specified text
    n_boxes = len(data['text'])
    if len(text_to_find.split(" "))==1:
        for i in range(n_boxes):
            if text_to_find.lower() in data['text'][i].lower():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                occurrences.append((x, y, x + w, y + h))  # Store coordinates as (x1, y1, x2, y2)
        
        return occurrences
    else:
        for word in text_to_find.lower().split(" "):
            for_this_word = []
            for i in range(n_boxes):
                if word in data['text'][i].lower() and len(for_each_word)==0:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    for_this_word.append((x, y, x + w, y + h))  # Store coordinates as (x1, y1, x2, y2)
                    y_check.append((y, y + h))
                elif word in data['text'][i].lower():
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    if (y,y+h) in y_check:
                        for_this_word.append((x, y, x + w, y + h))
            for_each_word.append(for_this_word)

        for y_lvl in y_check:
            y_group = []
            for word in for_each_word:
                for coords in word:
                    if (coords[1],coords[3]) == y_lvl:
                        y_group.append(coords)
            group_words.append(y_group)
        
        for item in group_words:
            if len(item)==len(text_to_find.split(" ")) and (item[0][0]<item[-1][0] and item[0][2]<item[-1][2]):
                occurrences.append((item[0][0],item[0][1],item[-1][2],item[-1][3]))

        return occurrences

def create_overlay_windows(root, occurrences):
    for idx, (x1, y1, x2, y2) in enumerate(occurrences):
        x1 = x1-5 ; y1 = y1-5 ; x2 = x2+5 ; y2 = y2+5
        overlay = tk.Toplevel(root)
        overlay.attributes('-alpha', 0.5)  # Set transparency (0.0 to 1.0)
        overlay.attributes('-topmost', True)
        overlay.overrideredirect(True)  # Remove window borders
        overlay.geometry(f"{x2 - x1}x{y2 - y1}+{x1}+{y1}")  # Set window size and position
        
        # Draw green rectangle
        canvas = tk.Canvas(overlay, bg='green', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=tk.YES)
        canvas.create_rectangle(0, 0, x2 - x1, y2 - y1, outline='', fill='green')
        
        # Add numbered label
        bg = tk.Label(overlay, bg='green', font=('Arial', 10, 'bold'))
        label = tk.Label(overlay, text=str(idx + 1), font=('Arial', 16, 'bold'))
        bg.place(relx=0.5, rely=0.5, anchor='center')
        label.place(relx=0.5, rely=0.5, anchor='center')

def find_text_on_screen(text_to_find):
    time.sleep(0.1)
    # text_to_find = "test"
    screenshot = capture_screen()

    root = tk.Tk()
    root.attributes('-alpha', 0.0)  # Set root window transparent for demonstration
    root.attributes('-topmost', True)
    # root.update()
    # root.overrideredirect(True)  # Remove window decorations
    
    # root.withdraw()  # Hide the root window
    
    # Locate text on the screen
    occurrences = locate_text_on_screen(text_to_find,screenshot)
    
    # Create overlay windows for each occurrence
    # create_overlay_windows_thread = threading.Thread(target=create_overlay_windows, args=([root, occurrences]))
    # create_overlay_windows_thread.start()
    
    create_overlay_windows(root, occurrences)

    def close_overlay():
        root.after(int(3 * 1000), root.destroy)  # Close after 'duration' seconds

    # Close the overlay after a delay
    close_overlay()
    
    root.mainloop()

    return occurrences


# import Gemini
import google.generativeai as genai

# Replace 'YOUR_API_KEY' with your actual API key
api_key = ""
with open(save_location, 'r') as file:
    api_key = file.read()

genai.configure(api_key=api_key)

safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS","threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel('gemini-1.5-flash',safety_settings=safety_settings)
# model2 = genai.GenerativeModel('gemini-1.5-flash',safety_settings=safety_settings)

# *  **{left_click(x,y)}:** Left-Clicks at the specified coordinates on the screen. **screen width is 1366 and height is 768 **0,0 is the top-left corner of the screen.
# *  **{right_click(x,y)}:** Right-clicks at the specified coordinates on the screen. **screen width is 1366 and height is 768 **0,0 is the top-left corner of the screen.
#**Relate to users emotions and feelings. and show them things that are chaotic , violent or thrilling like think about content they might like.
#(example: brainrot, skibidi, sigma , What the sigma! , goat , cap , ohio, gyatt, rizz )
# **Additional Details: Relate to the user and be funny and use Gen Alpha slangs also sometimes give them a surprise but not too frequently like 1 in 7 times.

prompt = '''**I am your Windows Assistant. Please describe what you want me to do, or give me a command.**

**Here are some things I can understand:**

* General questions about your computer or the internet. (e.g., What is the weather today? Open Gmail)
* **Predefined commands to assist you (These will be executed by a separate program):**
    *  **{launch_app(app)}:** Launches the specified application (e.g., {launch_app("Word")}).
    *  **{google(query)}:** Searches the web using Google (e.g., {google("best restaurants near me")}).
    *  **{gpt(query)}:** Sends your query to GPT (e.g., {gpt("write a poem about nature")}).
    *  **{youtube(query)}:** Searches YouTube for your query and plays the first result. (e.g., {youtbe("starman")}).
    *  **{take_screenshot()}:** Takes a screenshot and saves it to your Pictures folder.
    *  **{left_click(text,occurence_number)}:** Left-Clicks on the nth occurrence of the specified text on the screen. Occurence is counted from top to bottom and left to right. (example: {left_click("file",3)}).
    *  **{right_click(text,occurence_number)}:** Right-clicks on the nth occurrence of the specified text on the screen. Occurence is counted from top to bottom and left to right. (example: {left_click("file",3)}).
    *  **{double_click(text,occurence_number)}:** Double-clicks on the nth occurrence of the specified text on the screen. Occurence is counted from top to bottom and left to right.Use Double click when trying to open a file or launch app or edit a textbox etc. (example: {double_click("file",3)}).
    *  **{typewrite(text)}:** Types the specified text in command-by-command mode. (e.g., {typewrite("Hello, how are you?")})
    *  **{press(key)}:** Presses the specified key (e.g., {press("enter")} , {press("space")}). **{press("win")} will open Start Menu.
    *  **{press_hotkeys(keys)}:** Press all the specified keys together (e.g., {press_hotkeys("shift", "end")} , {press_hotkeys("ctrl","shift", "end")})
    *  **{say(text)}:** Speak and Show specified text (e.g., {say("Hello, how are you?")} , {say("Starting Chrome")} , {say("Should I do ...(task)?")})
    *  **{clear_history()}** Clear all chat history, Clear all memory use when user wants to clear chat history or says clear memory.
    *  **{stop_listening()}** Stops taking input from user. Only use when user asks for it to be used.
**When clicking something make sure to figure out it's exact occurence the counting starts from top-left and ends at bottom-right.
**When asked to read something I will use the provided image and read it using {say(text)} (e.g. {say("Once upon a time ....")})
**When asked to solve a Math Question I will take extra care to check all symbols such as root , power , log , etc even if the equation is in a image take extra care.
**I will never try to use a function not listed above.
**I can only use the functions and can't send anything except functions
**ScreenShots I recieve might not capture the full code so I will take that in Consideration before pointing out false positive issues.
**I will take care that the functions I send have both opening and closing brackets for commands that includes both {} and ().
**I will never say anything without using {say(text)} and every {say(text)} will be less than 100 chars    
**I will never use a function inside another (e.g., {say{"playing song{youtube("song")}"}) instead will split it in such format {say{"playing song"}}...{youtube("song")}}.
**I will never use {launch_app("youtube")}, {launch_app("google")} or {launch_app("gpt")} as they have their own predefined functions {youtube(query)} {google(query)} {gpt(query)}.
**I will try my best to follow your instructions and complete your requests. If my instructions involve predefined commands, they will be sent to a separate program for execution.**
**I will always use {say(text)} with short messeage about what im doing and I will keep it intresting.
**I will always complete every task given to me and will skip nothing ever.
**I will try to answer myself using {say(text)} if I can't only then will use other tools/commands.
**I will use Chat History: as context not command, only stuff after User : is command. 
**I will ignore Chat History: unless its needed for some specific context.
**I will never send Chat History in response.
**I will never do something said in Chat History unless it's related to the current command.
**Please note:** I cannot directly control your computer's hardware, but I can help you achieve your goals through a combination of instructions and predefined commands.
'''



def show_spongebob(text,duration=1):
    image_path = "spongebob/spongebob (Custom).png"
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-alpha', 1)
    root.attributes('-topmost', True)
    root.update()
    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)

    label = tk.Label(root, image=photo, bg='white')
    root.overrideredirect(True)
    label.pack()

    root.wm_attributes("-transparentcolor", "white")

    window_width = image.width
    window_height = image.height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = -10 #(screen_width - window_width) // 100
    y = (screen_height - window_height) // 5
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    # Function to close the overlay after a delay
    def close_overlay():
        root.after(int(len(text)/6)* duration * 1000, root.destroy)  # Close after 'duration' seconds

    # Close the overlay after a delay
    close_overlay()

    root.mainloop()

def capture_screen():
    screenshot = pyautogui.screenshot()
    return screenshot 

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

def speak(text, method=0):
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
        
def bot_say(text, duration=1):

    # display_text_thread = threading.Thread(target=display_text, args=([text, duration]))
    # display_text_thread.start()

    # speak_thread = threading.Thread(target=speak, args=([text]))
    # speak_thread.start()
    speak(text)

    # display_text(text, duration)
    # speak_thread.join()

def spongebob_say(text,file, duration=1):

    speak_thread = threading.Thread(target=speak, args=([file,1]))
    speak_thread.start()

    # show_spongebob(text,duration)
    show_spongebob_thread = threading.Thread(target=show_spongebob, args=([text,duration]))
    show_spongebob_thread.start()


    # display_text(text, duration)
    display_text_thread = threading.Thread(target=display_text, args=([text,duration]))
    display_text_thread.start()

def say(text):
    bot_say(text)

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
    pyautogui.press('win')
    time.sleep(0.2)
    pyautogui.write("Apps:"+app)
    time.sleep(0.25)
    pyautogui.press('enter')
    pass

def open_browser(url):
    # Construct the command to open the browser with a specific window size
    command = f"start chrome {url}"
    # webbrowser.open_new(command)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Print the result
    print(result.stdout)

def youtube(query):
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    html = requests.get('https://www.youtube.com/results?search_query='+query, headers=headers).text
    vid = html.split("watch?v=")
    if len(vid)>1:
        vid = vid[1].split("\\u")[0]

    # pyautogui.press('win')
    # time.sleep(0.2)
    # pyautogui.write("https://www.youtube.com/watch?v="+ vid)
    # time.sleep(0.25)
    # pyautogui.press('enter')

    open_browser("https://www.youtube.com/watch?v="+ vid)

def google(query):
    # pyautogui.press('win')
    # time.sleep(0.2)
    # pyautogui.write("https://www.google.com/search?q="+ query)
    # time.sleep(0.25)
    # pyautogui.press('enter')

    open_browser("https://www.google.com/search?q="+"%20".join(query.split(" ")))

def gpt(query):
    # pyautogui.press('win')
    # time.sleep(0.2)
    # pyautogui.write("https://chat.openai.com/?q="+ query)
    # time.sleep(0.25)
    # pyautogui.press('enter')

    open_browser("https://chat.openai.com/?q="+"%20".join(query.split(" ")))

def double_click(text,occurence_number):
    occurences = find_text_on_screen(text)
    occurence = occurences[occurence_number-1]
    x = (occurence[0] + occurence[2])//2
    y = (occurence[1] + occurence[3])//2
    pyautogui.click(x,y)
    time.sleep(0.05)
    pyautogui.click(x,y)

def left_click(text,occurence_number):
    occurences = find_text_on_screen(text)
    occurence = occurences[occurence_number-1]
    x = (occurence[0] + occurence[2])//2
    y = (occurence[1] + occurence[3])//2
    pyautogui.click(x,y)

def right_click(text,occurence_number):
    occurences = find_text_on_screen(text)
    occurence = occurences[occurence_number-1]
    x = (occurence[0] + occurence[2])//2
    y = (occurence[1] + occurence[3])//2
    pyautogui.click(x,y,button="right")

def stop_listening():
    global listen
    listen = False

def start_listening():
    global listen
    listen = True

def typewrite(text):
    pyautogui.typewrite(text)

def press(key):
    pyautogui.press(key)

def press_hotkeys(*args):
    pyautogui.hotkey(*args)

def take_screenshot():
    # pyautogui.screenshot("ss.jpg")
    # loop()
    pass

def loop():
    global in_progress
    in_progress = True

def clear_history():
    global history
    history = []

def extract_commands(parsed):
    commands = [] ; in_command = False ; ignore = False ; command = ""

    for char in response.text:
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

bot_say("Hello! How can I assist you?")

history = []
in_progress = False
command = None
response = None
img = None
listen = True
# left_click("Google Maps",1)
while True:
        if in_progress == False:
            command = recognize_speech()
        
        if command:
            if in_progress == False:
                command = command.lower()
                if "start listening" in command:
                    start_listening()

                pyautogui.screenshot("ss.jpg")
                img = PIL.Image.open('ss.jpg')
            
            else:
                img = PIL.Image.open('ss.jpg')

            in_progress = False
            if listen == False:
                time.sleep(0.25)
                continue

            response = model.generate_content([prompt+"\n"+"Chat History:".join(history)+"User Command:"+f'\n{command}',img])

            history.append(f'USER:{command}')
            history.append(f'ASSISTANT:{response.text}') 

            print(response.text)
            for cmd in extract_commands(response.text):
                try:exec(cmd)
                except Exception as error:print(error)

               

