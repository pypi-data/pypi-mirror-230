from datetime import datetime
import json
import os
import sys
from pathlib import Path
from colorama import Fore, Style
from dotenv import load_dotenv

# Defining the exclusive directory for dot files
DOTFILES_DIR = Path.home() / ".dev-assistant-client"
DOTFILES_DIR.mkdir(mode=777, parents=True, exist_ok=True)

load_dotenv()

APP_URL = os.getenv("APP_URL", "https://devassistant.tonet.dev")
API_PATH = os.getenv("API_PATH", "api")

TOKEN_FILE = DOTFILES_DIR / "token"
USER_DATA_FILE = DOTFILES_DIR / "user"
ABLY_TOKEN_FILE = DOTFILES_DIR / "ably_token"
DEVICE_ID_FILE = DOTFILES_DIR / "device_id"

# if is set in the env file, use it, otherwise use none
CERT_FILE = os.getenv("CERT_FILE", "")
KEY_FILE = os.getenv("KEY_FILE", "")

def dd(*args):
    """
    Just like the 'dump and die' function from Laravel
    """
    for arg in args:
        print(arg)
    sys.exit(1)

def get_device_id():
    try:
        return DEVICE_ID_FILE.read_text()
    except FileNotFoundError:
        return None


DEVICE_ID = get_device_id()
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "DevAssistant/0.2",
}


def flatten_dict(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def print_json(request):
    print(json.dumps(request, indent=4))


def now():
    # return just the date and time in a string format
    now = datetime.now()
    # return Fore.WHITE + now.strftime("%d/%m/%Y %H:%M:%S") + Style.RESET_ALL
    return Fore.WHITE + ">" + Style.RESET_ALL

def read_token():
    try:
        return TOKEN_FILE.read_text()
    except FileNotFoundError:
        return None

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def delete_token():
    TOKEN_FILE.unlink()