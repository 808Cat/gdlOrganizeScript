import subprocess
import os
import requests
import json
from pathlib import Path
import platform
import select
import sys
import time

def os_check():
    os_name = platform.system()

    if os_name == "Windows":
        return "W"
    elif os_name == "Linux":
        return "L"
    else:
        print(f"Please use Windows or Linux")
        exit()

def download_gdl():
    os_type = os_check()
    if os_type == "W":
        file_name = 'gdl.exe'
        url = 'https://github.com/mikf/gallery-dl/releases/latest/download/gallery-dl.exe'
    elif os_type == "L":
        file_name = 'gdl.bin'
        url = 'https://github.com/mikf/gallery-dl/releases/latest/download/gallery-dl.bin'

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)

    if not os.path.exists(file_path):
        print(f"Downloading {file_name}...")
        response = requests.get(url)

        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"{file_name} saved to {file_path}")
            if os_type == "L":
                os.chmod(file_path, 0o755)  # Make the binary executable on Linux
        else:
            print(f"Download failed, download Gallery-DL yourself. Status code: {response.status_code}")
            return None
    return file_path

def select_folder():
    folders = [f for f in os.listdir() if os.path.isdir(f) and not f.startswith('.') and f != "!_BASE"]

    if not folders:
        print("No folders found")
        return None

    print("\nAvailable folders:")
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder}")
    print("\nType the folder number or type 'all' for every folder. Press CTRL+C to exit")

    while True:
        choice = input("\nEnter folder number or 'all': ").strip()
        if choice.lower() == "all":
            return folders
        try:
            index = int(choice)
            if 1 <= index <= len(folders):
                selected = folders[index - 1]
                print(f"Selected folder: {selected}")
                return selected
            else:
                print("Invalid number. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number or 'all'.")

def load_sites_config(folder):
    config_path = os.path.join(folder, 'links.json')
    if not os.path.exists(config_path):
        print(f"No links.json found in {folder}")
        return None

    try:
        with open(config_path, 'r') as f:
            content = f.read()
        # I love AI
        def remove_comments(json_str):
            in_string = False
            escape = False
            cleaned = []
            i = 0
            n = len(json_str)
            while i < n:
                c = json_str[i]
                if escape:
                    cleaned.append(c)
                    escape = False
                    i += 1
                elif c == '\\':
                    cleaned.append(c)
                    escape = True
                    i += 1
                elif c == '"':
                    in_string = not in_string
                    cleaned.append(c)
                    i += 1
                elif not in_string and c == '#':
                    # Skip to end of line
                    while i < n and json_str[i] != '\n':
                        i += 1
                    # Include the newline if present
                    if i < n and json_str[i] == '\n':
                        cleaned.append('\n')
                        i += 1
                else:
                    cleaned.append(c)
                    i += 1
            return ''.join(cleaned)

        cleaned_content = remove_comments(content)
        return json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format in links.json: {e}")
        return None
    except Exception as e:
        print(f"Error reading links.json: {e}")
        return None

def download_sites(folder, gdl_path):
    sites = load_sites_config(folder)
    if not sites:
        return

    for site in sites:
        full_dir = os.path.abspath(os.path.join(folder, site["directory"]))
        Path(full_dir).mkdir(parents=True, exist_ok=True)

        command = [
            gdl_path,
            "--config-ignore",
            "--config", "gdlconf.conf",
            "-D", full_dir,
            "--no-colors",
            site["url"]
        ]

        print(f"\nDownloading: {site['url']} to {full_dir}")

        try:
            proc = subprocess.Popen(command)
        except Exception as e:
            print(f"Error starting download: {e}")
            continue

        skip_requested = False

        while proc.poll() is None:
            # Check for user input to skip
            rlist, _, _ = select.select([sys.stdin], [], [], 0)
            if rlist:
                user_input = sys.stdin.readline().strip().upper()
                if user_input == 'S':
                    skip_requested = True
                    proc.terminate()
                    break
            time.sleep(0.1)

        proc.wait()  # Ensure process termination is handled

        if skip_requested:
            print(f"Skipped {site['url']}")
        elif proc.returncode != 0:
            print(f"Download failed for {site['url']} with exit code {proc.returncode}")

if __name__ == "__main__":
    gdl_path = download_gdl()
    if not gdl_path:
        exit()

    selected_folder = select_folder()
    if not selected_folder:
        exit()

    if isinstance(selected_folder, list):
        for folder in selected_folder:
            print(f"\nProcessing folder: {folder}")
            download_sites(folder, gdl_path)
    else:
        download_sites(selected_folder, gdl_path)

    print("\nAll operations completed")
