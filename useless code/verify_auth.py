import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from clients import KalshiHttpClient, Environment

# Load environment variables
load_dotenv()

# Get credentials
KEYID = os.getenv('DEMO_KEYID')
KEYFILE = os.getenv('DEMO_KEYFILE')

print(f"Using Key ID: {KEYID}")
print(f"Using Key File: {KEYFILE}")

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

# Test authentication
try:
    status = client.get("/trade-api/v2/exchange/status")
    print("Authentication successful!")
    print("Exchange status:", status)
    
    markets = client.get("/trade-api/v2/markets")
    print("Markets access successful!")
    print("Number of markets:", len(markets.get('markets', [])))
except Exception as e:
    print("Authentication failed:", str(e))
    print("Full error details:", str(e.__dict__))
