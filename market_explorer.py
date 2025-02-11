from auth_manager import AuthManager
from market_data import MarketDataManager
import json
from datetime import datetime
from typing import Dict, Any
import pandas as pd
from tabulate import tabulate

class MarketExplorer:
    def __init__(self):
        self.auth = AuthManager(
            key_id="05b95ed4-a236-41a1-9e3b-81124f6871dd",
            key_file_path="private_key.pem"
        )
        self.market_data = MarketDataManager(self.auth)
        self.current_event = None
        self.current_market = None
        self.all_events = []
        self.all_markets = []

    def fetch_all_events(self):
        """Fetch all events using pagination."""
        all_events = []
        cursor = None
        total_pages = 0
        
        try:
            while True:
                # Get response
                response = self.market_data.get_events(cursor=cursor)
                
                # Extract events and cursor from response
                events = response.get('events', [])
                cursor = response.get('cursor')  # Get cursor for next page
                
                # Add events to our list
                all_events.extend(events)
                total_pages += 1
                print(f"Fetched page {total_pages}, total events: {len(all_events)}")
                
                # If no cursor or no events, we're done
                if not cursor or not events:
                    break
                
        except Exception as e:
            print(f"Error fetching events: {e}")
        
        self.all_events = all_events
        print(f"\nCompleted fetching {len(all_events)} events from {total_pages} pages")
        return all_events

    def show_events(self):
        """Display all available events."""
        if not self.all_events:
            print("Fetching all events...")
            self.fetch_all_events()
            
        print(f"\nAvailable Events ({len(self.all_events)} total):")
        print("=" * 80)
        
        # Show events in pages of 20
        page_size = 20
        page = 0
        while True:
            start_idx = page * page_size
            end_idx = start_idx + page_size
            current_events = self.all_events[start_idx:end_idx]
            
            if not current_events:
                break
                
            for i, event in enumerate(current_events, start=start_idx+1):
                print(f"{i}. {event['title']} ({event['event_ticker']})")
            
            print("\nCommands: [n]ext page, [p]revious page, [s]elect event number, [q]uit")
            cmd = input("Enter command: ").lower()
            
            if cmd == 'n':
                page += 1
            elif cmd == 'p':
                page = max(0, page - 1)
            elif cmd == 'q':
                return None
            elif cmd == 's':
                while True:
                    try:
                        choice = int(input("\nSelect event number (1-{len(self.all_events)}): ")) - 1
                        if 0 <= choice < len(self.all_events):
                            self.current_event = self.all_events[choice]
                            return self.current_event
                        else:
                            print("Invalid event number!")
                    except ValueError:
                        print("Please enter a valid number!")
                    except Exception as e:
                        print(f"Error: {e}")

    def show_markets_for_event(self):
        """Display markets for current event."""
        if not self.current_event:
            print("No event selected! Please select an event first.")
            return

        try:
            markets = self.market_data.get_markets(self.current_event['event_ticker'])['markets']
            self.all_markets = markets
            
            print(f"\nMarkets for {self.current_event['title']}:")
            print("=" * 80)
            
            # Show markets in pages of 10
            page_size = 10
            page = 0
            while True:
                start_idx = page * page_size
                end_idx = start_idx + page_size
                current_markets = markets[start_idx:end_idx]
                
                if not current_markets:
                    break
                    
                for i, market in enumerate(current_markets, start=start_idx+1):
                    print(f"{i}. {market['title']}")
                    print(f"   Ticker: {market['ticker']}")
                    print(f"   Yes Bid/Ask: {market.get('yes_bid', 'N/A')}/{market.get('yes_ask', 'N/A')}")
                    print(f"   No Bid/Ask: {market.get('no_bid', 'N/A')}/{market.get('no_ask', 'N/A')}")
                    print(f"   Volume: {market.get('volume', 0)}")
                    print("-" * 40)
                
                print("\nCommands: [n]ext page, [p]revious page, [s]elect market number, [q]uit")
                cmd = input("Enter command: ").lower()
                
                if cmd == 'n':
                    page += 1
                elif cmd == 'p':
                    page = max(0, page - 1)
                elif cmd == 'q':
                    return None
                elif cmd == 's':
                    while True:
                        try:
                            choice = int(input(f"\nSelect market number (1-{len(markets)}): ")) - 1
                            if 0 <= choice < len(markets):
                                self.current_market = markets[choice]
                                return self.current_market
                            else:
                                print("Invalid market number!")
                        except ValueError:
                            print("Please enter a valid number!")
                        except Exception as e:
                            print(f"Error: {e}")
                            
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return None

    def show_market_details(self):
        """Display detailed information for current market."""
        if not self.current_market:
            print("No market selected!")
            return

        ticker = self.current_market['ticker']
        
        # Get orderbook
        orderbook = self.market_data.get_market_orderbook(ticker)
        
        print(f"\nMarket Details for {ticker}")
        print("=" * 80)
        print(f"Title: {self.current_market['title']}")
        print(f"Status: {self.current_market['status']}")
        print(f"Liquidity: ${self.current_market['liquidity']/100:.2f}")
        print(f"Volume: {self.current_market['volume']}")
        
        print("\nOrderbook:")
        print("-" * 40)
        print("Bids:")
        if orderbook.get('bids'):
            for bid in orderbook['bids'][:5]:  # Show top 5 bids
                print(f"Price: {bid['price']}, Size: {bid['size']}")
        
        print("\nAsks:")
        if orderbook.get('asks'):
            for ask in orderbook['asks'][:5]:  # Show top 5 asks
                print(f"Price: {ask['price']}, Size: {ask['size']}")

    def interactive_menu(self):
        """Interactive menu for exploring markets."""
        while True:
            print("\nKalshi Market Explorer")
            print("1. Show Events")
            print("2. Show Markets for Current Event")
            print("3. Show Current Market Details")
            print("4. Exit")
            
            choice = input("Select option (1-4): ")
            
            if choice == "1":
                self.show_events()
            elif choice == "2":
                self.show_markets_for_event()
            elif choice == "3":
                self.show_market_details()
            elif choice == "4":
                break
            else:
                print("Invalid choice!")

if __name__ == "__main__":
    explorer = MarketExplorer()
    explorer.interactive_menu()
