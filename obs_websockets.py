from obswebsocket import obsws, requests
from dotenv import load_dotenv
import os
import time
import sys

load_dotenv('./secrets.env')

obsPort = os.getenv('OBS_PORT')
obsPassword = os.getenv('OBS_PASSWORD')

class OBSWebsocketsManager:
    ws = None
    
    def __init__(self):
        # Connect to websockets
        self.ws = obsws('localhost', obsPort, obsPassword)
        try:
            self.ws.connect()
        except:
            print("\nPANIC!!\nCOULD NOT CONNECT TO OBS!\nDouble check that you have OBS open and that your websockets server is enabled in OBS.")
            time.sleep(10)
            sys.exit()
        print("Connected to OBS Websockets!\n")

    def disconnect(self):
        self.ws.disconnect()

print("Connecting to OBS Websockets")
obswebsockets_manager = OBSWebsocketsManager()
