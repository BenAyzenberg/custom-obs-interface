from obs_websockets import OBSWebsocketsManager
from twitch_connector import TwitchConnectorManager
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Load environment variables
    
# Get credentials from .env file
CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
ACCESS_TOKEN = os.getenv('TWITCH_ACCESS_TOKEN')
BROADCASTER_ID = os.getenv('TWITCH_BROADCASTER_ID')
OBS_PORT = os.getenv('OBS_PORT')
OBS_PASSWORD = os.getenv('OBS_PASSWORD')

if not all([OBS_PORT, OBS_PASSWORD]):
    print("Error: Missing required environment variables")
    print("Please set OBS_PORT, OBS_PASSWORDin your secrets.env file")
    exit(1)

print("Connecting to OBS Websockets")
obs = OBSWebsocketsManager()
    
# Validate credentials
if not all([CLIENT_ID, ACCESS_TOKEN, BROADCASTER_ID]):
    print("Error: Missing required environment variables")
    print("Please set TWITCH_CLIENT_ID, TWITCH_ACCESS_TOKEN, and TWITCH_BROADCASTER_ID in your .env file")
    exit(1)
    
# Create connector
print("Connecting to Twitch EventSub...")
twitch = TwitchConnectorManager(CLIENT_ID, ACCESS_TOKEN, BROADCASTER_ID)
    
# Main loop - process redemptions as they come in
print("\n" + "="*50)
print("Listening for channel point redemptions...")
print("Press Ctrl+C to stop")
print("="*50 + "\n")
    
try:
    while True:
        # Process any redemptions in the queue
        redemption = twitch.process_redemptions()
            
        if redemption:
            print(f"✓ Processed redemption from {redemption['user_name']}")
            twitch.update_redemption_status(redemption['id'], 'FULFILLED')
            
        # Check every 60s
        time.sleep(60)
            
except KeyboardInterrupt:
    print("\n\nShutting down...")