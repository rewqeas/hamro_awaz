from utils.auth_utils import login_user

try:
    user = login_user("9841000000", "pass123")  # use real data from users.json
    print("Login successful:", user)
except ValueError as e:
    print("Login failed:", e)
