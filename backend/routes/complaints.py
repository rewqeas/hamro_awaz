import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..utils.file_handler import load_json, save_json
from ..dependency import get_current_user

# File paths
COMPLAINTS_FILE = "complains.json"
USERS_FILE = "users.json"

# Set up upload directory with absolute path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "complaints")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Debug print to verify paths
print(f"Upload directory: {UPLOAD_DIR}")

complaints_router = APIRouter(prefix="/complaints", tags=["Complaints"])

# Response model
class Complaint(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    author_phone: str
    municipality: str
    ward: str
    status: str
    created_at: str
    upvotes: int
    upvoted_by: List[int]
    image_url: Optional[str] = None

# Helpers
def load_complaints():
    return load_json(COMPLAINTS_FILE)

def save_complaints(complaints):
    save_json(COMPLAINTS_FILE, complaints)

def load_users():
    return load_json(USERS_FILE)

def generate_complaint_id(complaints: List[dict]) -> int:
    return max((c["id"] for c in complaints), default=0) + 1

# POST: Create complaint (with optional image)
@complaints_router.post("/", response_model=Complaint)
async def create_complaint(
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    complaints = load_complaints()
    users = load_users()

    user = next((u for u in users if u["id"] == current_user["id"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Save image if provided
    image_url = None
    if image:
        try:
            # Clean filename and ensure unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = os.path.splitext(image.filename)[1].lower()
            filename = f"complaint_{timestamp}_{current_user['id']}{file_ext}"
            
            # Create full file path
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Read the file content
            contents = await image.read()
            
            # Save the file
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Generate URL path (use forward slashes for URL)
            image_url = f"/uploads/complaints/{filename}"
            
            # Reset file pointer for potential future reads
            await image.seek(0)
            
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

    new_id = generate_complaint_id(complaints)
    complaint = {
        "id": new_id,
        "title": title,
        "content": content,
        "author_id": current_user["id"],
        "author_phone": current_user["sub"],
        "municipality": user.get("municipality", "Unknown"),
        "ward": user.get("ward", "Unknown"),
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "upvotes": 0,
        "upvoted_by": [],
        "image_url": image_url
    }

    complaints.append(complaint)
    save_complaints(complaints)
    return complaint

# GET: List all complaints
@complaints_router.get("/", response_model=List[Complaint])
def list_complaints(current_user: dict = Depends(get_current_user)):
    return load_complaints()

# POST: Upvote complaint
@complaints_router.post("/{complaint_id}/upvote")
def upvote_complaint(complaint_id: int, current_user: dict = Depends(get_current_user)):
    complaints = load_complaints()
    complaint = next((c for c in complaints if c["id"] == complaint_id), None)

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    user_id = current_user["id"]

    if user_id in complaint["upvoted_by"]:
        raise HTTPException(status_code=400, detail="You have already upvoted this complaint")

    complaint["upvoted_by"].append(user_id)
    complaint["upvotes"] = len(complaint["upvoted_by"])

    save_complaints(complaints)
    return {"message": "Upvoted successfully", "upvotes": complaint["upvotes"]}

# POST: Unvote complaint
@complaints_router.post("/{complaint_id}/unvote")
def unvote_complaint(complaint_id: int, current_user: dict = Depends(get_current_user)):
    complaints = load_complaints()
    complaint = next((c for c in complaints if c["id"] == complaint_id), None)

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    user_id = current_user["id"]

    if user_id not in complaint["upvoted_by"]:
        raise HTTPException(status_code=400, detail="You have not upvoted this complaint")

    complaint["upvoted_by"].remove(user_id)
    complaint["upvotes"] = len(complaint["upvoted_by"])

    save_complaints(complaints)
    return {"message": "Unvoted successfully", "upvotes": complaint["upvotes"]}
