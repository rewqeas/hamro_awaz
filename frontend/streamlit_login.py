import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def get_headers():
    """Get headers with authentication token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def make_request(method, endpoint, data=None, files=None, headers=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if headers is None:
            headers = get_headers()
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files, headers=headers)
            else:
                response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get('detail', 'Unknown error')
    except Exception as e:
        return False, str(e)

def login_user(phone, password):
    """Login user and store token"""
    success, result = make_request("POST", "/auth/login", {"phone": phone, "password": password}, headers={})
    if success:
        st.session_state.token = result['access_token']
        st.session_state.logged_in = True
        
        # Get user info
        success, user_info = make_request("GET", "/auth/me")
        if success:
            st.session_state.user = user_info['current_user']
        return True, "Login successful"
    return False, result

def logout_user():
    """Logout user and clear session"""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.logged_in = False
    st.rerun()

def register_user(user_data):
    """Register new user"""
    return make_request("POST", "/auth/register", user_data, headers={})

def get_next_user_id():
    """Get next available user ID"""
    success, users = make_request("GET", "/auth/users")
    if success and users:
        return max(user['id'] for user in users) + 1
    return 1001

# Page configuration
st.set_page_config(
    page_title="Hamro Aawaz - Complaint Box",
    page_icon="📢",
    layout="wide"
)

# Custom CSS
# Custom CSS
st.markdown("""
<style>
.complaint-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    color: #333;
}
.status-open { color: #ff4757; font-weight: bold; background: #fff5f5; padding: 4px 8px; border-radius: 4px; }
.status-working { color: #ffa502; font-weight: bold; background: #fff8f0; padding: 4px 8px; border-radius: 4px; }
.status-completed { color: #2ed573; font-weight: bold; background: #f0fff4; padding: 4px 8px; border-radius: 4px; }
.upvote-count { color: #1976d2; font-weight: bold; }
.municipality-post {
    border-left: 4px solid #2196f3;
    background: #f8f9fa;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.title("📢 Hamro Aawaz")
st.markdown("*Voice of the People - Digital Complaint Box System*")

# Authentication check
if not st.session_state.logged_in:
    # Authentication tabs
    auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with auth_tab1:
        st.header("Login")
        with st.form("login_form"):
            phone = st.text_input("Phone Number", placeholder="9841234567")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if phone and password:
                    success, message = login_user(phone, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(f"Login failed: {message}")
                else:
                    st.error("Please fill all fields")
    
    with auth_tab2:
        st.header("Register New Account")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name", placeholder="John Doe")
                phone = st.text_input("Phone Number", placeholder="9841234567")
                password = st.text_input("Password", type="password")
            
            with col2:
                role = st.selectbox("Role", ["citizen", "staff"])
                city = st.text_input("City", placeholder="Kathmandu")
                municipality = st.text_input("Municipality", placeholder="Kathmandu Metropolitan City")
                ward = st.text_input("Ward", placeholder="Ward 1")
            
            submit = st.form_submit_button("Register")
            
            if submit:
                if all([name, phone, password, city, municipality, ward]):
                    user_data = {
                        "id": get_next_user_id(),
                        "name": name,
                        "phone": phone,
                        "password": password,
                        "role": role,
                        "city": city,
                        "municipality": municipality,
                        "ward": ward
                    }
                    success, message = register_user(user_data)
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(f"Registration failed: {message}")
                else:
                    st.error("Please fill all fields")

else:
    # Main application for logged-in users
    
    # Sidebar with user info
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user.get('sub', 'User')}!")
        st.markdown(f"**Role:** {st.session_state.user.get('role', 'N/A').title()}")
        st.markdown(f"**ID:** {st.session_state.user.get('id', 'N/A')}")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Complaints", "🏛️ Municipality", "👤 Profile", "📊 Dashboard"])
    
    with tab1:
        st.header("Complaints Management")
        
        # Create new complaint section
        with st.expander("➕ Submit New Complaint", expanded=False):
            with st.form("complaint_form"):
                title = st.text_input("Title", placeholder="Brief description of the issue")
                content = st.text_area("Content", placeholder="Detailed description of the complaint...")
                image = st.file_uploader("Upload Image (Optional)", type=['jpg', 'jpeg', 'png'])
                
                submit = st.form_submit_button("Submit Complaint")
                
                if submit:
                    if title and content:
                        # Prepare form data
                        data = {"title": title, "content": content}
                        files = {"image": image} if image else None
                        
                        success, result = make_request("POST", "/complaints/", data, files)
                        if success:
                            st.success("Complaint submitted successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to submit complaint: {result}")
                    else:
                        st.error("Please fill in title and content")
        
        st.markdown("---")
        
        # Display all complaints
        st.subheader("All Complaints")
        success, complaints = make_request("GET", "/complaints/")
        
        if success and complaints:
            for complaint in complaints:
                with st.container():
                    st.markdown(f"""
                    <div class="complaint-card">
                        <h3>{complaint['title']}</h3>
                        <p><strong>Location:</strong> {complaint['municipality']}, {complaint['ward']}</p>
                        <p>{complaint['content']}</p>
                        <p><strong>Status:</strong> <span class="status-{complaint['status']}">{complaint['status'].upper()}</span> | 
                        <strong>Created:</strong> {complaint['created_at'][:19]}</p>
                    </div>
""", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        if complaint.get('image_url'):
                            st.image(f"{API_BASE_URL}{complaint['image_url']}", width=200)
                    
                    with col2:
                        st.markdown(f"**Upvotes:** {complaint['upvotes']}")
                        
                        # Check if user already upvoted
                        user_upvoted = st.session_state.user['id'] in complaint.get('upvoted_by', [])
                        
                        if user_upvoted:
                            if st.button(f"👎 Unvote", key=f"unvote_{complaint['id']}"):
                                success, result = make_request("POST", f"/complaints/{complaint['id']}/unvote")
                                if success:
                                    st.success("Removed upvote!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {result}")
                        else:
                            if st.button(f"👍 Upvote", key=f"upvote_{complaint['id']}"):
                                success, result = make_request("POST", f"/complaints/{complaint['id']}/upvote")
                                if success:
                                    st.success("Upvoted!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {result}")
                    
                    with col3:
                        if st.session_state.user.get('role') == 'staff':
                            with st.popover("🛠️ Staff Actions"):
                                new_status = st.selectbox("Update Status", 
                                                        ["open", "working", "completed"], 
                                                        key=f"status_{complaint['id']}")
                                statement = st.text_area("Statement", 
                                                        placeholder="Add update message...",
                                                        key=f"statement_{complaint['id']}")
                                action_image = st.file_uploader("Action Image", 
                                                              type=['jpg', 'jpeg', 'png'],
                                                              key=f"action_img_{complaint['id']}")
                                
                                if st.button("Update Status", key=f"update_{complaint['id']}"):
                                    data = {
                                        "complaint_id": complaint['id'],
                                        "status": new_status,
                                        "statement": statement
                                    }
                                    files = {"image": action_image} if action_image else None
                                    
                                    success, result = make_request("POST", "/municipality/update-complaint-status", data, files)
                                    if success:
                                        st.success("Status updated!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed: {result}")
                    
                    st.markdown("---")
        else:
            st.info("No complaints found or failed to load complaints.")
    
    with tab2:
        st.header("Municipality Feed")
        
        # Staff post creation
        if st.session_state.user.get('role') == 'staff':
            with st.expander("➕ Post Municipality Update", expanded=False):
                with st.form("municipality_post_form"):
                    post_title = st.text_input("Title", placeholder="Infrastructure Project Update")
                    action = st.selectbox("Action Type", ["working", "completed", "planned", "announcement"])
                    statement = st.text_area("Statement", placeholder="Describe the municipality activity...")
                    post_image = st.file_uploader("Upload Image (Optional)", type=['jpg', 'jpeg', 'png'])
                    
                    submit_post = st.form_submit_button("Post Update")
                    
                    if submit_post:
                        if post_title and statement:
                            data = {
                                "title": post_title,
                                "action": action,
                                "statement": statement
                            }
                            files = {"image": post_image} if post_image else None
        
                            success, result = make_request("POST", "/municipality/post-action", data, files)
                            if success:
                                st.success("Municipality post created successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to create post: {result}")
                        else:
                            st.error("Please fill in title and statement")
        
        st.markdown("---")
        
        # Display municipality activities
        st.subheader("Recent Municipality Activities")
        success, activities = make_request("GET", "/municipality/activities")
        
        if success and activities:
            for activity in activities:
                st.markdown(f"""
                <div class="municipality-post">
                    <h4>{activity['title']}</h4>
                    <p><strong>Action:</strong> {activity['action'].title()} | 
                       <strong>Municipality:</strong> {activity.get('municipality', 'N/A')}</p>
                    <p>{activity['statement']}</p>
                    <p><strong>Posted:</strong> {activity['timestamp'][:19]} | 
                       <strong>By Staff ID:</strong> {activity['by']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if activity.get('action_image'):
                    st.image(f"{API_BASE_URL}{activity['action_image']}", width=300)
                
                st.markdown("---")
        else:
            st.info("No municipality activities found.")
        
        # Display municipality data
        st.subheader("Municipality Overview")
        success, municipalities = make_request("GET", "/municipality/")
        
        if success and municipalities:
            for muni in municipalities:
                st.markdown(f"### {muni['municipality']} - {muni['city']}")
                if muni.get('activities'):
                    for act in muni['activities'][-3:]:  # Show last 3 activities
                        st.markdown(f"""
                        <div class="municipality-post">
                            <p><strong>{act['title']}</strong></p>
                            <p>{act['statement']}</p>
                            <small>Status: {act['action']} | {act['timestamp'][:19]}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No recent activities")
    
    with tab3:
        st.header("User Profile")
        
        if st.session_state.user:
            success, user_details = make_request("GET", "/auth/me")
            if success:
                user_info = user_details['current_user']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Phone:** {user_info.get('sub', 'N/A')}")
                    st.markdown(f"**Role:** {user_info.get('role', 'N/A').title()}")
                    st.markdown(f"**User ID:** {user_info.get('id', 'N/A')}")
                
                # Get full user details from users endpoint
                success, all_users = make_request("GET", "/auth/users")
                if success:
                    current_user_details = next((u for u in all_users if u['id'] == user_info['id']), None)
                    if current_user_details:
                        with col2:
                            st.markdown(f"**Name:** {current_user_details.get('name', 'N/A')}")
                            st.markdown(f"**City:** {current_user_details.get('city', 'N/A')}")
                            st.markdown(f"**Municipality:** {current_user_details.get('municipality', 'N/A')}")
                            st.markdown(f"**Ward:** {current_user_details.get('ward', 'N/A')}")
        
        st.markdown("---")
        
        # User's complaints
        st.subheader("My Complaints")
        success, all_complaints = make_request("GET", "/complaints/")
        
        if success and all_complaints:
            user_complaints = [c for c in all_complaints if c['author_id'] == st.session_state.user['id']]
            
            if user_complaints:
                for complaint in user_complaints:
                    st.markdown(f"""
                    <div class="complaint-card">
                        <h4>{complaint['title']}</h4>
                        <p>{complaint['content']}</p>
                        <p><strong>Status:</strong> <span class="status-{complaint['status']}">{complaint['status'].upper()}</span> | 
                           <strong>Upvotes:</strong> <span class="upvote-count">{complaint['upvotes']}</span></p>
                        <p><strong>Created:</strong> {complaint['created_at'][:19]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if complaint.get('image_url'):
                        st.image(f"{API_BASE_URL}{complaint['image_url']}", width=200)
            else:
                st.info("You haven't submitted any complaints yet.")
        
    with tab4:
        st.header("Dashboard & Statistics")
        
        # Get data for dashboard
        success, all_complaints = make_request("GET", "/complaints/")
        success_muni, activities = make_request("GET", "/municipality/activities")
        
        if success and all_complaints:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Complaints", len(all_complaints))
            
            with col2:
                open_complaints = len([c for c in all_complaints if c['status'] == 'open'])
                st.metric("Open Complaints", open_complaints)
            
            with col3:
                working_complaints = len([c for c in all_complaints if c['status'] == 'working'])
                st.metric("In Progress", working_complaints)
            
            with col4:
                completed_complaints = len([c for c in all_complaints if c['status'] == 'completed'])
                st.metric("Completed", completed_complaints)
            
            # Status distribution
            st.subheader("Complaint Status Distribution")
            status_data = {"Open": open_complaints, "Working": working_complaints, "Completed": completed_complaints}
            st.bar_chart(status_data)
            
            # Recent complaints
            st.subheader("Recent Complaints")
            recent_complaints = sorted(all_complaints, key=lambda x: x['created_at'], reverse=True)[:5]
            
            for complaint in recent_complaints:
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 5px;">
                    <strong>{complaint['title']}</strong><br>
                    <small>Status: {complaint['status']} | Upvotes: {complaint['upvotes']} | 
                    Created: {complaint['created_at'][:19]}</small>
                </div>
                """, unsafe_allow_html=True)
        
        if success_muni and activities:
            st.subheader("Recent Municipality Activities")
            recent_activities = sorted(activities, key=lambda x: x['timestamp'], reverse=True)[:5]
            
            for activity in recent_activities:
                st.markdown(f"""
                <div class="municipality-post">
                    <strong>{activity['title']}</strong><br>
                    <p>{activity['statement']}</p>
                    <small>Action: {activity['action']} | Posted: {activity['timestamp'][:19]}</small>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*Hamro Aawaz - Empowering citizens to make their voices heard* 🇳🇵")

# Auto-refresh for real-time updates (optional)
if st.session_state.logged_in:
    # Add a refresh button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        st.markdown(f"*Last updated: {datetime.now().strftime('%H:%M:%S')}*")
