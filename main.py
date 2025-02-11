import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from clients import KalshiHttpClient, Environment

# Load environment variables
load_dotenv()

# API credentials
KEYID = "05b95ed4-a236-41a1-9e3b-81124f6871dd"  # Your API key
KEYFILE = "private_key.pem"  # Path to your private key file

# Load private key
with open(KEYFILE, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

# Initialize client
client = KalshiHttpClient(
    key_id=KEYID,
    private_key=private_key,
    environment=Environment.DEMO
)

try:
    # Test basic API functionality
    print("\nChecking exchange status...")
    status = client.get_exchange_status()
    print("Exchange status:", status)

    print("\nGetting available markets...")
    markets = client.get_markets()
    print(f"Found {len(markets['markets'])} markets")
    
    # Show first 3 markets as example
    for market in markets['markets'][:3]:
        print(f"- {market['ticker']}: {market['title']}")

    # Get details for the first market
    if markets['markets']:
        ticker = markets['markets'][0]['ticker']
        print(f"\nGetting orderbook for {ticker}...")
        orderbook = client.get_market_orderbook(ticker)
        print("Best bid:", orderbook.get('bids', [{'price': 'No bids'}])[0]['price'])
        print("Best ask:", orderbook.get('asks', [{'price': 'No asks'}])[0]['price'])

        print(f"\nGetting price history for {ticker}...")
        history = client.get_market_history(ticker)
        print(f"Last price: {history.get('last_price', 'N/A')}")

except Exception as e:
    print("Error:", str(e))