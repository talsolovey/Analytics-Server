import requests
import random
import string
from joblib import Parallel, delayed
from typing import Dict

# Azure-hosted app's URL
API_URL = "https://my-analytics-server.azurewebsites.net/process_event"

# Generate random user IDs and event names
def generate_random_data() -> Dict[str, str]:
    userid = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    eventname = random.choice(["eventA", "eventB", "eventC", "eventD"])
    return {"userid": userid, "eventname": eventname}

# Function to send a single HTTP POST request
def send_request(data: Dict[str, str]) -> None:
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            print(f"Successfully sent: {data}")
        else:
            print(f"Failed to send: {data}, Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending request: {e}")

# Main function to send 1,000 requests in parallel
def main() -> None:
    # Generate 1,000 random events
    events = [generate_random_data() for _ in range(1000)]

    # Use joblib to send requests in parallel
    Parallel(n_jobs=5)(delayed(send_request)(event) for event in events)

if __name__ == "__main__":
    main()
