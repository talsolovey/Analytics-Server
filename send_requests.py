import requests
import random
from joblib import Parallel, delayed
from typing import Dict
import logging
from colorama import Fore, Style

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add colorized log methods
def info_color(message):
    logger.info(Fore.GREEN + message + Style.RESET_ALL)

def warning_color(message):
    logger.warning(Fore.YELLOW + message + Style.RESET_ALL)

def error_color(message):
    logger.error(Fore.RED + message + Style.RESET_ALL)

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
    result = {"success": 0, "failure": 0, "failed_requests": []}
    try:
        response = requests.post(API_URL, json=data, timeout=5)
        if response.status_code == 200:
            result["success"] += 1
        else:
            result["failure"] += 1
            result["failed_requests"].append({"data": data, "status_code": response.status_code, "response": response.text})
    except Exception as e:
        result["failure"] += 1
        result["failed_requests"].append({"data": data, "error": str(e)})
    return result


# Main function to send 1,000 requests in parallel
def main() -> None:
    # Generate 1,000 random events
    events = [generate_random_data() for _ in range(1000)]

    # Use joblib to send requests in parallel
    all_results = Parallel(n_jobs=4)(delayed(send_request)(event) for event in events)

    # Aggregate results from all processes
    final_results = {"success": 0, "failure": 0, "failed_requests": []}
    for result in all_results:
        final_results["success"] += result["success"]
        final_results["failure"] += result["failure"]
        final_results["failed_requests"].extend(result["failed_requests"])

    # Log summary after all requests
    info_color(f"Batch completed: {final_results['success']} successful, {final_results['failure']} failed.")

    # Log failed requests (if any)
    if final_results["failed_requests"]:
        formatted_failed_requests = "\n".join(
            f"  - UserID: {item['data']['userid']}, Event: {item['data']['eventname']}, Status: {item.get('status_code', 'N/A')}, Response: {item.get('response', item.get('error', 'N/A'))}"
            for item in final_results["failed_requests"]
        )
        warning_color(f"Failed requests:\n{formatted_failed_requests}")

if __name__ == "__main__":
    main()
