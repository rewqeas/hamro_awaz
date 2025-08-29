import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"   # FastAPI backend

st.title("📢 Submit & View Complaints")

# ------------------- SESSION STATE ------------------- #
if "token" not in st.session_state:
    st.session_state.token = None

# ------------------- HELPERS ------------------- #
def submit_complaint(title, content):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    resp = requests.post(
        f"{API_URL}/complaints/",
        json={"title": title, "content": content},
        headers=headers
    )
    return resp

def fetch_complaints():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    resp = requests.get(f"{API_URL}/complaints/", headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return []

def upvote_complaint(complaint_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    resp = requests.post(f"{API_URL}/complaints/{complaint_id}/upvote", headers=headers)
    return resp

# ------------------- COMPLAINT FORM ------------------- #
with st.form("complaint_form"):
    st.subheader("📝 Submit New Complaint")
    title = st.text_input("Complaint Title")
    content = st.text_area("Complaint Details")
    submit_btn = st.form_submit_button("Submit Complaint")

    if submit_btn:
        if not st.session_state.token:
            st.error("Please login first.")
        elif title and content:
            resp = submit_complaint(title, content)
            if resp.status_code == 200:
                st.success("Complaint submitted successfully!")
            else:
                st.error(resp.json().get("detail", "Error submitting complaint"))
        else:
            st.warning("Please provide both Title and Content.")

# ------------------- DISPLAY COMPLAINTS ------------------- #
st.markdown("---")
st.subheader("📊 Community Complaints (sorted by upvotes)")

complaints = fetch_complaints()
if complaints:
    # Sort complaints by upvotes (descending)
    complaints = sorted(complaints, key=lambda x: x["upvotes"], reverse=True)

    for c in complaints:
        with st.container():
            st.markdown(f"### {c['title']}")
            st.write(c["content"])
            st.caption(f"Submitted by Ward {c['ward']} | Upvotes: {c['upvotes']}")
            if st.button(f"👍 Upvote ({c['upvotes']})", key=f"up_{c['id']}"):
                resp = upvote_complaint(c["id"])
                if resp.status_code == 200:
                    st.success("Upvoted!")
                    st.rerun()
                else:
                    st.error(resp.json().get("detail", "Error"))
            st.markdown("---")
else:
    st.info("No complaints yet. Be the first to submit one!")
