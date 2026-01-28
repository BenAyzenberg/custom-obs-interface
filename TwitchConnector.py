from time import sleep
import requests
baseUrl = 'https://api.twitch.tv/helix'
redemptions = '/channel_points/custom_rewards/redemptions'

queue = []

# run indefinitely
while(True):
    
    sleep(60)