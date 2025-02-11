import json
from datetime import datetime
from clients import KalshiHttpClient, Environment
from cryptography.hazmat.primitives import serialization

class MarketAnalyzer:
    def __init__(self, client: KalshiHttpClient):
        self.client = client
        self.markets = []

    def fetch_markets(self):
        """Fetch all available markets and store them."""
        response = self.client.get_markets()
        self.markets = response.get('markets', [])
        return len(self.markets)

    def save_markets_to_file(self, filename: str = "markets.json"):
        """Save markets data to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.markets, f, indent=2)
        print(f"Saved {len(self.markets)} markets to {filename}")

    def get_markets_by_category(self):
        """Group markets by their category."""
        categories = {}
        for market in self.markets:
            category = market.get('category', 'Unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(market)
        return categories

    def print_market_summary(self):
        """Print a summary of available markets."""
        categories = self.get_markets_by_category()
        print("\nMarket Summary:")
        print("=" * 50)
        for category, markets in categories.items():
            print(f"\n{category}: {len(markets)} markets")
            # Print first 3 markets in each category
            for market in markets[:3]:
                print(f"  - {market['ticker']}: {market['title']}")

if __name__ == "__main__":
    # Load private key
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    # Initialize client
    client = KalshiHttpClient(
        key_id="05b95ed4-a236-41a1-9e3b-81124f6871dd",
        private_key=private_key,
        environment=Environment.DEMO
    )

    # Create analyzer
    analyzer = MarketAnalyzer(client)
    
    try:
        # Fetch and analyze markets
        num_markets = analyzer.fetch_markets()
        print(f"\nFetched {num_markets} markets")
        
        # Save to file
        analyzer.save_markets_to_file()
        
        # Print summary
        analyzer.print_market_summary()

    except Exception as e:
        print("Error:", str(e))
