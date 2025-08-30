# Hamro Aawaz API Endpoints Documentation

## Base URL
- **Local Development**: `http://localhost:8000`
- **Replit Environment**: `https://{replit-domain}`

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication Endpoints

### • **POST** `/auth/register`
Register a new user in the system.

#### **Request Format**
```json
{
  "id": 1001,
  "name": "John Doe",
  "phone": "9841234567",
  "password": "securepassword",
  "role": "citizen",
  "city": "Kathmandu",
  "municipality": "Kathmandu Metropolitan City",
  "ward": "Ward 1"
}
```

#### **Response Format**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1001,
    "name": "John Doe",
    "phone": "9841234567",
    "role": "citizen",
    "city": "Kathmandu",
    "municipality": "Kathmandu Metropolitan City",
    "ward": "Ward 1"
  }
}
```

---

### • **POST** `/auth/login`
Authenticate a user and get JWT token.

#### **Request Format**
```json
{
  "phone": "9841234567",
  "password": "securepassword"
}
```

#### **Response Format**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### • **GET** `/auth/me`
Get current user information from JWT token.

#### **Request Format**
- Headers: `Authorization: Bearer <token>`
- Body: None

#### **Response Format**
```json
{
  "current_user": {
    "sub": "9841234567",
    "role": "citizen",
    "id": 1001
  }
}
```

---

### • **GET** `/auth/users`
Get all users (for ID generation).

#### **Request Format**
- Headers: `Authorization: Bearer <token>`
- Body: None

#### **Response Format**
```json
[
  {
    "id": 1001,
    "name": "John Doe",
    "phone": "9841234567",
    "role": "citizen",
    "city": "Kathmandu",
    "municipality": "Kathmandu Metropolitan City",
    "ward": "Ward 1"
  }
]
```

---

## 📝 Complaints Endpoints

### • **POST** `/complaints/`
Create a new complaint with optional image upload.

#### **Request Format**
```form-data
title: "Road condition is terrible"
content: "The road in our area has many potholes and needs immediate repair"
image: <file> (optional)
```

#### **Response Format**
```json
{
  "id": 1,
  "title": "Road condition is terrible",
  "content": "The road in our area has many potholes and needs immediate repair",
  "author_id": 1001,
  "author_phone": "9841234567",
  "municipality": "Kathmandu Metropolitan City",
  "ward": "Ward 1",
  "status": "open",
  "created_at": "2025-08-29T10:30:45.123456",
  "upvotes": 0,
  "upvoted_by": [],
  "image_url": "/uploads/complaints/complaint_20250829_103045_1001.jpg"
}
```

---

### • **GET** `/complaints/`
Get all complaints.

#### **Request Format**
- Headers: `Authorization: Bearer <token>`
- Body: None

#### **Response Format**
```json
[
  {
    "id": 1,
    "title": "Road condition is terrible",
    "content": "The road in our area has many potholes and needs immediate repair",
    "author_id": 1001,
    "author_phone": "9841234567",
    "municipality": "Kathmandu Metropolitan City",
    "ward": "Ward 1",
    "status": "open",
    "created_at": "2025-08-29T10:30:45.123456",
    "upvotes": 0,
    "upvoted_by": [],
    "image_url": "/uploads/complaints/complaint_20250829_103045_1001.jpg"
  }
]
```

---

### • **POST** `/complaints/{complaint_id}/upvote`
Upvote a specific complaint.

#### **Request Format**
- Headers: `Authorization: Bearer <token>`
- Path: `complaint_id` (integer)
- Body: None

#### **Response Format**
```json
{
  "message": "Upvoted successfully",
  "upvotes": 5
}
```

---

### • **POST** `/complaints/{complaint_id}/unvote`
Remove upvote from a specific complaint.

#### **Request Format**
- Headers: `Authorization: Bearer <token>`
- Path: `complaint_id` (integer)
- Body: None

#### **Response Format**
```json
{
  "message": "Unvoted successfully",
  "upvotes": 4
}
```

---

## 🏛️ Municipality Endpoints

### • **GET** `/municipality/`
Get all municipalities data.

#### **Request Format**
- Headers: `Authorization: Bearer <token>`
- Body: None

#### **Response Format**
```json
[
  {
    "municipality": "Kathmandu Metropolitan City",
    "city": "Kathmandu",
    "activities": [
      {
        "complaint_id": 1,
        "title": "Road Repair Activity",
        "action": "working",
        "statement": "We have started working on the road repair",
        "timestamp": "2025-08-29T11:00:00.123456",
        "by": 2001,
        "action_image": "/uploads/municipality/1756441234567_2001.jpg"
      }
    ]
  }
]
```

---

### • **GET** `/municipality/activities`
Get all municipality activities across all municipalities.

#### **Request Format**
- Headers: `Authorization: Bearer <token>`
- Body: None

#### **Response Format**
```json
[
  {
    "complaint_id": 1,
    "title": "Road Repair Activity",
    "action": "working",
    "statement": "We have started working on the road repair",
    "timestamp": "2025-08-29T11:00:00.123456",
    "by": 2001,
    "action_image": "/uploads/municipality/1756441234567_2001.jpg",
    "municipality": "Kathmandu Metropolitan City"
  }
]
```

---

### • **POST** `/municipality/post-action`
Post a new municipality activity (Staff only).

#### **Request Format**
```form-data
title: "New Infrastructure Project"
action: "working"
statement: "Starting new bridge construction project"
image: <file> (optional)
```

#### **Response Format**
```json
{
  "message": "Post added to municipality feed",
  "post": {
    "complaint_id": null,
    "title": "New Infrastructure Project",
    "action": "working",
    "statement": "Starting new bridge construction project",
    "timestamp": "2025-08-29T12:00:00.123456",
    "by": 2001,
    "action_image": "/uploads/municipality/1756441567890_2001.jpg"
  }
}
```

---

### • **POST** `/municipality/update-complaint-status`
Update the status of a specific complaint (Staff only).

#### **Request Format**
```form-data
complaint_id: 1
status: "completed"
statement: "Road repair has been completed successfully"
image: <file> (optional)
```

#### **Response Format**
```json
{
  "message": "Complaint 1 status updated to completed",
  "activity": {
    "complaint_id": 1,
    "title": "Road condition is terrible",
    "action": "Marked as completed",
    "statement": "Road repair has been completed successfully",
    "timestamp": "2025-08-29T13:00:00.123456",
    "by": 2001,
    "action_image": "/uploads/municipality/1756441789012_2001.jpg"
  }
}
```

---

## 🏠 Root Endpoint

### • **GET** `/`
Health check endpoint.

#### **Request Format**
- Body: None

#### **Response Format**
```json
{
  "message": "Complaint Box API running"
}
```

---

## 📁 Static File Serving

### • **GET** `/uploads/{file_path}`
Serve uploaded images and files.

#### **Request Format**
- Path: `file_path` (e.g., `complaints/complaint_20250829_103045_1001.jpg`)

#### **Response Format**
- Returns the actual file content with appropriate MIME type

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error message describing what went wrong"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Only staff can perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred"
}
```

---

## Notes

- **Image Upload**: All image uploads are optional and support JPG, JPEG, and PNG formats
- **Authentication**: Most endpoints require JWT authentication except for registration and login
- **Role-based Access**: Some endpoints are restricted to `staff` role users only
- **File Storage**: Uploaded files are stored in `/backend/uploads/` directory
- **CORS**: API is configured to allow cross-origin requests for frontend integration