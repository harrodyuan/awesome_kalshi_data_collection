#!/usr/bin/env python3
"""
Integrated pipeline for collecting and processing Kalshi market data.
This script combines the functionality of:
- open_events_collector.py
- open_market_collector.py
- process_open_events.py
- process_market_details.py

The pipeline:
1. Collects open events from Kalshi API
2. Processes events data to collect markets
3. Processes events data to create a CSV
4. Processes market details to create detailed statistics
"""


import os
import sys
import time
import logging
import subprocess
from datetime import date
import importlib.util

# Set up logging with a more restrictive level for third-party modules
logging.getLogger().setLevel(logging.WARNING)  # Set default level to WARNING
logger = logging.getLogger('kalshi_pipeline')  # Create our own logger
logger.setLevel(logging.INFO)

# Create formatter and handler
formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

def create_directories():
    """Create necessary directories if they don't exist."""
    dirs = [
        "historical_data",
        "historical_data/open_events",
        "historical_data/open_markets",
        "historical_data/open_markets_individual",
        "historical_data/processed_events",
        "historical_data/processed_markets"
    ]
    
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.debug(f"Created directory: {directory}")

def run_subprocess(command, env=None):
    """Run a subprocess with controlled output."""
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            env=env
        )
        # More focused filtering of output lines
        important_keywords = [
            'total markets processed:',
            'successfully collected',
            'processed markets from'
        ]
        
        for line in result.stdout.split('\n'):
            line = line.lower().strip()
            if any(keyword in line for keyword in important_keywords):
                # Clean up the output format
                if 'successfully collected' in line:
                    logger.info(f"Collected {line.split()[2]} events")
                elif 'processed markets from' in line:
                    nums = [int(s) for s in line.split() if s.isdigit()]
                    logger.info(f"Processed {nums[0]} markets from {nums[1]} events")
                elif 'total markets processed:' in line:
                    num = int(line.split(':')[1].strip())
                    logger.info(f"Total markets: {num}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(command)}")
        logger.error(e.stderr)
        return False

# Update the main execution to show less output
def run_pipeline():
    """Run the full Kalshi data collection and processing pipeline."""
    today = date.today().strftime("%Y%m%d")

    # Step 1: Create necessary directories
    create_directories()

    # Step 2: Collect open events
    env = os.environ.copy()
    env['PROCESSING_DATE'] = today
    
    pipeline_steps = [
        ("Collecting open events", ["python", "open_events_collector.py"]),
        ("Collecting open markets", ["python", "open_market_collector.py"]),
        ("Processing open events", ["python", "process_open_events.py"]),
        ("Processing market details", ["python", "process_market_details.py"])
    ]
    
    for step_num, (step_desc, command) in enumerate(pipeline_steps, 1):
        logger.info(f"Running step {step_num}/{len(pipeline_steps)}...")
        
        if not run_subprocess(command, env):
            logger.error(f"Pipeline failed at step {step_num}")
            return False

    logger.info(f"Pipeline completed successfully - {today}")

if __name__ == "__main__":
    start_time = time.time()
    logger.info("Starting Kalshi data collection and processing pipeline...")
    
    try:
        run_pipeline()
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Pipeline execution completed in {elapsed_time:.2f} seconds")