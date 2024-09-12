import asyncio
import concurrent.futures
import redis
import ssl
import certifi
import json
import logging
import requests

# Configurations
RPC_ENDPOINT = "PUT-YOUR-RPC-URL-HERE"   # Replace with your RPC Endpoint for Substrate
BATCH_SIZE = 100  # Batch size for Redis operations
MAX_WORKERS = 10  # Number of parallel workers

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to Redis
r = redis.Redis()

# SSL context using certifi to ensure SSL certificate validation
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Fetch the block hash for a given block number
def fetch_block_data(block_number):
    try:
        response = requests.post(
            RPC_ENDPOINT,
            json={"jsonrpc": "2.0", "method": "chain_getBlockHash", "params": [block_number], "id": 1},
            headers={"Content-Type": "application/json"},
            verify=certifi.where()
        )
        block_hash = response.json().get("result")

        if block_hash:
            response = requests.post(
                RPC_ENDPOINT,
                json={"jsonrpc": "2.0", "method": "chain_getBlock", "params": [block_hash], "id": 1},
                headers={"Content-Type": "application/json"},
                verify=certifi.where()
            )
            block_data = response.json().get("result")
            return block_number, block_data
        return block_number, None
    except Exception as e:
        logging.error(f"Error fetching block {block_number}: {e}")
        return block_number, None

# Get the latest finalized block number
def get_latest_block_number():
    response = requests.post(
        RPC_ENDPOINT,
        json={"jsonrpc": "2.0", "method": "chain_getFinalizedHead", "params": [], "id": 1},
        headers={"Content-Type": "application/json"},
        verify=certifi.where()
    )
    latest_block_hash = response.json().get("result")
    response = requests.post(
        RPC_ENDPOINT,
        json={"jsonrpc": "2.0", "method": "chain_getBlock", "params": [latest_block_hash], "id": 1},
        headers={"Content-Type": "application/json"},
        verify=certifi.where()
    )
    block_data = response.json().get("result")
    block_number = block_data['block']['header']['number']
    return int(block_number, 16)  # Convert from hex to int

# Process blocks in parallel
def process_blocks(block_numbers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_block = {executor.submit(fetch_block_data, bn): bn for bn in block_numbers}
        for future in concurrent.futures.as_completed(future_to_block):
            block_number, block_data = future.result()
            if block_data:
                r.set(f'block:{block_number}', json.dumps(block_data))
                r.publish('new_block', f"Block Number: {block_number}")
                r.set('latest_block_number', block_number)  # Update the last processed block number
                logging.info(f"Ingested Block {block_number}")

# Fetch all historical data
async def fetch_all_historical_data():
    logging.info("Fetching all historical data...")
    
    latest_block_number = get_latest_block_number()

    # Fetch the last processed block number from Redis or start from block 1
    last_processed_block = int(r.get('latest_block_number') or 0)
    block_number = last_processed_block + 1
    
    while block_number <= latest_block_number:
        block_numbers = range(block_number, min(block_number + BATCH_SIZE, latest_block_number + 1))
        process_blocks(block_numbers)
        block_number += BATCH_SIZE

# Listen for real-time data
async def listen_realtime_data():
    logging.info("Starting to listen for real-time data...")
    while True:
        # Fetch the last processed block number from Redis or start from block 1
        last_processed_block = int(r.get('latest_block_number') or 0)
        block_number = last_processed_block + 1
        
        _, block_data = fetch_block_data(block_number)
        if block_data:
            r.set(f'block:{block_number}', json.dumps(block_data))
            r.publish('new_block', f"Block Number: {block_number}")
            r.set('latest_block_number', block_number)  # Update the last processed block number
            logging.info(f"Ingested Block {block_number}")
        await asyncio.sleep(2)  # Adjust this to control polling frequency

# Run historical and real-time tasks concurrently
async def main():
    historical_task = asyncio.create_task(fetch_all_historical_data())
    realtime_task = asyncio.create_task(listen_realtime_data())

    await asyncio.gather(historical_task, realtime_task)

# Start the event loop
asyncio.run(main())
