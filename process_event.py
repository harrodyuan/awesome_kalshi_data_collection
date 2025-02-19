import json
import os
import pandas as pd
from datetime import datetime
import sys

class EventProcessor:
    def __init__(self, json_file_path):
        self.data_dir = "historical_data"
        self.json_file_path = os.path.join(self.data_dir, "events", json_file_path)
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directory structure."""
        output_dir = os.path.join(self.data_dir, "processed")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
    def load_json_data(self):
        """Load JSON data from file"""
        try:
            with open(self.json_file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Error loading JSON file: {str(e)}")

    def process_events(self):
        """Process events data and convert to DataFrame"""
        data = self.load_json_data()
        events_data = []

        for event in data.get('events', []):
            event_info = {
                'timestamp': data.get('timestamp'),
                'total_open_events': data.get('total_open_events'),
                'event_ticker': event.get('event_ticker'),
                'series_ticker': event.get('series_ticker'),
                'sub_title': event.get('sub_title'),
                'title': event.get('title'),
                'collateral_return_type': event.get('collateral_return_type'),
                'mutually_exclusive': event.get('mutually_exclusive'),
                'category': event.get('category'),
                'strike_date': event.get('strike_date', '')
            }
            events_data.append(event_info)
            
        return pd.DataFrame(events_data)

    def save_to_csv(self, output_path):
        """Save processed data to CSV"""
        try:
            df = self.process_events()
            full_output_path = os.path.join(self.data_dir, "processed", output_path)
            df.to_csv(full_output_path, index=False)
            print(f"Successfully saved {len(df)} events to {full_output_path}")
            return df
        except Exception as e:
            raise Exception(f"Error saving to CSV: {str(e)}")

def main():
    # Get date from command line argument or use current date
    if len(sys.argv) > 1:
        try:
            # Validate the date format
            input_date = sys.argv[1]
            datetime.strptime(input_date, "%Y%m%d")
            date_str = input_date
        except ValueError:
            print("Invalid date format. Please use YYYYMMDD format.")
            return
    else:
        date_str = datetime.now().strftime("%Y%m%d")
    
    # File paths
    input_path = f"open_events_{date_str}.json"
    output_path = f"processed_events_{date_str}.csv"
    
    print(f"Processing data for date: {date_str}")
    
    # Process events
    processor = EventProcessor(input_path)
    
    try:
        df = processor.save_to_csv(output_path)
        
        # Print summary statistics
        print("\nSummary Statistics:")
        print(f"Total events: {len(df)}")
        print("\nEvents by category:")
        print(df['category'].value_counts())
        print("\nMutually exclusive events:")
        print(df['mutually_exclusive'].value_counts())
        
    except Exception as e:
        print(f"Error processing events: {str(e)}")

if __name__ == "__main__":
    main()