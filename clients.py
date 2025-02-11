import requests
import base64
import time
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import json

from requests.exceptions import HTTPError

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature

import websockets

class Environment(Enum):
    DEMO = "demo"
    PROD = "prod"

class KalshiBaseClient:
    """Base client class for interacting with the Kalshi API."""
    def __init__(
        self,
        key_id: str,
        private_key: rsa.RSAPrivateKey,
        environment: Environment = Environment.DEMO,
    ):
        self.key_id = key_id
        self.private_key = private_key
        self.environment = environment
        self.last_api_call = datetime.now()

        if self.environment == Environment.DEMO:
            self.HTTP_BASE_URL = "https://demo-api.kalshi.co"
            self.WS_BASE_URL = "wss://demo-api.kalshi.co"
        elif self.environment == Environment.PROD:
            self.HTTP_BASE_URL = "https://api.kalshi.com"
            self.WS_BASE_URL = "wss://api.kalshi.com"
        else:
            raise ValueError("Invalid environment")

    def request_headers(self, method: str, path: str) -> Dict[str, Any]:
        """Generates the required authentication headers for API requests."""
        timestamp = datetime.now().timestamp()
        current_time_milliseconds = int(timestamp * 1000)
        timestamp_str = str(current_time_milliseconds)

        # Create message string exactly as documented
        msg_string = timestamp_str + method + path
        signature = self.sign_pss_text(msg_string)

        return {
            'Content-Type': 'application/json',
            'KALSHI-ACCESS-KEY': self.key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp_str
        }

    def sign_pss_text(self, text: str) -> str:
        """Signs the text using RSA-PSS and returns the base64 encoded signature."""
        message = text.encode('utf-8')
        try:
            signature = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
        except InvalidSignature as e:
            raise ValueError("RSA sign PSS failed") from e

class KalshiHttpClient(KalshiBaseClient):
    def __init__(self, key_id: str, private_key: rsa.RSAPrivateKey, environment: Environment = Environment.DEMO):
        super().__init__(key_id, private_key, environment)
        self.host = self.HTTP_BASE_URL
        # Simplified API endpoints
        self.exchange_url = "/trade-api/v2/exchange"
        self.markets_url = "/trade-api/v2/markets"
        self.portfolio_url = "/trade-api/v2/portfolio"

    def rate_limit(self) -> None:
        """Built-in rate limiter to prevent exceeding API rate limits."""
        THRESHOLD_IN_MILLISECONDS = 100
        now = datetime.now()
        threshold_in_microseconds = 1000 * THRESHOLD_IN_MILLISECONDS
        threshold_in_seconds = THRESHOLD_IN_MILLISECONDS / 1000
        if now - self.last_api_call < timedelta(microseconds=threshold_in_microseconds):
            time.sleep(threshold_in_seconds)
        self.last_api_call = datetime.now()

    def raise_if_bad_response(self, response: requests.Response) -> None:
        """Raises an HTTPError if the response status code indicates an error."""
        if response.status_code not in range(200, 299):
            response.raise_for_status()

    def post(self, path: str, body: dict) -> Any:
        """Performs an authenticated POST request to the Kalshi API."""
        self.rate_limit()
        full_url = self.host + path
        print(f"Making POST request to: {full_url}")  # Debug print
        
        response = requests.post(
            full_url,
            json=body,
            headers=self.request_headers("POST", path)
        )
        if response.status_code == 404:
            print(f"404 Error Details: {response.text}")
        response.raise_for_status()
        return response.json()

    def get(self, path: str, params: Dict[str, Any] = {}) -> Any:
        """Performs an authenticated GET request to the Kalshi API."""
        self.rate_limit()
        full_url = self.host + path
        print(f"Making GET request to: {full_url}")  # Debug print
        response = requests.get(
            full_url,
            headers=self.request_headers("GET", path),
            params=params
        )
        if response.status_code == 404:
            print(f"404 Error Details: {response.text}")  # Debug print
        self.raise_if_bad_response(response)
        return response.json()

    def delete(self, path: str, params: Dict[str, Any] = {}) -> Any:
        """Performs an authenticated DELETE request to the Kalshi API."""
        self.rate_limit()
        response = requests.delete(
            self.host + path,
            headers=self.request_headers("DELETE", path),
            params=params
        )
        self.raise_if_bad_response(response)
        return response.json()

    def get_markets(self) -> Dict[str, Any]:
        """Gets list of available markets."""
        return self.get(self.markets_url)

    def get_market_by_ticker(self, ticker: str) -> Dict[str, Any]:
        """Gets specific market details."""
        return self.get(f"{self.markets_url}/{ticker}")

    def get_balance(self) -> Dict[str, Any]:
        """Gets current account balance."""
        return self.get(f"{self.portfolio_url}/balance")

    def get_exchange_status(self) -> Dict[str, Any]:
        """Gets exchange status."""
        return self.get(f"{self.exchange_url}/status")

    def create_order(self, ticker: str, side: str, count: int, price: int) -> Dict[str, Any]:
        """Place a new order."""
        body = {
            "ticker": ticker,
            "side": side,          # "buy" or "sell"
            "count": count,        # number of contracts
            "price": price,        # price in cents
            "type": "limit"        # order type
        }
        return self.post(f"{self.markets_url}/orders", body)

    def get_market_orderbook(self, ticker: str) -> Dict[str, Any]:
        """Get orderbook for a specific market."""
        return self.get(f"{self.markets_url}/{ticker}/orderbook")

    def get_market_history(self, ticker: str) -> Dict[str, Any]:
        """Get price history for a market."""
        return self.get(f"{self.markets_url}/{ticker}/history")

class KalshiWebSocketClient(KalshiBaseClient):
    """Client for handling WebSocket connections to the Kalshi API."""
    def __init__(
        self,
        key_id: str,
        private_key: rsa.RSAPrivateKey,
        environment: Environment = Environment.DEMO,
    ):
        super().__init__(key_id, private_key, environment)
        self.ws = None
        self.url_suffix = "/trade-api/ws/v2"
        self.message_id = 1  # Add counter for message IDs

    async def connect(self):
        """Establishes a WebSocket connection using authentication."""
        host = self.WS_BASE_URL + self.url_suffix
        auth_headers = self.request_headers("GET", self.url_suffix)
        async with websockets.connect(host, additional_headers=auth_headers) as websocket:
            self.ws = websocket
            await self.on_open()
            await self.handler()

    async def on_open(self):
        """Callback when WebSocket connection is opened."""
        print("WebSocket connection opened.")
        await self.subscribe_to_tickers()

    async def subscribe_to_tickers(self):
        """Subscribe to ticker updates for all markets."""
        subscription_message = {
            "id": self.message_id,
            "cmd": "subscribe",
            "params": {
                "channels": ["ticker"]
            }
        }
        await self.ws.send(json.dumps(subscription_message))
        self.message_id += 1

    async def handler(self):
        """Handle incoming messages."""
        try:
            async for message in self.ws:
                await self.on_message(message)
        except websockets.ConnectionClosed as e:
            await self.on_close(e.code, e.reason)
        except Exception as e:
            await self.on_error(e)

    async def on_message(self, message):
        """Callback for handling incoming messages."""
        print("Received message:", message)

    async def on_error(self, error):
        """Callback for handling errors."""
        print("WebSocket error:", error)

    async def on_close(self, close_status_code, close_msg):
        """Callback when WebSocket connection is closed."""
        print("WebSocket connection closed with code:", close_status_code, "and message:", close_msg)