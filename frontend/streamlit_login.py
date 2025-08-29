import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"   # FastAPI backend

st.set_page_config(page_title="Hamro Aawaz - Citizen-Municipality App", layout="wide")

# ------------------- SESSION STATE ------------------- #
# Initialize session state variables
for key, default_value in {
    "token": None,
    "role": None,
    "user_id": None,
    "municipality": None,
    "complaints_page": 0,
    "activities_page": 0,
    "items_per_page": 5,
    "sort_by": "newest",
    "filter_by": "all",
    "search_query": "",
    "loading": False,
    "last_refresh": None,
    "cached_complaints": None,
    "cached_activities": None,
    "cache_duration": 60,  # seconds
    "show_success": False,
    "success_message": "",
    "active_tab": "green"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# CSS for loading animation and notifications
st.markdown("""
<style>
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    .loading {
        animation: pulse 1.5s infinite;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #10b981;
        color: white;
        margin: 1rem 0;
        animation: fadeOut 3s forwards;
    }
    @keyframes fadeOut {
        0% { opacity: 1; }
        90% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; }
    }
    .complaint-card {
        transition: transform 0.2s;
    }
    .complaint-card:hover {
        transform: translateY(-2px);
    }
    .tab-content {
        padding: 1rem;
        border-radius: 0.5rem;
        background: rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# ------------------- HELPERS ------------------- #
def login(phone, password):
    try:
        resp = requests.post(f"{API_URL}/auth/login", json={"phone": phone, "password": password})
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            user_resp = requests.get(f"{API_URL}/auth/me", headers=headers)
            if user_resp.status_code == 200:
                user_data = user_resp.json()["current_user"]
                return token, user_data["role"], user_data["id"]
        st.error(resp.json().get("detail", "Invalid credentials"))
    except Exception as e:
        st.error(f"Error: {e}")
    return None, None, None

def register_user(name, phone, password, role, city, municipality, ward):
    try:
        users_resp = requests.get(f"{API_URL}/auth/users")
        if users_resp.status_code == 200:
            users = users_resp.json()
            new_id = max([u.get("id", 0) for u in users], default=0) + 1
        else:
            new_id = 1000

        resp = requests.post(f"{API_URL}/auth/register", json={
            "id": new_id,
            "name": name,
            "phone": phone,
            "password": password,
            "role": role,
            "city": city,
            "municipality": municipality,
            "ward": ward
        })
        if resp.status_code == 200:
            st.success("Registration successful! Please login.")
        else:
            st.error(resp.json().get("detail", "Registration failed"))
    except Exception as e:
        st.error(f"Error: {e}")

def logout():
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.user_id = None
    st.success("Logged out!")

def submit_complaint(title, content, image_file=None):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    files, data = {}, {"title": title, "content": content}
    if image_file:
        files["image"] = (image_file.name, image_file.getvalue(), image_file.type)
    return requests.post(f"{API_URL}/complaints/", data=data, files=files, headers=headers)

def fetch_complaints():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    resp = requests.get(f"{API_URL}/complaints/", headers=headers)
    return resp.json() if resp.status_code == 200 else []

def upvote_complaint(complaint_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    return requests.post(f"{API_URL}/complaints/{complaint_id}/upvote", headers=headers)

def unvote_complaint(complaint_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    return requests.post(f"{API_URL}/complaints/{complaint_id}/unvote", headers=headers)

def fetch_municipality_activities():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    resp = requests.get(f"{API_URL}/municipality/activities", headers=headers)
    return resp.json() if resp.status_code == 200 else []

def get_all_municipalities():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    resp = requests.get(f"{API_URL}/municipality/", headers=headers)
    return resp.json() if resp.status_code == 200 else []

def post_municipality_action(title, action, statement=None, image_file=None):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    files = {}
    data = {
        "title": title,
        "action": action,
        "statement": statement
    }
    if image_file:
        files["image"] = (image_file.name, image_file.getvalue(), image_file.type)
    return requests.post(
        f"{API_URL}/municipality/post-action",
        data=data,
        files=files,
        headers=headers
    )

def update_complaint_status(complaint_id, status, statement=None, image_file=None):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    files = {}
    data = {
        "complaint_id": complaint_id,
        "status": status,
        "statement": statement
    }
    if image_file:
        files["image"] = (image_file.name, image_file.getvalue(), image_file.type)
    return requests.post(
        f"{API_URL}/municipality/update-complaint-status",
        data=data,
        files=files,
        headers=headers
    )

def calculate_municipality_score(municipalities):
    scores = {m["municipality"]: 0 for m in municipalities}
    for muni in municipalities:
        for activity in muni.get("activities", []):
            if activity.get("action") == "Marked as completed":
                scores[muni["municipality"]] += 2
            elif activity.get("action") in ["working", "Marked as working"]:
                scores[muni["municipality"]] += 1
    return scores

def display_complaint_card(c, show_voting=True, show_status=False):
    """Display a complaint card with consistent styling"""
    status_color = "green" if c.get('status') == "completed" else "orange" if c.get('status') == "working" else "#333"
    upvotes = c.get('upvotes', 0)
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%); 
                border: 2px solid {status_color}; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 10px 0;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);'>
        <h4 style='color: white; margin-bottom: 8px;'>{c['title']}</h4>
        <p style='color: #cccccc; margin-bottom: 10px;'>{c['content']}</p>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <small style='color: #888;'>📅 {c['created_at'][:10]} | 🏠 {c.get('municipality', 'Unknown')} - Ward {c.get('ward', 'N/A')}</small>
            <span style='background: #ff6b6b; color: white; padding: 4px 8px; border-radius: 15px; font-size: 12px;'>👍 {upvotes}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if c.get("image_url"):
        try:
            img_url = f"{API_URL}{c['image_url']}"
            st.image(img_url, caption="Complaint Image", use_container_width=True)
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
    
    if show_voting and st.session_state.role == "citizen":
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"👍 Upvote", key=f"up_{c['id']}_{show_status}"):
                resp = upvote_complaint(c["id"])
                if resp.status_code == 200:
                    st.success("Upvoted!")
                    st.rerun()
        with col2:
            if st.button("👎 Unvote", key=f"un_{c['id']}_{show_status}"):
                resp = unvote_complaint(c["id"])
                if resp.status_code == 200:
                    st.info("Unvoted")
                    st.rerun()
    
    if show_status and st.session_state.role == "staff":
        with st.expander(f"Update Status - {c['title']}"):
            status = st.selectbox("Update Status", ["working", "completed"], key=f"status_{c['id']}")
            statement = st.text_area("Add Statement", key=f"stmt_{c['id']}")
            image_file = st.file_uploader("Upload Action Image", type=["jpg", "jpeg", "png"], key=f"img_{c['id']}")
            if st.button("Update Status", key=f"update_{c['id']}"):
                resp = update_complaint_status(c['id'], status, statement, image_file)
                if resp.status_code == 200:
                    st.success("Status updated successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {resp.text}")

def display_activity_card(activity):
    """Display a municipality activity card"""
    # Define status color based on action
    action_color = "#10b981" if "completed" in activity.get('action', '').lower() else "#f59e0b" if "working" in activity.get('action', '').lower() else "#60a5fa"
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
                border: 2px solid {action_color}; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 10px 0;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <h4 style='color: white; margin-bottom: 8px; flex: 1;'>{activity['title']}</h4>
            <span style='background: {action_color}; color: white; padding: 4px 8px; border-radius: 15px; font-size: 12px;'>
                {activity.get('action', 'Update')}
            </span>
        </div>
        {f"<p style='color: #e0f2fe; margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;'>{activity['statement']}</p>" if activity.get('statement') else ''}
        <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px;'>
            <small style='color: #81d4fa;'>📅 {activity['timestamp'][:10]}</small>
            <small style='color: #81d4fa; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 10px;'>
                🏛️ {activity.get('municipality', 'Unknown')}
            </small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display image after the card if it exists
    if activity.get("action_image"):
        try:
            img_url = f"{API_URL}{activity['action_image']}"
            # Instead of downloading the image, use the URL directly
            st.image(img_url, caption="Activity Image", use_container_width=True)
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
            st.write(f"Image URL attempted: {img_url}")
    
    if activity.get("action_image"):
        try:
            img_url = f"{API_URL}{activity['action_image']}"
            st.image(img_url, caption="Activity Image", use_container_width=True)
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")

# ------------------- MAIN UI ------------------- #
# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #1a1a2e;
        color: white;
    }
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #16213e 100%);
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    .alert-section {
        margin: 20px 0;
        padding: 20px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.token:
    # Login/Register Interface with Nepali support
    st.markdown("""
    <div style='text-align: center; padding: 50px 0;'>
        <h1 style='font-size: 3rem; background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>
            🗣️ हाम्रो आवाज
        </h1>
        <p style='font-size: 1.2rem; color: #888; margin-bottom: 20px;'>
            नागरिक र नगरपालिकाको आवाज
        </p>
        <p style='font-size: 1rem; color: #666; margin-bottom: 40px;'>
            A Platform for Citizens and Municipality Collaboration
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 लग-इन / Login", "📝 दर्ता / Register"])
    with tab1:
        st.subheader("Login")
        phone = st.text_input("Phone Number", key="login_phone")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            token, role, user_id = login(phone, password)
            if token:
                st.session_state.token = token
                st.session_state.role = role
                st.session_state.user_id = user_id
                st.rerun()

    with tab2:
        st.subheader("Register New Account")
        with st.form("register_form"):
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["citizen", "staff"])
            city = st.text_input("City")
            municipality = st.text_input("Municipality")
            ward = st.text_input("Ward Number")
            if st.form_submit_button("Register", use_container_width=True):
                register_user(name, phone, password, role, city, municipality, ward)

else:
    # Main Dashboard Header
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='font-size: 2.5rem; background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px;'>
                🗣️ Hamro Aawaz
            </h1>
            <p style='font-size: 1rem; color: #888;'>
                हाम्रो आवाज - Our Voice for Better Community
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<p style='color: #888; text-align: right; padding-top: 20px;'>Logged in as: <strong>{st.session_state.role}</strong></p>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Navigation Menu with Nepali translations
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h3 style='text-align: center; color: #fff; margin-bottom: 15px;'>मुख्य मेनु / Main Menu</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin: 5px;'>
            <h4 style='color: #fff; margin-bottom: 10px;'>गुनासो श्रेणीहरू / Complaint Categories</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔴 उच्च प्राथमिकता / High Priority", use_container_width=True, type="secondary"):
            st.markdown('<script>document.getElementById("red-alert").scrollIntoView();</script>', unsafe_allow_html=True)
        if st.button("🟠 मध्यम प्राथमिकता / Medium Priority", use_container_width=True, type="secondary"):
            st.markdown('<script>document.getElementById("orange-alert").scrollIntoView();</script>', unsafe_allow_html=True)
        if st.button("🟢 सामान्य प्राथमिकता / Normal Priority", use_container_width=True, type="secondary"):
            st.markdown('<script>document.getElementById("green-alert").scrollIntoView();</script>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin: 5px;'>
            <h4 style='color: #fff; margin-bottom: 10px;'>अन्य जानकारी / Other Information</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("�️ नगरपालिका अपडेट / Municipality Updates", use_container_width=True, type="secondary"):
            st.markdown('<script>document.getElementById("muni-updates").scrollIntoView();</script>', unsafe_allow_html=True)
        if st.button("🏆 उत्कृष्ट नगरपालिका / Top Municipalities", use_container_width=True, type="secondary"):
            st.markdown('<script>document.getElementById("leaderboard").scrollIntoView();</script>', unsafe_allow_html=True)

    # Fetch data
    complaints = fetch_complaints()
    municipality_activities = fetch_municipality_activities()
    municipalities = get_all_municipalities()
    
    # Sort complaints by upvotes
    complaints.sort(key=lambda x: x.get('upvotes', 0), reverse=True)
    
    # Categorize complaints
    low_priority = [c for c in complaints if c.get('upvotes', 0) < 15]
    mid_priority = [c for c in complaints if 15 <= c.get('upvotes', 0) < 35]
    high_priority = [c for c in complaints if c.get('upvotes', 0) >= 35]
    
    st.markdown("---")
    
    # SECTION 1: GREEN ALERT - Low Priority Issues
    st.markdown("<div id='green-alert'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='alert-section'>
        <h2 style='color: #10b981; text-align: center; margin-bottom: 10px;'>
            🟢 सामान्य प्राथमिकता / Normal Priority
        </h2>
        <p style='text-align: center; color: #888; margin-bottom: 20px; font-size: 0.9rem;'>
            समस्याहरू जसमा कम मात्रामा मत छन् (०-१५ मत) / Issues with low votes (0-15 upvotes)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if low_priority:
        for complaint in low_priority[:5]:  # Show top 5
            display_complaint_card(complaint, show_voting=True)
    else:
        st.markdown("<p style='text-align: center; color: #10b981;'>✅ No low priority alerts currently</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECTION 2: ORANGE ALERT - Mid Priority Issues
    st.markdown("<div id='orange-alert'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='alert-section'>
        <h2 style='color: #f59e0b; text-align: center; margin-bottom: 10px;'>
            🟠 मध्यम प्राथमिकता / Medium Priority
        </h2>
        <p style='text-align: center; color: #888; margin-bottom: 20px; font-size: 0.9rem;'>
            बढ्दो चिन्ताका विषयहरू (१५-३५ मत) / Growing concerns (15-35 upvotes)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if mid_priority:
        for complaint in mid_priority:
            display_complaint_card(complaint, show_voting=True)
    else:
        st.markdown("<p style='text-align: center; color: #f59e0b;'>✅ No medium priority alerts currently</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECTION 3: RED ALERT - High Priority Issues
    st.markdown("<div id='red-alert'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='alert-section'>
        <h2 style='color: #ef4444; text-align: center; margin-bottom: 10px;'>
            🚨 उच्च प्राथमिकता / High Priority
        </h2>
        <p style='text-align: center; color: #888; margin-bottom: 20px; font-size: 0.9rem;'>
            तत्काल ध्यान दिनुपर्ने समस्याहरू (३५+ मत) / Urgent issues (35+ upvotes)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if high_priority:
        for complaint in high_priority:
            display_complaint_card(complaint, show_voting=True)
    else:
        st.markdown("<p style='text-align: center; color: #10b981;'>✅ No high priority alerts currently</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECTION 4: Municipality Updates Feed
    st.markdown("<div id='muni-updates'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='alert-section'>
        <h2 style='color: #3b82f6; text-align: center; margin-bottom: 10px;'>
            🏛️ नगरपालिका अपडेट / Municipality Updates
        </h2>
        <p style='text-align: center; color: #888; margin-bottom: 20px; font-size: 0.9rem;'>
            नगरपालिकाका पछिल्ला गतिविधिहरू / Latest municipality activities
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if municipality_activities:
        for activity in municipality_activities[:10]:  # Show latest 10 activities
            display_activity_card(activity)
    else:
        st.markdown("<p style='text-align: center; color: #888;'>No municipality updates currently</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECTION 5: Municipality Leaderboard
    st.markdown("<div id='leaderboard'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='alert-section'>
        <h2 style='color: #ffd700; text-align: center; margin-bottom: 10px;'>
            🏆 उत्कृष्ट नगरपालिका / Top Municipalities
        </h2>
        <p style='text-align: center; color: #888; margin-bottom: 20px; font-size: 0.9rem;'>
            सर्वोत्कृष्ट कार्य गर्ने नगरपालिकाहरू / Best performing municipalities
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate scores and display leaderboard
    municipality_scores = calculate_municipality_score(municipalities)
    sorted_municipalities = sorted(municipality_scores.items(), key=lambda x: x[1], reverse=True)
    
    leaderboard_cols = st.columns(3)
    for idx, (muni, score) in enumerate(sorted_municipalities):
        col_idx = idx % 3
        with leaderboard_cols[col_idx]:
            medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "🏅"
            rank_color = "#ffd700" if idx == 0 else "#c0c0c0" if idx == 1 else "#cd7f32" if idx == 2 else "#888"
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(255,215,0,0.1) 0%, rgba(255,215,0,0.05) 100%); 
                        border: 2px solid {rank_color}; 
                        padding: 15px; 
                        border-radius: 10px; 
                        margin: 10px 0; 
                        text-align: center;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);'>
                <div style='font-size: 2rem; margin-bottom: 5px;'>{medal}</div>
                <h4 style='color: {rank_color}; margin-bottom: 5px;'>#{idx + 1}</h4>
                <p style='color: white; margin-bottom: 5px;'>{muni}</p>
                <span style='background: {rank_color}; color: black; padding: 4px 8px; border-radius: 15px; font-size: 12px; font-weight: bold;'>
                    {score} points
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action Button Section
    if st.session_state.role == "citizen":
        # Submit Complaint Button
        st.markdown("""
        <div style='text-align: center; margin: 30px 0;'>
            <h3 style='color: #ff6b6b; margin-bottom: 20px;'>📝 नयाँ गुनासो दर्ता / Report New Issue</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("➕ नयाँ गुनासो दर्ता गर्नुहोस् / Submit a New Complaint", expanded=False):
            with st.form("complaint_form"):
                title = st.text_input("Complaint Title")
                content = st.text_area("Complaint Content")
                image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
                if st.form_submit_button("🚀 Submit Complaint", use_container_width=True):
                    if title and content:
                        resp = submit_complaint(title, content, image_file)
                        if resp.status_code == 200:
                            st.success("✅ Complaint submitted successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed: {resp.text}")
                    else:
                        st.warning("Please fill in all required fields!")
    
    elif st.session_state.role == "staff":
        # Post Municipality Activity Button
        st.markdown("""
        <div style='text-align: center; margin: 30px 0;'>
            <h3 style='color: #3b82f6; margin-bottom: 20px;'>🏛️ नगरपालिका अपडेट / Municipality Update</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📢 नयाँ नगरपालिका गतिविधि / Post New Municipality Activity", expanded=False):
            with st.form("municipality_form"):
                title = st.text_input("Activity Title")
                action = st.selectbox("Action Type", ["working", "completed"])
                statement = st.text_area("Statement (Optional)")
                image_file = st.file_uploader("Action Image (Optional)", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("🚀 Post Update", use_container_width=True):
                    if title:
                        resp = post_municipality_action(title, action, statement, image_file)
                        if resp.status_code == 200:
                            st.success("✅ Municipality update posted successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {resp.text}")
                    else:
                        st.warning("Please provide a title for the activity!")