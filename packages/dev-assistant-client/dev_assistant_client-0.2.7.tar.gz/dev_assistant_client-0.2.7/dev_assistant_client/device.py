import os
import json
import logging
import getpass
import platform
import socket
import uuid
import re
from colorama import Fore, Style
from dev_assistant_client.api_client import APIClient
from dev_assistant_client.ably_handler import AblyHandler
from dev_assistant_client.auth import Auth
from dev_assistant_client.utils import (
    CERT_FILE,
    DEVICE_ID_FILE,
    KEY_FILE,
    TOKEN_FILE,
    APP_URL,
    API_PATH,
    DEVICE_ID,
    dd,
    now,
    read_token,
    
)

def create_device_payload():
    """
    The function `create_device_payload` returns a dictionary containing information about the device,
    such as its ID, name, type, IP address, MAC address, operating system, architecture, Python version,
    and username.
    :return: a dictionary containing information about a device.
    """
    return {
        "id": DEVICE_ID or "",
        "name": socket.gethostname(),
        "type": "desktop",
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "mac_address": ":".join(re.findall("..", "%012x" % uuid.getnode())),
        "os": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "username": getpass.getuser(),
    }

api_client = APIClient(f"{APP_URL}/{API_PATH}", CERT_FILE, KEY_FILE)

async def connect_device():
    """
    Tries to connect the device to the server. It starts by reading a token, creates
    a device payload and makes a POST call to the server. If the call is successful,
    the device is connected and the device ID is saved locally. Then, it tries to establish
    a WebSocket connection using the ably_connect() function from auth.py.
    """
    token = read_token()
    
    payload = create_device_payload()
    print(now(), "Device ID: \t", Fore.LIGHTYELLOW_EX + DEVICE_ID + Style.RESET_ALL, sep="\t")
    print(now(), "Connecting device...", sep="\t", end="\t")

    api_client.headers["Authorization"] = "Bearer " + token
    
    response = api_client.post("/devices", data=payload)
    
    if response.status_code in [200, 201]:
        print(Fore.LIGHTGREEN_EX + "Connected" + Style.RESET_ALL, sep="\t")
        with open(DEVICE_ID_FILE, "w") as f:
            f.write(json.loads(response.content).get("id"))
        if json.loads(response.content).get("id") != DEVICE_ID:
            print(now(), Fore.LIGHTYELLOW_EX + "Warning: " + Style.RESET_ALL, "Device ID has changed. Please update where it is needed.")
            print(now(), "New device ID: ", Fore.LIGHTYELLOW_EX + json.loads(response.content).get("id") + Style.RESET_ALL, sep="\t")
        await AblyHandler().ably_connect()
    else:
        print(Fore.LIGHTRED_EX + "Failed to connect!" + Style.RESET_ALL, sep="\t")
        if response.status_code == 401:
            print( Fore.LIGHTRED_EX + "Error: " + Style.RESET_ALL, json.loads(response.content).get('error'), sep="\t")
            print( Fore.LIGHTRED_EX + "Please do login again." + Style.RESET_ALL, sep="\t")
            os.remove(TOKEN_FILE)
        else:
            print(now(), "Status code: ", response.status_code, sep="\t")
            print(now(), "Response: ", response.content, sep="\t")