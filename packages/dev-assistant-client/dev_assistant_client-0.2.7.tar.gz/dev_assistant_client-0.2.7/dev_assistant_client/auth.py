from colorama import Fore, Style
from dev_assistant_client.config import api_client, getpass
from dev_assistant_client.utils import delete_token, save_token

class Auth:
    """
    The Auth class handles authentication operations, including logging in,
    logging out, and establishing a WebSocket connection with Ably.
    """
    
    def login(self):
        """
        Prompts the user for email and password, and attempts to log in.
        If successful, the received token is saved locally and returns True.
        If login fails, returns False.
        """
        
        email = input("Enter your email: ")
        password = getpass.getpass("Enter your password: ")
        data = {"email": email, "password": password}
     
        response = api_client.post("/api/login", data=data)
        
        if response.status_code in [200, 201, 202, 204]:
            token = response.json()["token"]
            save_token(token)
            return True
        else:
            print(Fore.LIGHTRED_EX + "Login failed. Please check your credentials and try again." + Style.RESET_ALL)
            return False
        
    def logout(self):
        """
        Logs out the user by deleting the locally stored token.
        """
        try:
            delete_token()
            print("Logged out successfully.")
        except FileNotFoundError:
            print("You aren't logged in.")
