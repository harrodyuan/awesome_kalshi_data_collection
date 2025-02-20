import pandas as pd
import json
import os
from datetime import datetime
import sys

class MarketDetailsProcessor:
    def __init__(self):
        self.data_dir = "historical_data"
        self.ensure_directories()

    def ensure_directories(self):
        """Create necessary directory structure."""
        dirs = [
            self.data_dir,
            os.path.join(self.data_dir, "processed_markets"),
            os.path.join(self.data_dir, "processed_events"),
            os.path.join(self.data_dir, "open_markets_individual")
        ]
        for dir_path in dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def load_processed_events(self, date_str: str) -> pd.DataFrame:
        """Load processed events CSV file."""
        events_file = os.path.join(
            self.data_dir, 
            "processed_events", 
            f"processed_events_{date_str}.csv"
        )
        return pd.read_csv(events_file)

    def get_market_details(self, event_ticker: str, date_str: str) -> list:
        """Extract all market details from individual market JSON file."""
        try:
            # List all files in the directory
            market_dir = os.path.join(self.data_dir, "open_markets_individual")
            market_files = [f for f in os.listdir(market_dir) if f.startswith(f"open_markets_{event_ticker}_")]
            
            if not market_files:
                print(f"No market files found for {event_ticker}")
                return []
                
            # Use the most recent file
            market_file = os.path.join(market_dir, market_files[-1])
            
            with open(market_file, 'r') as f:
                market_data = json.load(f)

            market_details = []
            # Use all_markets instead of open_markets to get all market data
            for market in market_data.get('all_markets', []):
                detail = {
                    # File level information
                    'collection_timestamp': market_data.get('timestamp'),
                    'total_markets': market_data.get('total_markets'),
                    'total_open_markets': market_data.get('total_open_markets'),
                    
                    # Market specific information
                    'ticker': market.get('ticker'),
                    'event_ticker': market.get('event_ticker'),
                    'market_type': market.get('market_type'),
                    'title': market.get('title'),
                    'subtitle': market.get('subtitle'),
                    'yes_sub_title': market.get('yes_sub_title'),
                    'no_sub_title': market.get('no_sub_title'),
                    
                    # Timing information
                    'open_time': market.get('open_time'),
                    'close_time': market.get('close_time'),
                    'expected_expiration_time': market.get('expected_expiration_time'),
                    'expiration_time': market.get('expiration_time'),
                    'latest_expiration_time': market.get('latest_expiration_time'),
                    'settlement_timer_seconds': market.get('settlement_timer_seconds'),
                    
                    # Status and configuration
                    'status': market.get('status'),
                    'response_price_units': market.get('response_price_units'),
                    'notional_value': market.get('notional_value'),
                    'tick_size': market.get('tick_size'),
                    
                    # Current pricing
                    'yes_bid': market.get('yes_bid'),
                    'yes_ask': market.get('yes_ask'),
                    'no_bid': market.get('no_bid'),
                    'no_ask': market.get('no_ask'),
                    'last_price': market.get('last_price'),
                    
                    # Historical pricing
                    'previous_yes_bid': market.get('previous_yes_bid'),
                    'previous_yes_ask': market.get('previous_yes_ask'),
                    'previous_price': market.get('previous_price'),
                    
                    # Trading metrics
                    'volume': market.get('volume'),
                    'volume_24h': market.get('volume_24h'),
                    'liquidity': market.get('liquidity'),
                    'open_interest': market.get('open_interest'),
                    
                    # Additional attributes
                    'result': market.get('result'),
                    'can_close_early': market.get('can_close_early'),
                    'expiration_value': market.get('expiration_value'),
                    'category': market.get('category'),
                    'risk_limit_cents': market.get('risk_limit_cents'),
                    'rules_primary': market.get('rules_primary'),
                    'rules_secondary': market.get('rules_secondary')
                }
                market_details.append(detail)
            
            return market_details
        except Exception as e:
            print(f"Error processing market file for {event_ticker}: {e}")
            return []

    def process_markets(self, date_str: str) -> pd.DataFrame:
        """Process all markets and create expanded DataFrame."""
        events_df = self.load_processed_events(date_str)
        print(f"\nLoaded {len(events_df)} events to process")
        
        all_markets = []
        total_events = len(events_df)
        
        for idx, event in events_df.iterrows():
            try:
                event_ticker = event['event_ticker']
                if not event_ticker:
                    print(f"Warning: Missing event_ticker for row {idx}")
                    continue
                    
                print(f"Processing event {idx + 1}/{total_events}: {event_ticker}")
                markets = self.get_market_details(event_ticker, date_str)
                
                if markets:
                    for market in markets:
                        market.update({
                            'event_timestamp': event['timestamp'],
                            'event_total_open_events': event['total_open_events'],
                            'event_series_ticker': event['series_ticker'],
                            'event_ticker': event['event_ticker'],
                            'event_title': event['title'],
                            'event_sub_title': event['sub_title'],
                            'event_category': event['category'],
                            'event_collateral_return_type': event.get('collateral_return_type', ''),
                            'event_mutually_exclusive': event['mutually_exclusive'],
                            'event_strike_date': event['strike_date'],
                            'category': event['category']
                        })
                    
                    all_markets.extend(markets)
                    print(f"Added {len(markets)} markets for {event_ticker}")
                
            except Exception as e:
                print(f"Error processing event {idx}: {str(e)}")
                continue

        if not all_markets:
            print("Warning: No markets processed")
            return pd.DataFrame()
            
        markets_df = pd.DataFrame(all_markets)
        
        try:
            if not markets_df.empty:
                markets_df['bid_ask_spread'] = markets_df['yes_ask'] - markets_df['yes_bid']
                markets_df['mid_price'] = (markets_df['yes_bid'] + markets_df['yes_ask']) / 2
                markets_df['market_implied_probability'] = markets_df['mid_price'] / 100
                
                # Handle dates
                markets_df['expiration_time'] = pd.to_datetime(markets_df['expiration_time'])
                markets_df['collection_timestamp'] = pd.to_datetime(markets_df['collection_timestamp'])
                
                if markets_df['expiration_time'].dt.tz is not None:
                    markets_df['expiration_time'] = markets_df['expiration_time'].dt.tz_convert('UTC')
                if markets_df['collection_timestamp'].dt.tz is not None:
                    markets_df['collection_timestamp'] = markets_df['collection_timestamp'].dt.tz_convert('UTC')
                
                markets_df['expiration_time'] = markets_df['expiration_time'].dt.tz_localize(None)
                markets_df['collection_timestamp'] = markets_df['collection_timestamp'].dt.tz_localize(None)
                
                markets_df['days_to_expiration'] = (markets_df['expiration_time'] - 
                                                  markets_df['collection_timestamp']).dt.total_seconds() / (24*60*60)
                
                markets_df['markets_in_event'] = markets_df.groupby('event_ticker')['ticker'].transform('count')
                
                # Format timestamps
                for col in ['open_time', 'close_time', 'expiration_time']:
                    try:
                        markets_df[f'{col}_formatted'] = pd.to_datetime(
                            markets_df[col], 
                            format='ISO8601'
                        ).dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        markets_df[f'{col}_formatted'] = markets_df[col]

                markets_df['category'] = markets_df['category'].fillna('')
                
        except Exception as e:
            print(f"Error adding derived columns: {str(e)}")

        # Save processed markets
        output_file = os.path.join(self.data_dir, "processed_markets", f"processed_markets_{date_str}.csv")
        markets_df.to_csv(output_file, index=False)
        
        print(f"\nProcessed {len(markets_df)} markets from {len(events_df)} events")
        print(f"Saved to: {output_file}")
        
        return markets_df

def main():
    # Get date from command line argument or use current date
    if len(sys.argv) > 1:
        try:
            input_date = sys.argv[1]
            datetime.strptime(input_date, "%Y%m%d")
            date_str = input_date
        except ValueError:
            print("Invalid date format. Please use YYYYMMDD format.")
            return
    else:
        date_str = datetime.now().strftime("%Y%m%d")
    
    print(f"Processing market details for date: {date_str}")
    
    processor = MarketDetailsProcessor()
    df = processor.process_markets(date_str)
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Total markets processed: {len(df)}")
    if not df.empty:
        print("\nMarkets by category (from events):")
        category_counts = df['category'].value_counts()
        print(category_counts)
        print("\nMarkets by status:")
        print(df['status'].value_counts())
        print("\nAverage volume per market:", df['volume'].mean())

if __name__ == "__main__":
    main()
