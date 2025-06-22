#!/usr/bin/env python3
import subprocess
import os
import requests
import json
from pathlib import Path
import platform
import select
import sys
import time
import threading

def os_check():
    os_name = platform.system()

    if os_name != "Linux":
        print(f"Please use Linux or modify the script, Sorry for the inconvenience.")
        exit()

def download_gdl():
    os_check()
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
            os.chmod(file_path, 0o755) # Make the binary executable
        else:
            print(f"Download failed, download Gallery-DL yourself. Status code: {response.status_code}")
            return None
    return file_path

def error(message, show=True):
    if show:
        print(message)
    with open('errors.log', 'a', encoding='utf-8') as log_file:
        log_file.write(f"{message}\n")

def select_folder():
    folders = [f for f in os.listdir() if os.path.isdir(f) and not f.startswith('.') and f != "!_BASE" and f != "!_git" and f != "!_old"]

    if not folders:
        print("No folders found")
        return None

    print("\nAvailable folders:")
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder}")
    print("\nType the folder number, 'all' for every folder, or 'startfromX' to start from folder X. Press CTRL+C to exit")

    while True:
        choice = input("\nEnter folder number, 'all', or 'startfromX': ").strip().lower()
        if choice == "all":
            print("Selected all folders.")
            return folders
        elif choice.startswith("startfrom"):
            if len(choice) == 9:
                print("Please provide a number after 'startfrom' (e.g., 'startfrom3').")
                continue
            num_str = choice[9:]
            try:
                start_num = int(num_str)
                if 1 <= start_num <= len(folders):
                    selected = folders[start_num - 1:]
                    print(f"Starting from folder {start_num}\n---------\n{'\n'.join(selected)}")
                    return selected
                else:
                    print(f"Start number must be between 1 and {len(folders)}.")
            except ValueError:
                print("Invalid format after 'startfrom'. Use 'startfromX' where X is a number.")
        else:
            try:
                index = int(choice)
                if 1 <= index <= len(folders):
                    selected = folders[index - 1]
                    print(f"Selected folder: {selected}")
                    return selected
                else:
                    print(f"Invalid number. Please enter a number between 1 and {len(folders)}.")
            except ValueError:
                print("Invalid input. Please enter a valid number, 'all', or 'startfromX'.")

def load_sites_config(folder):
    config_path = os.path.join(folder, 'links.json')
    if not os.path.exists(config_path):
        error(f"No links.json found in {folder}")
        return None

    try:
        with open(config_path, 'r') as f:
            content = f.read()
        # Thanks deepseek
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
                    while i < n and json_str[i] != '\n':
                        i += 1
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
        error(f"Invalid JSON format in {folder}'s links.json: {e}")
        return None
    except Exception as e:
        error(f"Error reading links.json: {e}")
        return None

def download_sites(folder, gdl_path):
    sites = load_sites_config(folder)
    if not sites:
        return

    for site in sites:
        full_dir = os.path.abspath(os.path.join(folder, site["directory"]))
        Path(full_dir).mkdir(parents=True, exist_ok=True)
        site_url = site["url"]
        is_fa = 'furaffinity.net' in site_url.lower()

        command = [
            gdl_path,
            "--config-ignore",
            "--config", "gdlconf.conf",
            "-D", full_dir,
            "--no-colors",
            site_url
        ]

        print(f"\nDownloading: {site_url}")

        try:
            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
        except Exception as e:
            error(f"Error starting download: {e}")
            continue

        skip_requested = False
        fa_skip_count = 0
        fa_new_count = 0
        fa_last_new = 0
        fa_howmanybeforefuckingoffandmovingontothenextdownload = 20

        def output_reader(proc, is_fa_site):
            nonlocal fa_skip_count, fa_new_count
            for line in iter(proc.stdout.readline, ''):
                line = line.rstrip()
                print(line)
                if '[error]' in line:
                    parts = line.split('[error]', 1)
                    message = parts[1].strip() if len(parts) > 1 else line.strip()
                    error(f"{site_url} | {message}", False)

                # FA skip detection
                if is_fa_site:
                    if line.startswith('# '):
                        fa_skip_count += 1
                    else:
                        # Reset skip counter when we find a new file
                        fa_skip_count = 0
                        fa_new_count += 1
                        fa_last_new = fa_skip_count + fa_new_count

                    print(f"fa_skip_count: {fa_skip_count} fa_new_count: {fa_new_count} fa_howmany..download: {fa_howmanybeforefuckingoffandmovingontothenextdownload}")

                    # Only skip if we hit the threshold with no new files in between
                    if fa_skip_count >= fa_howmanybeforefuckingoffandmovingontothenextdownload:
                        print(f"Auto-skipping FA: {fa_skip_count} existing files in a row, 0 new downloads")
                        skip_requested = True
                        proc.terminate()
                        break

        thread = threading.Thread(target=output_reader, args=(proc, is_fa))
        thread.daemon = True
        thread.start()

        while proc.poll() is None:
            rlist, _, _ = select.select([sys.stdin], [], [], 0)
            if rlist:
                user_input = sys.stdin.readline().strip().upper()
                if user_input == 'S':
                    skip_requested = True
                    proc.terminate()
                    break
            time.sleep(0.1)

        thread.join()
        proc.wait()

        if skip_requested:
            print(f"Skipped {site_url}")
        elif proc.returncode != 0:
            error(f"Download failed for {site_url} with exit code {proc.returncode}")

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
