import streamlit as st
import streamlit.components.v1 as components
import streamlit_js_eval
import pandas as pd
import os
from datetime import datetime
from geopy.geocoders import Nominatim

# Constants
IMAGE_FOLDER = "incident_images"
CSV_FILE = "incident_reports.csv"
USER_FILE = "users.csv"

# Ensure image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# User Authentication Functions
def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    else:
        return pd.DataFrame(columns=["username", "password", "role"])

def save_user(username, password, role="user"):
    df = load_users()
    if username in df["username"].values:
        return False  # User already exists
    new_user = pd.DataFrame([[username, password, role]], columns=["username", "password", "role"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)
    return True

def authenticate_user(username, password):
    df = load_users()
    user = df[(df["username"] == username) & (df["password"] == password)]
    if not user.empty:
        return user.iloc[0]["role"]
    return None

# Incident Reporting Functions
def save_incident(username, incident_type, location, auto_location, description, image_filename):
    data = {
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Username": [username],
        "Type": [incident_type],
        "Location": [location],
        "Auto_Location": [auto_location],
        "Description": [description],
        "Image": [image_filename]
    }
    df = pd.DataFrame(data)
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

def load_incidents():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame()

# Main App
def main():
    st.set_page_config(page_title="Incident Report System", layout="centered")
    st.markdown(
        """
        <style>
        .main .block-container {
            max-width: 600px;
            margin: auto;
            padding: 1rem;
        }
        html, body, [class*="css"]  {
            font-size: 16px;
        }
        textarea, input {
            font-size: 16px !important;
        }
        div.stButton > button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #ff4b4b;
            color: white;
            font-size: 16px;
            padding: 12px 24px;
            border-radius: 50px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3);
            z-index: 1000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🚨 Incident Reporting")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

    if not st.session_state.logged_in:
        login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

        with login_tab:
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                role = authenticate_user(username, password)
                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with register_tab:
            st.subheader("Create New Account")
            new_username = st.text_input("New Username", key="new_username")
            new_password = st.text_input("New Password", type="password", key="new_password")
            if st.button("Register"):
                if new_username and new_password:
                    success = save_user(new_username, new_password)
                    if success:
                        st.success("Account created! You can now log in.")
                    else:
                        st.warning("Username already exists.")
                else:
                    st.warning("Please enter both username and password.")
    else:
        st.sidebar.success(f"Logged in as: {st.session_state.username} ({st.session_state.role})")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()

        if st.session_state.role == 'user':
            gps_result = streamlit_js_eval.get_geolocation()

            with st.form("incident_form"):
                st.subheader("📋 Submit Incident Report")
                incident_type = st.selectbox("Incident Type", ["Fire", "Injury", "Chemical Spill", "Other"])
                location = st.text_input("Manual Location (e.g., Block A, Lab 3)")
                description = st.text_area("Describe what happened", height=150)
                uploaded_image = st.file_uploader("Upload a photo (optional)", type=["jpg", "jpeg", "png"])

                if uploaded_image is not None:
                    st.image(uploaded_image, caption="📸 Preview", use_container_width=True)

                submitted = st.form_submit_button("Submit Incident")

            if submitted:
                if location and description:
                    img_filename = ""
                    if uploaded_image:
                        img_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_image.name}"
                        with open(os.path.join(IMAGE_FOLDER, img_filename), "wb") as f:
                            f.write(uploaded_image.getbuffer())

                    auto_location = gps_result or "Unavailable"
                    save_incident(
                        st.session_state.username,
                        incident_type,
                        location,
                        auto_location,
                        description,
                        img_filename
                    )
                    st.success("✅ Incident submitted successfully!")
                else:
                    st.warning("Please fill in all fields.")

        elif st.session_state.role == 'admin':
            st.subheader("📂 Incident Dashboard")
            df = load_incidents()
            st.subheader("👥 Registered Users")

            users_df = load_users()

            if not users_df.empty:
                users_df["password"] = "🔒"  # Mask password
                st.dataframe(users_df)
            else:
                st.info("No registered users found.")

            if df.empty:
                st.info("No incidents have been reported yet.")
            else:
                for _, row in df.iterrows():
                    with st.expander(f"[{row['Timestamp']}] {row['Type']} by {row['Username']}"):
                        st.markdown(f"**Manual Location:** {row['Location']}")
                        st.markdown(f"**Detected Location:** {row['Auto_Location']}")
                        st.markdown(f"**Description:** {row['Description']}")
                        if row['Image']:
                            img_path = os.path.join(IMAGE_FOLDER, row['Image'])
                            if os.path.exists(img_path):
                                st.image(img_path, caption="Attached Image", use_container_width=True)

                st.download_button("⬇ Download Reports (CSV)", data=df.to_csv(index=False),
                                   file_name="incident_reports.csv")

if __name__ == "__main__":
    main()
