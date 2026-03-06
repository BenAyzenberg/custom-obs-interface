from obs_websockets import OBSWebsocketsManager
from twitch_connector import TwitchConnectorManager
from sound_manager import SoundManager
from dotenv import load_dotenv
import os
import time
import pygame

load_dotenv('./secrets.env')

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
obs = OBSWebsocketsManager(OBS_PORT, OBS_PASSWORD)
    
# Validate credentials
if not all([CLIENT_ID, ACCESS_TOKEN, BROADCASTER_ID]):
    print("Error: Missing required environment variables")
    print("Please set TWITCH_CLIENT_ID, TWITCH_ACCESS_TOKEN, and TWITCH_BROADCASTER_ID in your .env file")
    exit(1)
    
# Create connector
print("Connecting to Twitch EventSub...")
twitch = TwitchConnectorManager(CLIENT_ID, ACCESS_TOKEN, BROADCASTER_ID)
noise = SoundManager()
    
# Main loop - process redemptions as they come in
print("\n" + "="*50)
print("Listening for channel point redemptions...")
print("Press Ctrl+C to stop")
print("="*50 + "\n")
    
try:
    
    while True:
        # Process any redemptions in the queue
        redemption = twitch.process_redemptions()
        currentScene = obs.get_active_scene()
            
        if redemption:
            completeStatus = False
            
            if redemption['title'] == 'Hydrate':
                obs.set_text('RewardText', 'Hydrate')
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', True)
                noise.play('Hydrate')
                time.sleep(10)
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', False)
                completeStatus = True

            elif redemption['title'] == 'Stretch':
                obs.set_text('RewardText', 'Stretch')
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', True)
                noise.play('Stretch')
                time.sleep(10)
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', False)
                completeStatus = True

            elif redemption['title'] == 'PostureCheck':
                obs.set_text('RewardText', 'Posture Check')
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', True)
                noise.play('Posture')
                time.sleep(10)
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', False)
                completeStatus = True

            elif redemption['title'] == 'Pushups':
                obs.set_text('RewardText', 'Pushups')
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', True)
                noise.play('Pushups')
                time.sleep(10)
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', False)
                completeStatus = True


        if completeStatus:
            #print('Test Success')
            print(f"✓ Processed redemption from {redemption['user_name']}")
            twitch.update_redemption_status(redemption['id'], 'FULFILLED')
        else:
            print(f"Redemption {redemption['title']} from {redemption['user_name']} could not be completed")
            print("Either the redemtion requires manual action or something failed\nStatus not updated")
            
        # Check every 60s
        time.sleep(60)
            
except KeyboardInterrupt:
    print("\n\nShutting down...")