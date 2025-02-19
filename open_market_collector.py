import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from auth_manager import AuthManager
from market_data import MarketDataManager

class OpenMarketCollector:
    def __init__(self, auth_manager: AuthManager):
        self.market_data = MarketDataManager(auth_manager)
        self.data_dir = "historical_data"
        self.ensure_directories()

    def ensure_directories(self):
        dirs = [
            self.data_dir,
            os.path.join(self.data_dir, "open_markets"),
            os.path.join(self.data_dir, "open_markets_individual")
        ]
        for dir_path in dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def load_checkpoint(self) -> set:
        checkpoint_file = os.path.join(self.data_dir, "checkpoint_open_markets.json")
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
                return set(data.get('processed_events', []))
        return set()

    def save_checkpoint(self, processed_events: set):
        checkpoint_file = os.path.join(self.data_dir, "checkpoint_open_markets.json")
        with open(checkpoint_file, 'w') as f:
            json.dump({
                'processed_events': list(processed_events),
                'last_update': datetime.now().isoformat(),
                'total_processed': len(processed_events)
            }, f, indent=2)

    def collect_open_markets(self) -> str:
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y%m%d')
        
        # Load checkpoint
        processed_events = self.load_checkpoint()
        
        # First load open events
        open_events_file = os.path.join(self.data_dir, "events", f"open_events_{date_str}.json")
        with open(open_events_file, 'r') as f:
            events_data = json.load(f)
            event_tickers = [event['event_ticker'] for event in events_data.get('events', [])]
        
        all_open_markets = []
        
        try:
            # Get markets for each open event
            for event_ticker in event_tickers:
                if event_ticker in processed_events:
                    print(f"Skipping already processed event: {event_ticker}")
                    continue

                try:
                    print(f"Fetching markets for event: {event_ticker}")
                    response = self.market_data.get_markets(event_ticker=event_ticker)
                    markets = response.get('markets', [])
                    open_markets = [m for m in markets if m['status'] == 'active']
                    
                    # Always save individual event markets, even if empty
                    individual_file = os.path.join(
                        self.data_dir,
                        "open_markets_individual",
                        f"open_markets_{event_ticker}_{date_str}.json"
                    )
                    with open(individual_file, 'w') as f:
                        json.dump({
                            'timestamp': timestamp.isoformat(),
                            'event_ticker': event_ticker,
                            'total_markets': len(markets),
                            'total_open_markets': len(open_markets),
                            'all_markets': markets,
                            'open_markets': open_markets
                        }, f, indent=2)
                    
                    if open_markets:
                        all_open_markets.extend(open_markets)
                        print(f"Found {len(open_markets)} open markets for {event_ticker}")
                    else:
                        print(f"No open markets found for {event_ticker}")
                    
                    processed_events.add(event_ticker)
                    self.save_checkpoint(processed_events)
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error fetching markets for {event_ticker}: {e}")
                    continue

        except KeyboardInterrupt:
            print("\nCollection interrupted. Saving progress...")
            
        finally:
            # Save combined results
            filename = os.path.join(self.data_dir, "open_markets", f"open_markets_{date_str}.json")
            with open(filename, 'w') as f:
                json.dump({
                    'timestamp': timestamp.isoformat(),
                    'total_events_processed': len(processed_events),
                    'total_open_markets': len(all_open_markets),
                    'markets': all_open_markets
                }, f, indent=2)
            
            self.save_checkpoint(processed_events)
            
            print(f"\nCollected {len(all_open_markets)} open markets")
            print(f"Processed {len(processed_events)} events")
            print(f"Individual market data saved to: {os.path.join(self.data_dir, 'open_markets_individual')}")
            return filename

if __name__ == "__main__":
    auth = AuthManager(key_id="05b95ed4-a236-41a1-9e3b-81124f6871dd", key_file_path="private_key.pem")
    collector = OpenMarketCollector(auth)
    open_markets_file = collector.collect_open_markets()
    print(f"\nOpen markets saved to: {open_markets_file}")