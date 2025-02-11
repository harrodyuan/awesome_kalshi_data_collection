# Kalshi Data Collection Pipeline

Python toolkit for collecting and analyzing data from [Kalshi](https://kalshi.com) markets.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Set up authentication:
- Create `private_key.pem` file with your Kalshi private key
- Update `key_id` in scripts with your key ID

## Usage

### 1. Collect Events
```bash
python events_collector.py
```
This will:
- Collect all available events from Kalshi
- Save to `historical_data/events/events_YYYYMMDD.json`
- Create checkpoint at `historical_data/checkpoint_events.json`

### 2. Collect Markets
```bash
python market_collector.py
```
This will:
- Process events and collect associated markets
- Save individual market files to `historical_data/markets/`
- Create checkpoint at `historical_data/checkpoint_markets.json`
- Limit collection to 10,000 events by default

### 3. Run Complete Pipeline
```bash
python pipeline.py
```
This will run the complete collection and analysis process.

## File Structure
```
kalshi-starter-code-python/
├── auth_manager.py        # Authentication handling
├── events_collector.py    # Events collection
├── market_collector.py    # Markets collection
├── market_data.py        # API interaction
├── event_analyzer.py      # Data analysis
├── pipeline.py           # Pipeline orchestration
└── historical_data/      # Collected data storage
    ├── events/          
    ├── markets/         
    └── failures/        
```

## Data Storage

- Events: `historical_data/events/events_YYYYMMDD.json`
- Markets: `historical_data/markets/markets_YYYYMMDD.json`
- Individual Markets: `historical_data/markets/markets_EVENTTICKER_YYYYMMDD.json`
- Failures: `historical_data/failures/failures_YYYYMMDD.txt`
- Checkpoints: `historical_data/checkpoint_*.json`

## Security Note

Keep your `private_key.pem` file secure and never commit it to version control.
The .gitignore file is set up to prevent accidental commits of sensitive data.

## License

MIT

## Author

BD_Harold