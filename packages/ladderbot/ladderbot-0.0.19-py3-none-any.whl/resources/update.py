import os
import requests
from tkinter import messagebox

VERSION = 0.0
APP_NAME = 'LadderSlasher.exe'
LATEST_VERSION_URL = "https://raw.githubusercontent.com/7urtles/LadderSlasher/main/version.txt"
LATEST_VERSION_BINARY_URL = "https://github.com/7urtles/LadderSlasher/releases/latest/download/LadderSlasher.exe"

def rename_file(old_path, new_name):
    try:
        # Split the old path into its directory and filename
        directory, filename = os.path.split(old_path)
        # Split the filename into its name and extension
        name, extension = os.path.splitext(filename)
        # Construct the new filename by combining the new name and the extension
        new_filename = f"{new_name}{extension}"
        # Construct the new path by combining the directory and the new filename
        new_path = os.path.join(directory, new_filename)
        # Rename the file using its old path and its new path
        os.rename(old_path, new_path)
    except Exception as e:
        print(e)
        input()
        exit()

def delete_old_version(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(e)
        input()
        exit()


def new_version_available():
    try:
        LATEST_VERSION = requests.get(LATEST_VERSION_URL).text.strip()
        print(f"Current version: {VERSION}\nLatest version: {LATEST_VERSION}")
        if float(VERSION) < float(LATEST_VERSION):
            return True
        return False
    except Exception as e:
        print(e)
        input()
        exit()

def download_update():
    try:
        result = requests.get(
            LATEST_VERSION_BINARY_URL,
            allow_redirects = True
        )
        open(APP_NAME, 'wb').write(result.content)
        messagebox.showinfo("Update Applied", "reopen to run new version")
    except Exception as e:
        print(e)
        input()
        exit()

def run():
    delete_old_version('previous_version.exe')
    if new_version_available():
        rename_file(APP_NAME, 'previous_version')
        download_update()



