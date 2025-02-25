import requests
from typing import Dict, List, Optional
from auth_manager import AuthManager

class MarketDataManager:
    # def __init__(self, auth_manager: AuthManager, base_url: str = "https://trading-api.kalshi.com"):
    # def __init__(self, auth_manager: AuthManager, base_url: str = "https://api.kalshi.com"):
    # def __init__(self, auth_manager: AuthManager, base_url: str = "https://demo-api.kalshi.co"):
    def __init__(self, auth_manager: AuthManager, base_url: str = "https://api.elections.kalshi.com"):
        self.auth = auth_manager
        self.base_url = base_url

    def get_events(self, cursor: Optional[str] = None, limit: int = 100, status: Optional[str] = None) -> Dict:
        """Get available events with pagination support."""
        path = "/trade-api/v2/events"
        headers = self.auth.generate_headers("GET", path)
        
        # Simple params - just limit, cursor, and status
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if status:
            params["status"] = status
        
        print(f"Making request to: {self.base_url}{path}")
        response = requests.get(f"{self.base_url}{path}", headers=headers, params=params)
        
        if response.status_code == 404:
            print(f"404 Error Details: {response.text}")
        response.raise_for_status()
        
        return response.json()  # Return raw response which includes events and cursor

    def get_markets(self, event_ticker: Optional[str] = None) -> Dict:
        """Get markets for an event."""
        path = "/trade-api/v2/markets"
        params = {}
        if event_ticker:
            params['event_ticker'] = event_ticker
            
        headers = self.auth.generate_headers("GET", path)
        print(f"Making request to: {self.base_url}{path} with params: {params}")
        
        response = requests.get(f"{self.base_url}{path}", headers=headers, params=params)
        if response.status_code == 404:
            print(f"404 Error Details: {response.text}")
        response.raise_for_status()
        return response.json()

    def get_market_orderbook(self, ticker: str, depth: int = 5) -> Dict:
        """Get orderbook for a specific market with specified depth."""
        path = f"/trade-api/v2/markets/{ticker}/orderbook"
        headers = self.auth.generate_headers("GET", path)
        
        params = {"depth": depth}  # Add depth parameter to show top N levels
        
        print(f"Requesting orderbook from: {self.base_url}{path}")
        response = requests.get(f"{self.base_url}{path}", 
                              headers=headers,
                              params=params)
        
        if response.status_code == 404:
            print(f"404 Error Details: {response.text}")
        else:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
        response.raise_for_status()
        return response.json()
