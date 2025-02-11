from collections import defaultdict
from typing import Dict, List
import json

class EventAnalyzer:
    def analyze_existing_data(self, json_path: str) -> Dict:
        """Analyze events from existing JSON file."""
        # Load data
        with open(json_path, 'r') as f:
            data = json.load(f)
            events = data.get('events', [])
            
        # Initialize counters
        summary = {
            'total_events': len(events),
            'categories': defaultdict(int),
            'time_types': defaultdict(int)
        }
        
        # Analyze events
        for event in events:
            # Count categories
            category = event.get('category', 'unknown')
            summary['categories'][category] += 1
            
            # Analyze time specifications
            if event.get('strike_date'):
                summary['time_types']['specific_date'] += 1
            elif event.get('strike_period'):
                summary['time_types']['date_range'] += 1
            else:
                summary['time_types']['no_date or date info in title?'] += 1
        
        return summary
    
    def print_summary(self, summary: Dict):
        """Print formatted analysis summary."""
        print("\n=== Events Analysis ===")
        print(f"Total Events: {summary['total_events']}")
        
        print("\nCategory Distribution:")
        for category, count in sorted(summary['categories'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / summary['total_events']) * 100
            print(f"{category}: {count} ({percentage:.1f}%)")
            
        print("\nTime Specification Distribution:")
        for time_type, count in sorted(summary['time_types'].items()):
            percentage = (count / summary['total_events']) * 100
            print(f"{time_type}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    analyzer = EventAnalyzer()
    summary = analyzer.analyze_existing_data("events_20250211.json")
    analyzer.print_summary(summary)
