from utils.file_handler import load_json, save_json

USERS_FILE = 'users.json'

def authenticate_user(phone:str, password:str):
    """
    Authenticate user by phone and password (plain check).
    Returns user dict if valid, else None.
    """
    users = load_json(USERS_FILE)

    for user in users:
        if user['phone'] == phone and user['password'] == password:
            return user
        
    return None


def register_user(user_data: dict):
    """
    Register a new user.
    Expects dict with keys: id, name, phone, password, role, city, municipality, ward
    """
    users = load_json(USERS_FILE)

    # ✅ Check duplicate phone number
    for user in users:
        if user['phone'] == user_data['phone']:
            raise ValueError("Phone number already registered")

    # ✅ Append and save outside the loop
    users.append(user_data)
    save_json(USERS_FILE, users)
    return user_data

    
def get_user_by_id(user_id:int):
    """
    Fetch a single user by their ID.
    Returns dict or None if not found.
    """

    users = load_json(USERS_FILE)

    for user in users:
        if user['phone'] == user_id:
            return user
        
    return None

def get_all_users():
    """
    Return list of all users.
    """
    return load_json(USERS_FILE)

def login_user(phone:str, password:str)->dict:
    """
    Login user by verifying phone and password.
    Returns user dict if valid, else raises ValueError.
    """

    users = load_json(USERS_FILE)

    for user in users:
        if user['phone'] == phone:
            if user['password'] == password:
                return user #login successful
            
            else:
                raise ValueError("Incorrect password")
            
        raise ValueError('Phone number not registered')
    

