# Substrate Blockchain Data Ingestor for Redis

This project is a Python script designed to fetch and ingest all historical data from a Substrate-based blockchain while simultaneously listening for and ingesting real-time data. The data is stored in a Redis database and published for easy access and analysis.

## Features

- **Historical Data Ingestion:** Fetches all historical blocks from the blockchain, starting from block 1 up to the latest finalized block.
- **Real-Time Data Listening:** Continuously listens for new blocks as they are produced and ingests them into Redis.
- **Parallel Processing:** Utilizes parallel processing to fetch multiple blocks simultaneously, improving performance.
- **Redis Integration:** Stores blocks in Redis and publishes updates on new blocks for real-time monitoring and analysis.

## Requirements

- Python 3.7+
- Redis
- `pip` to install Python dependencies

### Python Packages

The following Python packages are required:

- `requests`
- `redis`
- `certifi`
- `asyncio`

## Installation

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/substrate-blockchain-ingestor.git
cd substrate-blockchain-ingestor
```

### 2. Set Up a Virtual Environment (Optional)

It's recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install Required Python Packages

Install the necessary Python packages using `pip`:

```bash
pip install redis certifi requests
```

### 4. Ensure Redis is Running

Make sure you have a Redis server running locally or remotely. You can start Redis using:

```bash
redis-server
```

## Usage

### Running the Script

After setting up the environment and installing dependencies, you can run the script:

```bash
python3 ingester.py
```

### What the Script Does

- **Historical Data Fetching:** The script fetches all historical blocks in batches and ingests them into Redis.
- **Real-Time Data Listening:** While historical data is being fetched, the script also listens for new blocks and ingests them in real-time.
- **Data Storage:** Each block is stored in Redis with the key format `block:<block_number>`.

### Configuration

You can configure various parameters in the script, such as:

- **`BATCH_SIZE`:** Number of blocks to fetch in each batch.
- **`MAX_WORKERS`:** Number of parallel workers to use for fetching blocks.
- **`RPC_ENDPOINT`:** URL of the Substrate RPC endpoint.

## Query Blockchain by Block Number

Currently, the script supports queries by block number; however, the output is data rich when a block number is queried. Run this command after you started the Redis server:
```
redis-cli get block:[blocknumber] | jq .
```

Specify a block number for **blocknumber** above.

For example, if you query block 23867, you will run

```
redis-cli get block:23867 | jq .
```

And the output is below:

<img width="1283" alt="Screenshot 2024-08-29 at 2 53 56 PM" src="https://github.com/user-attachments/assets/cc2792fc-60b0-4906-9369-cc0b9fa60c21">

However, if you wish to query another parameter (like parentHash, for example), keep in mind Redis stores the data of a block in a serialized JSON object, not as keys and suffixes.  That being said, you can query parentHash, extrinsics, logs, etc. **by passing them as a jq suffix.** 

Run the following commands below to get information on the block's data:

```
# Remember to specify the block number in place of [blocknumber] below:

# Get the parentHsh of the block
redis-cli GET block:[blocknumber] | jq '.block.header.parentHash' 

# Get the stateRoot of the block
redis-cli GET block:[blocknumber] | jq '.block.header.stateRoot'

# Get the logs of the block
redis-cli GET block:[blocknumber] | jq '.block.header.digest.logs[]'

# Get the extrinsics of the block
redis-cli GET block:[blocknumber] | jq '.block.extrinsics[]'
``` 


## Troubleshooting

### Common Issues

- **Import Errors:** Ensure that there is no file named `redis.py` in your working directory to avoid conflicts with the `redis` Python package.
- **SSL Certificate Errors:** The script uses `certifi` to handle SSL certificates. If you encounter SSL errors, ensure that the certificates are correctly installed and accessible.

### Logs

The script logs all activities, including any errors encountered during execution. You can check the console output for detailed logs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork this repository, make your changes, and submit a pull request.
