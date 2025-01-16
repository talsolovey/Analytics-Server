import requests
import random
from joblib import Parallel, delayed
from typing import Dict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Azure-hosted app's URL
API_URL = "http://analytics-server.eastus.azurecontainer.io:8000/process_event"

# Pool of user names.
USER_POOL = ["alice", "bob", "charlie", "dave", "eve"]
             
# Generate random user IDs and event names
def generate_random_data() -> Dict[str, str]:
    userid = random.choice(USER_POOL)
    eventname = random.choice(["eventA", "eventB", "eventC", "eventD"])
    return {"userid": userid, "eventname": eventname}

# Function to send a single HTTP POST request
def send_request(data: Dict[str, str]) -> None:
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            logging.info("Successfully sent: %s", data)
        else:
            logging.error("Failed to send: %s, Status Code: %s", data, response.status_code)
    except Exception as e:
        logging.exception("Error sending request: %s", data)

# Main function to send 1,000 requests in parallel
def main() -> None:
    # Generate 1,000 random events
    events = [generate_random_data() for _ in range(1000)]

    # Use joblib to send requests in parallel
    Parallel(n_jobs=4)(delayed(send_request)(event) for event in events)

if __name__ == "__main__":
    main()
