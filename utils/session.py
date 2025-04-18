import json
import os

SESSION_FILE = "data/session.json"

def save_login(username, role):
    os.makedirs("data", exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump({"username": username, "role": role}, f)

def load_login():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None

def clear_login():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
