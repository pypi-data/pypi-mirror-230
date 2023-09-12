import asyncio
import getpass
import json
import logging
import requests
from ably import AblyRealtime
from dev_assistant_client.api_client import APIClient
from dev_assistant_client.io import IOAssistant
from dev_assistant_client.utils import APP_URL, CERT_FILE, KEY_FILE, DEVICE_ID, dd, delete_token, read_token, save_token

api_client = APIClient(APP_URL, CERT_FILE, KEY_FILE)
