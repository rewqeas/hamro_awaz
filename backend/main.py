from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes.auth import auth_router
from .routes.complaints import complaints_router
from .routes.municipality import municipality_router


app = FastAPI()






#include the auth routes
app.include_router(auth_router)
app.include_router(complaints_router)
app.include_router(municipality_router)


# Configure CORS for file serving
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up file serving
import os

# Configure uploads directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up one level to project root
UPLOADS_DIR = os.path.join(BASE_DIR, "backend", "uploads")  # Put uploads inside backend folder

# Ensure directories exist
os.makedirs(os.path.join(UPLOADS_DIR, "complaints"), exist_ok=True)
os.makedirs(os.path.join(UPLOADS_DIR, "municipality"), exist_ok=True)

print(f"Project root directory: {BASE_DIR}")  # Debug print
print(f"Uploads directory: {UPLOADS_DIR}")  # Debug print

# Mount the uploads directory for static file serving
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

@app.get("/")
def root():
    return {"message": "Complaint Box API running"}