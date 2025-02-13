# Kalshi Data Collection Pipeline

A robust Python toolkit for collecting and analyzing market data from [Kalshi](https://kalshi.com).

## Prerequisites

- Python 3.8+
- Valid Kalshi account with API access
- API key and key ID from Kalshi

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd kalshi-starter-code-python
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure authentication:
   - Create `private_key.pem` in project root
   - Add your Kalshi private key to this file
   - Update `key_id` in configuration

## Components

### Data Collection Scripts
- `events_collector.py`: Fetches event data
- `market_collector.py`: Gathers market information
- `pipeline.py`: Orchestrates the complete collection process

### Usage Examples

1. Collect Events:
```bash
python events_collector.py
```

2. Collect Markets:
```bash
python market_collector.py --limit 10000
```

3. Run Full Pipeline:
```bash
python pipeline.py
```

## Data Structure

```
historical_data/
├── events/
│   └── events_YYYYMMDD.json
├── markets/
│   ├── markets_YYYYMMDD.json
│   └── markets_EVENTTICKER_YYYYMMDD.json
├── failures/
│   └── failures_YYYYMMDD.txt
└── checkpoints/
    ├── checkpoint_events.json
    └── checkpoint_markets.json
```

## Troubleshooting

- **Authentication Errors**: Verify `private_key.pem` format and permissions
- **Rate Limiting**: Adjust collection delay in configuration
- **Data Gaps**: Check checkpoint files for collection status

## Security

- Never commit `private_key.pem`
- Review .gitignore settings
- Rotate API keys regularly

## License

MIT

## Author

BD_Harold