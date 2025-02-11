from auth_manager import AuthManager
from market_data import MarketDataManager
import json
from datetime import datetime

def main():
    # Initialize managers
    auth = AuthManager(
        key_id="05b95ed4-a236-41a1-9e3b-81124f6871dd",
        key_file_path="private_key.pem"
    )
    market_data = MarketDataManager(auth)

    try:
        # 1. Get available events
        print("\nFetching events...")
        events_response = market_data.get_events()
        events = events_response.get('events', [])
        print(f"Found {len(events)} events")

        # Debug print first event structure
        if events:
            print("\nFirst event structure:")
            first_event = events[0]
            for key, value in first_event.items():
                print(f"{key}: {value}")

            # 2. Get markets using event_ticker
            event_ticker = first_event.get('event_ticker')
            if event_ticker:
                print(f"\nFetching markets for event ticker: {event_ticker}")
                markets = market_data.get_markets(event_ticker)
                
                if markets.get('markets'):
                    print(f"Found {len(markets['markets'])} markets")
                    
                    # 3. Get orderbook for first market
                    market = markets['markets'][0]
                    ticker = market.get('ticker')
                    if ticker:
                        print(f"\nFetching orderbook for market: {ticker}")
                        orderbook = market_data.get_market_orderbook(ticker)
                        
                        # Save data
                        data = {
                            'timestamp': datetime.now().isoformat(),
                            'event': first_event,
                            'market': market,
                            'orderbook': orderbook
                        }
                        
                        with open('market_data.json', 'w') as f:
                            json.dump(data, f, indent=2)
                        print("\nMarket data saved to market_data.json")
            else:
                print("No event_ticker found in event data")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
