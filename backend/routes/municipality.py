from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os
from ..utils.file_handler import load_json, save_json
from ..dependency import get_current_user

# Load user info since it's not in JWT token
USERS_FILE = "users.json"

def get_full_user_info(user_id: int):
    users = load_json(USERS_FILE)
    return next((u for u in users if u["id"] == user_id), None)

MUNICIPALITY_FILE = "municipality.json"
COMPLAINTS_FILE = "complains.json"

# ----------------- FIXED PATH -----------------
# Go up to project root, then to backend/uploads/municipality
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "backend", "uploads", "municipality")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Debug print to verify paths
print(f"Municipality upload folder: {UPLOAD_FOLDER}")

municipality_router = APIRouter(prefix="/municipality", tags=["Municipality"])

# ---------------- MODELS ---------------- #
class ComplaintStatusUpdate(BaseModel):
    complaint_id: int
    status: str   # "working" or "completed"
    statement: Optional[str] = None   # optional field


# ---------------- HELPERS ---------------- #
def load_municipalities():
    return load_json(MUNICIPALITY_FILE)

def save_municipalities(data):
    save_json(MUNICIPALITY_FILE, data)

def load_complaints():
    return load_json(COMPLAINTS_FILE)

def save_complaints(data):
    save_json(COMPLAINTS_FILE, data)


# ---------------- ROUTES ---------------- #

# 1. Get all municipalities
@municipality_router.get("/")
async def get_municipalities(current_user: dict = Depends(get_current_user)):
    return load_municipalities()

# 2. Get all municipality activities
@municipality_router.get("/activities")
async def get_all_activities(current_user: dict = Depends(get_current_user)):
    municipalities = load_municipalities()
    all_activities = []
    for muni in municipalities:
        for activity in muni.get("activities", []):
            # Add municipality info to each activity
            activity_with_muni = {
                **activity,
                "municipality": muni["municipality"]
            }
            all_activities.append(activity_with_muni)
    
    # Sort by timestamp, newest first
    all_activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_activities

# 3. Municipality Post Action (with optional image)
@municipality_router.post("/post-action")
async def municipality_post(
    title: str = Form(...),
    action: str = Form(...),
    statement: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "staff":
        raise HTTPException(status_code=403, detail="Only staff can post municipality actions")

    user_info = get_full_user_info(current_user["id"])
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    municipalities = load_municipalities()
    municipality = next(
        (m for m in municipalities if m["municipality"].lower() == user_info["municipality"].lower()),
        None
    )
    if not municipality:
        raise HTTPException(status_code=404, detail="Municipality not found for current staff")

    # Handle image upload
    image_path = None
    if image:
        file_ext = os.path.splitext(image.filename)[1]
        filename = f"{datetime.now().timestamp()}_{current_user['id']}{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_path = f"/uploads/municipality/{filename}"

    activity = {
        "complaint_id": None,
        "title": title,
        "action": action,
        "statement": statement,
        "timestamp": datetime.now().isoformat(),
        "by": current_user["id"],
        "action_image": image_path
    }

    municipality["activities"].append(activity)
    save_municipalities(municipalities)

    return {"message": "Post added to municipality feed", "post": activity}


# 2. Update Complaint Status (with optional image)
@municipality_router.post("/update-complaint-status")
async def update_complaint_status(
    complaint_id: int = Form(...),
    status: str = Form(...),
    statement: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "staff":
        raise HTTPException(status_code=403, detail="Only staff can update complaint status")

    complaints = load_complaints()
    complaint = next((c for c in complaints if c["id"] == complaint_id), None)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Update complaint status
    complaint["status"] = status
    save_complaints(complaints)

    user_info = get_full_user_info(current_user["id"])
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    municipalities = load_municipalities()
    municipality = next(
        (m for m in municipalities if m["municipality"].lower() == user_info["municipality"].lower()),
        None
    )
    if not municipality:
        raise HTTPException(status_code=404, detail="Municipality not found for current staff")

    # Handle image upload
    image_path = None
    if image:
        file_ext = os.path.splitext(image.filename)[1]
        filename = f"{datetime.now().timestamp()}_{current_user['id']}{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_path = f"/uploads/municipality/{filename}"

    activity = {
        "complaint_id": complaint["id"],
        "title": complaint["title"],
        "action": f"Marked as {status}",
        "statement": statement,
        "timestamp": datetime.now().isoformat(),
        "by": current_user["id"],
        "action_image": image_path
    }

    municipality["activities"].append(activity)
    save_municipalities(municipalities)

    return {"message": f"Complaint {complaint['id']} status updated to {status}", "activity": activity}
