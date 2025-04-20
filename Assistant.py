import sys
import os
import importlib
import threading
import keyboard
import google.generativeai as genai

script_dir = os.path.dirname(os.path.abspath(__file__))
custom_modules = os.path.join(script_dir, 'custom_modules')
modules = {}
documentation = {}
api_key = ""
wake_key = ""

def import_all_modules_from_external_folder(folder_path=custom_modules):
    # Add folder to system path
    sys.path.append(folder_path)

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove .py extension
            print(f"Importing Custom Module: {module_name}")
            module = importlib.import_module(module_name)
            modules[module_name] = module  

def list_modules_and_contents():
    for module_name, module in modules.items():
        print(f"\nModule: {module_name}")
        print("Contents:")
        # imports = [], variables = [], functions = []
        for name in dir(module):
            if name.startswith('__'): continue
            obj = getattr(module, name)
            print(f"    {type(obj).__name__} {name}")

def fetch_documentation():
    for module_name, module in modules.items():
        for name in dir(module):
            if name.startswith('__'): continue
            obj = getattr(module, name)
            # print(obj.__doc__)
            if type(obj).__name__ == "function":
                globals()[name] = obj
                if not obj.__doc__ == None:
                    documentation[f"{name}"]=  f"{obj.__doc__}"


def add_functions_to_prompt():
    global prompt
    prompt = '''
**I am your Windows Assistant. Please describe what you want me to do, or give me a command.**

**Here are some things I can understand:**

* General questions about your computer or the internet. (e.g., What is the weather today? Open Gmail)
* **Predefined commands to assist you (These will be executed by a separate program):**
'''
    for func, doc in documentation.items(): prompt = prompt + "*  **{"+func+"()}:** " + doc + "\n"

def additional_prompt():
    global prompt
    additional = '''**When clicking something make sure to figure out it's exact occurence the counting starts from top-left and ends at bottom-right.
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
    prompt = prompt + additional

def load_model(save_location):

    os.makedirs(os.path.dirname(save_location), exist_ok=True)
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

    return genai.GenerativeModel('gemini-1.5-flash',safety_settings=safety_settings)

if __name__ == "__main__":
    
    import_all_modules_from_external_folder()
    fetch_documentation()
    add_functions_to_prompt()
    additional_prompt()
    print(prompt)
    modules['IoT'].update_esp8266_ip()
    model = load_model(modules['Setup'].save_location)
    print("Loaded...")

    while True:
        if (keyboard.is_pressed('ctrl') and keyboard.is_pressed('windows')):
            command = modules['Basic'].recognize_speech()

            if command:
                command = command.lower()
                # if "hello" not in command:  continue
                img = modules['Basic'].capture_screen()
                response = model.generate_content([prompt+"\n"+"Chat History:".join(modules['Basic'].history)+"User Command:"+f'\n{command}',img])
                modules['Basic'].history.append(f'USER:{command}')
                modules['Basic'].history.append(f'ASSISTANT:{response.text}') 
                print(response.text)
                for cmd in modules['Basic'].extract_commands(response.text):
                    try:exec(cmd)
                    except Exception as error: print(error)