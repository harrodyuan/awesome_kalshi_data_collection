# Kalshi Data Collection Pipeline BD_Harold

A robust Python tool for collecting and analyzing market data from [Kalshi](https://kalshi.com).

### Configure authentication:
   - Create `private_key.pem` in project root
   - Add your Kalshi private key to this file
   - Update `key_id` in configuration

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

3. Or instead, you could just run the full pipeline all at once.
```bash
python pipeline.py
```

## Author
BD_Harold
