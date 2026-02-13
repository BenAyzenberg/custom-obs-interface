from time import sleep
import os
from dotenv import load_dotenv
import requests
from websocket import WebSocketTimeoutException
baseUrl = 'https://api.twitch.tv/helix'
redemptions = '/channel_points/custom_rewards/redemptions'

