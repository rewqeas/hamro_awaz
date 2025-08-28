import json
import os

USERS_FILE = os.path.join("data", "users.json")

def add_user(new_user: dict):
    """Append a new user dict into users.json"""
    try:
        # Read existing users
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        else:
            users = []

        # Add new user
        users.append(new_user)

        # Save back
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)

        print(f"✅ User {new_user['name']} added successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Example test user
    test_user = {
        "id": 7,
        "name": "Test User",
        "phone": "9841000999",
        "password": "testpass",
        "role": "citizen",
        "city": "Kathmandu",
        "municipality": "Kathmandu Metropolitan",
        "ward": "Ward 12"
    }

    add_user(test_user)
