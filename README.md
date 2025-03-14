# Kalshi Data Collection Pipeline

A robust Python tool for collecting and analyzing market data from [Kalshi](https://kalshi.com).

## Setup

### Prerequisites
- Python 3.8+
- Required packages: Install using `pip install -r requirements.txt`

### Authentication
1. Create `private_key.pem` in project root directory
2. Add your Kalshi private key to this file
3. Update `key_id` in configuration
   
## Pipeline Components

### Core Scripts
- `open_events_collector.py`: Fetches open events from Kalshi
- `open_market_collector.py`: Collects detailed market data
- `process_open_events.py`: Processes and formats event data
- `process_market_details.py`: Analyzes and processes market details
- `pipeline_all_kalshi.py`: Main pipeline orchestrator

### Directory Structure
```
historical_data/
├── open_events/           # Raw event data
├── open_markets/         # Raw market data
├── open_markets_individual/  # Individual market details
├── processed_events/     # Processed event data (CSV)
└── processed_markets/    # Processed market data (CSV)
```

## Usage

### Run Complete Pipeline
To execute the entire data collection and processing pipeline:
```bash
python pipeline_all_kalshi.py
```

This will:
1. Collect all open events
2. Gather market data
3. Process events into CSV format
4. Process market details with statistics

### Output
The pipeline generates:
- JSON files containing raw data
- CSV files with processed data
- Summary statistics for markets

## Pipeline Steps
1. Event Collection: Fetches current open events
2. Market Collection: Gathers detailed market data
3. Event Processing: Converts events to structured format
4. Market Processing: Analyzes market details and statistics