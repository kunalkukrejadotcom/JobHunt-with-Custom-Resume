import json
import os

PROFILE_PATH = os.path.join("data", "master_profile.json")

def load_profile():
    if not os.path.exists(PROFILE_PATH):
        # Return an empty shell if not found
        return {
            "basics": {},
            "skills": {"languages": [], "frameworks": [], "tools": []},
            "experiences": [],
            "education": []
        }
    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_profile(data):
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
