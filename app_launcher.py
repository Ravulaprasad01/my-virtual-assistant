import subprocess
import os
import sys
import re

# Mapping of friendly names and aliases to commands/paths
APP_COMMANDS = {
    'notepad': 'notepad',
    'calculator': 'calc',
    'calc': 'calc',
    'chrome': 'chrome',
    'google chrome': 'chrome',
    'excel': 'excel',
    'microsoft excel': 'excel',
    'powerpoint': 'powerpnt',
    'power point': 'powerpnt',
    'microsoft powerpoint': 'powerpnt',
    'word': 'winword',
    'microsoft word': 'winword',
    'microsoft store': 'start ms-windows-store:',
    'store': 'start ms-windows-store:',
    'edge': 'msedge',
    'microsoft edge': 'msedge',
    'paint': 'mspaint',
    'explorer': 'explorer',
    'cmd': 'cmd',
    'terminal': 'wt',
    'settings': 'start ms-settings:',
}

# Keywords to ignore in user input
IGNORE_WORDS = {'open', 'launch', 'start', 'run', 'the', 'app', 'application', 'program', 'please'}

def parse_app_name(user_input):
    # Lowercase and remove punctuation
    cleaned = re.sub(r'[^a-zA-Z0-9 ]', '', user_input.lower())
    # Remove ignored words
    words = [w for w in cleaned.split() if w not in IGNORE_WORDS]
    app_name = ' '.join(words)
    return app_name

def open_app(user_input):
    app_name = parse_app_name(user_input)
    if app_name in APP_COMMANDS:
        command = APP_COMMANDS[app_name]
        # For 'start' commands, use shell=True
        if command.startswith('start '):
            subprocess.Popen(command, shell=True)
        else:
            try:
                subprocess.Popen(command)
            except FileNotFoundError:
                print(f"Could not find application: {app_name}")
    else:
        # Try to open as a direct path
        if os.path.exists(app_name):
            os.startfile(app_name)
        else:
            print(f"Unknown application: {app_name}\nYou can enter the full path to an executable if you want.")

def main():
    print("Type a command like 'open excel', 'launch powerpoint', 'start microsoft store', etc. Type 'exit' to quit.")
    while True:
        user_input = input("Which website or app do you want to open? ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            sys.exit(0)
        open_app(user_input)

if __name__ == '__main__':
    main() 