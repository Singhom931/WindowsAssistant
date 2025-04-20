import tkinter as tk
from pathlib import Path
import os

save_folder = r'C:\Assistant'
save_location = r'C:\Assistant\api.key.txt'
prompt_location = r'C:\Assistant\prompt.txt'

Path(save_folder).mkdir(parents=True, exist_ok=True)
if not Path(save_location).exists(): Path(save_location).write_text("")
if not Path(prompt_location).exists(): Path(prompt_location).write_text("")


def get_api_key(location=save_location):
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

clear_temp_mp3_files(save_folder)
    
if __name__ == "__main__":
    get_api_key()