import os
import json
from datetime import datetime

def recover_market_checkpoint():
    """One-time script to recover market checkpoint from existing files."""
    data_dir = "historical_data"
    markets_dir = os.path.join(data_dir, "markets")
    
    if not os.path.exists(markets_dir):
        print("No markets directory found!")
        return
        
    # Collect all processed event tickers
    processed_events = set()
    total_markets = 0
    
    print("Scanning market files...")
    for filename in os.listdir(markets_dir):
        if filename.startswith("markets_") and filename.endswith(".json"):
            try:
                # Extract event ticker from filename (format: markets_EVENTTICKER_DATE.json)
                parts = filename.split('_')
                if len(parts) >= 2:
                    event_ticker = '_'.join(parts[1:-1])  # Join all parts between 'markets' and date
                    processed_events.add(event_ticker)
                    
                    # Count markets in file
                    filepath = os.path.join(markets_dir, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        total_markets += data.get('total_markets', 0)
                        
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    # Save recovered checkpoint
    checkpoint_file = os.path.join(data_dir, "checkpoint_markets.json")
    timestamp = datetime.now().isoformat()
    
    checkpoint_data = {
        'processed_events': list(processed_events),
        'last_timestamp': timestamp,
        'total_processed': len(processed_events),
        'total_markets': total_markets,
        'recovery_date': timestamp
    }
    
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint_data, f, indent=2)
        
    print(f"\nCheckpoint Recovery Complete:")
    print(f"Found {len(processed_events)} processed events")
    print(f"Total markets: {total_markets}")
    print(f"Saved to: {checkpoint_file}")
    
    # Print first few events as sample
    print("\nSample of recovered event tickers:")
    for ticker in list(processed_events)[:5]:
        print(f"- {ticker}")

if __name__ == "__main__":
    recover_market_checkpoint()
