import requests
import os
import webbrowser
from dotenv import load_dotenv

load_dotenv('./secrets.env')
CLIENT_ID =  os.getenv('TWITCH_CLIENT_ID')

url = f"https://id.twitch.tv/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri=http://localhost&response_type=token&scope=channel:read:redemptions+channel:manage:redemptions"
webbrowser.open(url)