import json
import time
import threading
from collections import deque
from dotenv import load_dotenv
import os
import requests
import websocket

class TwitchConnectorManager:
    """
    Manages Twitch EventSub WebSocket connection for channel point redemptions.
    
    Flow:
    1. Connect to WebSocket
    2. Receive welcome message with session_id
    3. Subscribe to channel point redemption events
    4. Handle incoming redemption notifications
    5. Process redemptions from queue
    """
    
    def __init__(self, client_id, access_token, broadcaster_id):
        """
        Initialize the Twitch connector.
        
        Args:
            client_id: Your Twitch application client ID
            access_token: OAuth token with channel:read:redemptions scope
            broadcaster_id: The Twitch user ID of the channel to monitor
        """
        self.client_id = client_id
        self.access_token = access_token
        self.broadcaster_id = broadcaster_id
        
        # API endpoints
        self.base_url = 'https://api.twitch.tv/helix'
        self.ws_url = 'wss://eventsub.wss.twitch.tv/ws'
        
        # WebSocket connection
        self.ws = None
        self.session_id = None
        self.connected = False
        
        # Redemption queue
        self.redemption_queue = deque()
        self.queue_lock = threading.Lock()
        
        # Start connection
        self._connect()
    
    def _connect(self):
        """Establish WebSocket connection."""
        print("Connecting to Twitch EventSub WebSocket...")
        
        # Create WebSocket with event handlers
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        # Run WebSocket in a separate thread
        ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        ws_thread.start()
        
        # Wait for connection
        timeout = 10
        start_time = time.time()
        while not self.connected and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if not self.connected:
            raise Exception("Failed to connect to Twitch EventSub within timeout")
    
    def _on_open(self, ws):
        """Called when WebSocket connection opens."""
        print("WebSocket connection opened, waiting for welcome message...")
    
    def _on_message(self, ws, message):
        """
        Handle incoming WebSocket messages.
        
        Message types:
        - session_welcome: Initial message with session_id
        - notification: Event notification (redemption)
        - session_keepalive: Heartbeat to keep connection alive
        - session_reconnect: Server requesting reconnection
        """
        data = json.loads(message)
        message_type = data['metadata']['message_type']
        
        if message_type == 'session_welcome':
            self._handle_welcome(data)
        elif message_type == 'notification':
            self._handle_notification(data)
        elif message_type == 'session_keepalive':
            # Just acknowledge we received it
            pass
        elif message_type == 'session_reconnect':
            print("Reconnection requested by Twitch")
            # In production, you'd handle reconnection here
        else:
            print(f"Unknown message type: {message_type}")
    
    def _handle_welcome(self, data):
        """
        Handle welcome message and create subscription.
        
        The welcome message contains the session_id needed to create subscriptions.
        """
        self.session_id = data['payload']['session']['id']
        print(f"✓ Connected! Session ID: {self.session_id}")
        self.connected = True
        
        # Now that we have session_id, create the subscription
        self._create_subscription()
    
    def _create_subscription(self):
        """
        Create EventSub subscription for channel point redemptions.
        
        This tells Twitch to send redemption events to our WebSocket session.
        """
        url = f"{self.base_url}/eventsub/subscriptions"
        
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Subscribe to channel point redemption events
        payload = {
            "type": "channel.channel_points_custom_reward_redemption.add",
            "version": "1",
            "condition": {
                "broadcaster_user_id": self.broadcaster_id
            },
            "transport": {
                "method": "websocket",
                "session_id": self.session_id
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 202:
            print("✓ Subscription created successfully!")
            print("  Now listening for channel point redemptions...")
        else:
            print(f"✗ Failed to create subscription: {response.status_code}")
            print(f"  Response: {response.text}")
    
    def _handle_notification(self, data):
        """
        Handle redemption notification.
        
        When a viewer redeems channel points, this receives the event.
        """
        event = data['payload']['event']
        
        # Extract redemption info
        redemption_info = {
            'id': event['id'],
            'user_name': event['user_name'],
            'user_input': event.get('user_input', ''),
            'reward_title': event['reward']['title'],
            'reward_cost': event['reward']['cost'],
            'redeemed_at': event['redeemed_at'],
            'status': event['status']
        }
        
        print(f"\n🎁 New Redemption!")
        print(f"   User: {redemption_info['user_name']}")
        print(f"   Reward: {redemption_info['reward_title']} ({redemption_info['reward_cost']} points)")
        if redemption_info['user_input']:
            print(f"   Input: {redemption_info['user_input']}")
        
        # Add to processing queue
        with self.queue_lock:
            self.redemption_queue.append(redemption_info)
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors."""
        print(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket closure."""
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False
    
    def process_redemptions(self):
        """
        Process redemptions from the queue.
        
        This is where you'd implement your custom logic for each redemption.
        Call this method periodically or in a loop.
        """
        with self.queue_lock:
            if not self.redemption_queue:
                return None
            
            redemption = self.redemption_queue.popleft()
        
        # CUSTOM LOGIC HERE
        # Example: trigger different actions based on reward title
        print(f"\n⚙️  Processing: {redemption['reward_title']}")
        
        # You can update the redemption status here
        # self.update_redemption_status(redemption['id'], 'FULFILLED')
        
        return redemption
    
    def update_redemption_status(self, redemption_id, status):
        """
        Update redemption status to FULFILLED or CANCELED.
        
        Args:
            redemption_id: The ID of the redemption
            status: Either 'FULFILLED' or 'CANCELED'
        """
        url = f"{self.base_url}/channel_points/custom_rewards/redemptions"
        
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'id': redemption_id,
            'broadcaster_id': self.broadcaster_id,
            'reward_id': redemption_id,  # You'd need to track this
        }
        
        payload = {'status': status}
        
        response = requests.patch(url, headers=headers, params=params, json=payload)
        
        if response.status_code == 200:
            print(f"✓ Redemption marked as {status}")
        else:
            print(f"✗ Failed to update redemption: {response.text}")
    
    def get_queue_size(self):
        """Get the current number of pending redemptions."""
        with self.queue_lock:
            return len(self.redemption_queue)


# Example usage
if __name__ == "__main__":
    # Load environment variables
    load_dotenv('./secrets.env')
    
    # Get credentials from .env file
    CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
    ACCESS_TOKEN = os.getenv('TWITCH_ACCESS_TOKEN')
    BROADCASTER_ID = os.getenv('TWITCH_BROADCASTER_ID')
    
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
                # Your custom handling here
                print(f"✓ Processed redemption from {redemption['user_name']}")
            
            # Check every 100ms
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")