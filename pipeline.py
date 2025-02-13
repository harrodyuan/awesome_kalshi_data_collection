import os
from datetime import datetime

# Import classes from other modules
from auth_manager import AuthManager
from events_collector import EventsCollector
from market_collector import MarketCollector
from event_analyzer import EventAnalyzer

global MAX_EVENTS # Maximum number of events to process
MAX_EVENTS = 1
class DataPipeline:
    def __init__(self):
        self.auth = AuthManager(
            key_id="05b95ed4-a236-41a1-9e3b-81124f6871dd",
            key_file_path="private_key.pem"
        )
        self.date_str = datetime.now().strftime('%Y%m%d')
        
    def run_pipeline(self):
        """Run the complete data collection and analysis pipeline."""
        print("\n=== Starting Data Collection Pipeline ===")
        print(f"Date: {self.date_str}")
        
        try:
            # 1. Collect Events
            print("\n1. Collecting Events...")
            events_collector = EventsCollector(self.auth)
            events_file = events_collector.collect_events()
            print(f"Events saved to: {events_file}")
            
            # 2. Collect Markets
            print("\n2. Collecting Markets...")
            market_collector = MarketCollector(self.auth)
            markets_file = market_collector.collect_all_markets(events_file=events_file, max_events=MAX_EVENTS)
            print(f"Markets saved to: {markets_file}")
            
            # 3. Analyze Data
            print("\n3. Analyzing Event Data...")
            analyzer = EventAnalyzer()
            summary = analyzer.analyze_existing_data(events_file)
            analyzer.print_summary(summary)
            
            print("\n=== Pipeline Complete ===")
            print(f"Data collection for {self.date_str} finished successfully")
            
        except Exception as e:
            print(f"\nERROR: Pipeline failed - {str(e)}")
            raise

if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run_pipeline()
