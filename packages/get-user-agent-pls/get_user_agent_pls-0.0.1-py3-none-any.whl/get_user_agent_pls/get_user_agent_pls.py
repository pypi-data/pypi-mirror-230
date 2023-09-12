import json
import os
import time
from .get_user_agent_pls_scraper import main as fetch_and_save_user_agents

# User agents file
USER_AGENTS_FILE = "user-agents.json"

def fetch_user_agent(browser="chrome", operating_system="windows"):
    """Fetch a user-agent string."""
    # Fetch and save the latest user agents if the file doesn't exist or is older than a week
    if not os.path.exists(USER_AGENTS_FILE) or time.time() - os.path.getmtime(USER_AGENTS_FILE) > 7 * 24 * 60 * 60:
        user_agents = fetch_and_save_user_agents()
        with open(USER_AGENTS_FILE, 'w') as f:
            json.dump(user_agents, f)
    else:
        # Load the user agents from the JSON file
        with open(USER_AGENTS_FILE, 'r') as f:
            user_agents = json.load(f)
        
    return user_agents.get(browser.capitalize(), "")

if __name__ == "__main__":
    # Test fetching a user-agent string
    print(fetch_user_agent())
