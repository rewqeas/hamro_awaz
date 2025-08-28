import streamlit as st
import datetime
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict
import uuid

# Data structures
@dataclass
class Complaint:
    id: str
    title: str
    description: str
    complaint_type: str
    timestamp: datetime.datetime
    upvotes: int = 0
    status: str = "submitted"
    municipality_update: str = ""
    rejection_reason: str = ""

# Page config - Full width layout
st.set_page_config(page_title="Hamro Aawaz - Civic Alert Dashboard", layout="wide")

# Custom CSS styling
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tab button style */
    .tab-button {
        display: inline-block;
        width: 23%;       /* Each tab ~1/4 width with spacing */
        height: 80px;     /* Increased height */
        text-align: center;
        padding-top: 20px;
        margin: 0.5%;
        font-size: 20px;
        font-weight: bold;
        cursor: pointer;
        border-radius: 10px;
        color: white;
        border: none;
    }
    .tab-red {background-color: #FF0000;}
    .tab-orange {background-color: #FF8C00;}
    .tab-green {background-color: #28a745; color:white;}
    .tab-blue {background-color: #007bff; color:white;}
    .tab-gold {background-color: #FFD700; color:black;}
    .tab-button:hover {
        opacity: 0.8;
    }
    .active {
        border: 3px solid #000000;
    }
    
    /* Complaint box styling */
    .complaint-box {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        border: 2px solid #007bff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        z-index: 1000;
        width: 400px;
    }
    .complaint-toggle {
        position: fixed;
        bottom: 20px;
        right: 30px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 1001;
    }
    .complaint-toggle:hover {
        background: #0056b3;
    }
    
    /* Alert cards */
    .alert-card {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid;
    }
    .high-alert {
        background-color: #ffe6e6;
        border-left-color: #FF0000;
    }
    .mid-alert {
        background-color: #fff3e0;
        border-left-color: #FF8C00;
    }
    .low-alert {
        background-color: #e8f5e8;
        border-left-color: #28a745;
    }
    .security-badge {
        background-color: #dc3545;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize session state
if 'complaints' not in st.session_state:
    st.session_state.complaints = []
if 'user_votes' not in st.session_state:
    st.session_state.user_votes = set()
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Red Alert"
if "show_complaint_form" not in st.session_state:
    st.session_state.show_complaint_form = False
if 'honours_list' not in st.session_state:
    st.session_state.honours_list = [
        {"title": "Community Champion", "recipient": "Ward 5 Residents", "description": "Outstanding community participation in waste management", "date": "2024-08-15"},
        {"title": "Safety Hero", "recipient": "Local Security Team", "description": "Quick response to security concerns", "date": "2024-08-10"},
        {"title": "Infrastructure Advocate", "recipient": "Youth Group", "description": "Successful road repair campaign", "date": "2024-08-05"},
    ]
if 'pending_complaints' not in st.session_state:
    st.session_state.pending_complaints = []  # Complaints waiting for verification

def get_alert_level(upvotes):
    if upvotes >= 50:
        return "🔴 High Alert"
    elif upvotes >= 35:
        return "🟠 Mid Alert"
    else:
        return "🟢 Low Alert"

def get_alert_class(upvotes):
    if upvotes >= 50:
        return "high-alert"
    elif upvotes >= 35:
        return "mid-alert"
    else:
        return "low-alert"

def add_complaint(title, description, complaint_type, photo=None):
    complaint = Complaint(
        id=str(uuid.uuid4())[:8],
        title=title,
        description=description,
        complaint_type=complaint_type,
        timestamp=datetime.datetime.now()
    )
    if photo:
        complaint.photo = photo.name
    
    st.session_state.complaints.append(complaint)
    return complaint

def set_tab(tab_name):
    st.session_state.active_tab = tab_name

# App title
st.markdown("<h1 style='text-align:center; color:#2c3e50; font-size:3em;'>🗣️ Hamro Aawaz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666; font-size:1.2em; margin-top:-20px;'>हाम्रो आवाज - Our Voice for Better Community</p>", unsafe_allow_html=True)

# Tab definitions with updated descriptions
tab_data = [
    {"name": "Red Alert", "class": "tab-red", "description": "High Priority Issues (50+ votes)"},
    {"name": "Orange Alert", "class": "tab-orange", "description": "Medium Priority Issues (35-49 votes)"},
    {"name": "Green Alert", "class": "tab-green", "description": "Low Priority Issues (0-34 votes)"},
    {"name": "Honours", "class": "tab-gold", "description": "Community Recognition & Achievements"},
]

# Display tabs as clickable buttons
cols = st.columns(len(tab_data))
for i, tab in enumerate(tab_data):
    # Check if active
    is_active = st.session_state.active_tab == tab["name"]
    button_style = f"{tab['class']} active" if is_active else tab["class"]
    
    if cols[i].button(tab["name"], key=tab["name"]):
        set_tab(tab["name"])

# Submit Complaint Button - positioned prominently
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("📝 Submit Complaint", key="main_submit_button", type="primary", use_container_width=True):
        st.session_state.show_complaint_form = not st.session_state.show_complaint_form

# Complaint Form Modal (shown when button is clicked)
if st.session_state.show_complaint_form:
    st.markdown("---")
    st.markdown("<h2 style='text-align:center; color:#007bff; font-size:2em;'>📝 Submit Your Complaint</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>Your voice matters! Report issues to help improve our community.</p>", unsafe_allow_html=True)
    
    # Centered complaint form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("complaint_form", clear_on_submit=True):
            st.markdown("### 📋 Complaint Details")
            
            complaint_title = st.text_input("🏷️ Complaint Title", placeholder="Brief title for your complaint")
            
            complaint_desc = st.text_area(
                "📝 Description", 
                height=120,
                placeholder="Describe the issue in detail. Include location, time, and any relevant information."
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                complaint_type = st.selectbox(
                    "📂 Complaint Type:",
                    ["Security", "Infrastructure", "Sanitation", "Miscellaneous"],
                    help="Select the category that best describes your complaint"
                )
            
            with col_b:
                # Photo upload feature
                uploaded_photo = st.file_uploader(
                    "📷 Add Photo (Optional)",
                    type=['png', 'jpg', 'jpeg'],
                    help="Upload a photo if it helps illustrate the issue"
                )
            
            # Display uploaded photo preview
            if uploaded_photo is not None:
                st.image(uploaded_photo, caption="Uploaded Photo", width=300)
            
            st.markdown("---")
            
            # Form buttons
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                submitted = st.form_submit_button("🚀 Submit Complaint", type="primary", use_container_width=True)
            
            with col_cancel:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_complaint_form = False
                    st.rerun()
            
            if submitted:
                if complaint_title and complaint_desc:
                    complaint = add_complaint(complaint_title, complaint_desc, complaint_type, uploaded_photo)
                    
                    if complaint_type == "Security":
                        st.success("🚨 Security issue submitted! This will be given high priority and immediately visible to authorities.")
                    else:
                        st.success("✅ Complaint submitted successfully! Community members can now vote on your issue.")
                    
                    st.balloons()
                    st.session_state.show_complaint_form = False
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in both title and description to submit your complaint.")

# Separator
st.markdown("<hr style='border:2px solid #34495e;'>", unsafe_allow_html=True)

# Get complaints by alert level
def get_complaints_by_alert_level(level):
    active_complaints = [c for c in st.session_state.complaints if c.status != "rejected"]
    if level == "high":
        return [c for c in active_complaints if c.upvotes >= 50]
    elif level == "mid":
        return [c for c in active_complaints if 35 <= c.upvotes <= 49]
    else:  # low
        return [c for c in active_complaints if c.upvotes < 35]

# Display content based on active tab
if st.session_state.active_tab == "Red Alert":
    st.markdown("<h2 style='color:#FF0000; text-align:center; font-size:2.5em;'>🚨 Red Alert - High Priority Issues</h2>", unsafe_allow_html=True)
    
    high_alert_complaints = get_complaints_by_alert_level("high")
    
    if not high_alert_complaints:
        st.markdown("<div style='text-align:center; font-size:1.5em; color:#666; margin:50px 0;'>✅ No high priority alerts currently</div>", unsafe_allow_html=True)
        st.image("https://via.placeholder.com/1600x300/28a745/FFFFFF?text=All+Clear+-+No+High+Priority+Issues", use_column_width=True)
    else:
        st.markdown(f"<div style='text-align:center; font-size:1.2em; color:#FF0000; margin:20px 0;'>⚠️ {len(high_alert_complaints)} Critical Issues Requiring Immediate Attention</div>", unsafe_allow_html=True)
        for complaint in sorted(high_alert_complaints, key=lambda x: x.upvotes, reverse=True):
            st.markdown(f"""
            <div class='alert-card high-alert'>
                <h3>🚨 {complaint.title}</h3>
                {'<span class="security-badge">🔒 SECURITY ISSUE</span>' if complaint.complaint_type == 'Security' else ''}
                <p><strong>Description:</strong> {complaint.description}</p>
                <p><strong>Type:</strong> {complaint.complaint_type} | <strong>Upvotes:</strong> {complaint.upvotes} | <strong>Submitted:</strong> {complaint.timestamp.strftime('%Y-%m-%d %H:%M')}</p>
                {f'<p style="background:#fff3cd; padding:10px; border-radius:5px;"><strong>📢 Municipality Update:</strong> {complaint.municipality_update}</p>' if complaint.municipality_update else ''}
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.active_tab == "Orange Alert":
    st.markdown("<h2 style='color:#FF8C00; text-align:center; font-size:2.5em;'>🟠 Orange Alert - Medium Priority Issues</h2>", unsafe_allow_html=True)
    
    mid_alert_complaints = get_complaints_by_alert_level("mid")
    
    if not mid_alert_complaints:
        st.markdown("<div style='text-align:center; font-size:1.5em; color:#666; margin:50px 0;'>📋 No medium priority alerts currently</div>", unsafe_allow_html=True)
        st.image("https://via.placeholder.com/1600x300/FF8C00/FFFFFF?text=No+Medium+Priority+Issues", use_column_width=True)
    else:
        st.markdown(f"<div style='text-align:center; font-size:1.2em; color:#FF8C00; margin:20px 0;'>⚡ {len(mid_alert_complaints)} Issues Need Community Support</div>", unsafe_allow_html=True)
        for complaint in sorted(mid_alert_complaints, key=lambda x: x.upvotes, reverse=True):
            st.markdown(f"""
            <div class='alert-card mid-alert'>
                <h3>🟠 {complaint.title}</h3>
                {'<span class="security-badge">🔒 SECURITY ISSUE</span>' if complaint.complaint_type == 'Security' else ''}
                <p><strong>Description:</strong> {complaint.description}</p>
                <p><strong>Type:</strong> {complaint.complaint_type} | <strong>Upvotes:</strong> {complaint.upvotes} | <strong>Submitted:</strong> {complaint.timestamp.strftime('%Y-%m-%d %H:%M')}</p>
                {f'<p style="background:#fff3cd; padding:10px; border-radius:5px;"><strong>📢 Municipality Update:</strong> {complaint.municipality_update}</p>' if complaint.municipality_update else ''}
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.active_tab == "Green Alert":
    st.markdown("<h2 style='color:#28a745; text-align:center; font-size:2.5em;'>🟢 Green Alert - Community Feed</h2>", unsafe_allow_html=True)
    
    low_alert_complaints = get_complaints_by_alert_level("low")
    
    if not low_alert_complaints:
        st.markdown("<div style='text-align:center; font-size:1.5em; color:#666; margin:50px 0;'>📝 No complaints yet. Be the first to submit one!</div>", unsafe_allow_html=True)
        st.image("https://via.placeholder.com/1600x300/28a745/FFFFFF?text=Community+Feed+-+Submit+Your+First+Complaint", use_column_width=True)
    else:
        st.markdown("<h3>Community complaints that need your support! 👍</h3>")
        st.markdown(f"<div style='text-align:center; font-size:1.1em; color:#28a745; margin:20px 0;'>🌱 {len(low_alert_complaints)} Community Issues - Help them grow!</div>", unsafe_allow_html=True)
        
        for complaint in sorted(low_alert_complaints, key=lambda x: x.timestamp, reverse=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class='alert-card low-alert'>
                    <h4>🟢 {complaint.title}</h4>
                    {'<span class="security-badge">🔒 SECURITY ISSUE</span>' if complaint.complaint_type == 'Security' else ''}
                    <p><strong>Description:</strong> {complaint.description}</p>
                    <p><strong>Type:</strong> {complaint.complaint_type} | <strong>Upvotes:</strong> {complaint.upvotes} | <strong>Submitted:</strong> {complaint.timestamp.strftime('%Y-%m-%d %H:%M')}</p>
                    {f'<p style="background:#fff3cd; padding:10px; border-radius:5px;"><strong>📢 Municipality Update:</strong> {complaint.municipality_update}</p>' if complaint.municipality_update else ''}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                vote_key = f"vote_{complaint.id}"
                if complaint.id not in st.session_state.user_votes:
                    if st.button("👍 Upvote", key=vote_key, use_container_width=True):
                        complaint.upvotes += 1
                        st.session_state.user_votes.add(complaint.id)
                        st.rerun()
                else:
                    st.success("✅ Voted")

elif st.session_state.active_tab == "Honours":
    st.markdown("<h2 style='color:#FFD700; text-align:center; font-size:2.5em;'>🏆 Honours - Community Recognition</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:1.2em; color:#666;'>Celebrating our community heroes and successful initiatives</p>", unsafe_allow_html=True)
    
    # Display honours in a grid
    cols = st.columns(2)
    for i, honour in enumerate(st.session_state.honours_list):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #fff3cd, #ffeaa7); border-radius: 15px; padding: 20px; margin: 10px 0; border-left: 5px solid #FFD700;'>
                <h3 style='color: #d68910; margin-bottom: 10px;'>🏆 {honour['title']}</h3>
                <p><strong style='color: #8e44ad;'>Recipient:</strong> {honour['recipient']}</p>
                <p><strong style='color: #27ae60;'>Achievement:</strong> {honour['description']}</p>
                <p style='color: #7f8c8d; font-size: 0.9em;'><strong>Date:</strong> {honour['date']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add new honour section (for municipality)
    st.markdown("---")
    st.markdown("### 🎖️ Add New Honour (Municipality Only)")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.form("add_honour_form"):
            honour_title = st.text_input("Honour Title")
            honour_recipient = st.text_input("Recipient")
            honour_description = st.text_area("Achievement Description", height=80)
            
            if st.form_submit_button("🏆 Add Honour", type="primary"):
                if honour_title and honour_recipient and honour_description:
                    new_honour = {
                        "title": honour_title,
                        "recipient": honour_recipient,
                        "description": honour_description,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.honours_list.insert(0, new_honour)
                    st.success("🎉 New honour added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all fields.")
    
    with col2:
        st.markdown("#### 📊 Community Impact")
        total_complaints = len(st.session_state.complaints)
        resolved_complaints = len([c for c in st.session_state.complaints if c.municipality_update])
        total_honours = len(st.session_state.honours_list)
        
        st.metric("Total Complaints", total_complaints)
        st.metric("Addressed Issues", resolved_complaints)
        st.metric("Honours Awarded", total_honours)

# Municipality Dashboard (simplified, moved to bottom)
with st.expander("🏛️ Municipality Dashboard (Admin Only)", expanded=False):
    if st.session_state.complaints:
        st.markdown("### Recent Complaints Management")
        
        for complaint in st.session_state.complaints[-5:]:  # Show last 5
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{complaint.title}** ({get_alert_level(complaint.upvotes)})")
                    st.write(f"Type: {complaint.complaint_type} | Votes: {complaint.upvotes}")
                
                with col2:
                    update_key = f"quick_update_{complaint.id}"
                    if st.button("📝 Update", key=update_key):
                        complaint.municipality_update = "Under review by authorities"
                        complaint.status = "in_progress"
                        st.success("Updated!")
                        st.rerun()
        
        # Quick stats
        st.markdown("### 📊 Quick Statistics")
        total_complaints = len(st.session_state.complaints)
        security_issues = len([c for c in st.session_state.complaints if c.complaint_type == "Security"])
        high_alerts = len([c for c in st.session_state.complaints if c.upvotes > 35])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", total_complaints)
        col2.metric("Security", security_issues)
        col3.metric("High Alert", high_alerts)
    else:
        st.info("No complaints submitted yet.")

# Footer
st.markdown("<hr style='border:2px solid #34495e; margin-top:50px;'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#666; font-size:1.1em;'>🗣️ Hamro Aawaz - हाम्रो आवाज | Empowering Communities Through Digital Participation</div>", unsafe_allow_html=True)
