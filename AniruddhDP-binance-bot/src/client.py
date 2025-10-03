# In src/client.py

import os
import logging
from dotenv import load_dotenv
from binance import Client
from binance.exceptions import BinanceAPIException

# Load environment variables from the .env file in the project's root directory
load_dotenv()

# Setup structured logging to a file named 'bot.log' in the root directory
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BinanceClient:
    def __init__(self):
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")

        if not self.api_key or not self.api_secret:
            error_msg = "API key and secret must be set in the .env file."
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        self.base_url = "https://testnet.binancefuture.com"
        self.client = None
        self._connect()

    def _connect(self):
        """Connects to the Binance Futures Testnet and verifies the connection."""
        try:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            self.client.API_URL = self.base_url
            self.client.get_account() # Test connection
            logging.info("Successfully connected to Binance Futures Testnet.")
            print("Successfully connected to Binance Futures Testnet.")
        except BinanceAPIException as e:
            logging.error(f"Error connecting to Binance: {e}")
            print(f"Error connecting to Binance: {e}")
            self.client = None