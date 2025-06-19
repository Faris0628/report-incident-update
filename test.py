import streamlit as st
import streamlit.components.v1 as components
import streamlit_js_eval
import pandas as pd
import os
import base64
from datetime import datetime
from geopy.geocoders import Nominatim

# Constants
IMAGE_FOLDER = "incident_images"
CSV_FILE = "incident_reports.csv"
USER_FILE = "users.csv"
LOCAL_BACKGROUND = "UMPbcg.jpg"

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

def delete_user(username):
    df = load_users()
    df = df[df["username"] != username]
    df.to_csv(USER_FILE, index=False)

def reset_password(username, new_password):
    df = load_users()
    df.loc[df["username"] == username, "password"] = new_password
    df.to_csv(USER_FILE, index=False)

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

def update_user_incident(index, incident_type, location, description):
    df = load_incidents()
    df.at[index, "Type"] = incident_type
    df.at[index, "Location"] = location
    df.at[index, "Description"] = description
    df.to_csv(CSV_FILE, index=False)

# Main App
def main():
    st.set_page_config(page_title="UMPSA Incident Report System", layout="centered")

    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("data:image/jpg;base64,{encoded_bg}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }
        .main .block-container {
            background-color: rgba(255, 255, 255, 0.88);
            border-radius: 10px;
            padding: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.image("Emblem_of_Universiti_Malaysia_Pahang.png", width=120)
    st.title("🎓 UMPSA Campus Incident Reporting Portal")

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
        menu_option = st.sidebar.radio("Navigate", ["Submit Report", "My Reports"] if st.session_state.role == "user" else ["Dashboard"])

        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()

        if st.session_state.role == 'user' and menu_option == "Submit Report":
            gps_result = streamlit_js_eval.get_geolocation()

            with st.form("incident_form"):
                st.subheader("📋 Submit Incident Report")
                incident_type = st.selectbox("Incident Type", ["Fire", "Injury", "Chemical Spill", "Other"])
                location = st.text_input("Manual Location (e.g., Block A, Lab 3)")
                description = st.text_area("Describe what happened", height=150)
                uploaded_image = st.file_uploader("Upload a photo (optional)", type=["jpg", "jpeg", "png"])

                if uploaded_image:
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
                    save_incident(st.session_state.username, incident_type, location, auto_location, description, img_filename)
                    st.success("✅ Incident submitted successfully!")
                else:
                    st.warning("Please fill in all required fields.")

        elif st.session_state.role == 'user' and menu_option == "My Reports":
            st.subheader("📁 My Submitted Reports")
            df = load_incidents()
            user_df = df[df["Username"] == st.session_state.username].reset_index()

            if not user_df.empty:
                for i, row in user_df.iterrows():
                    with st.expander(f"[{row['Timestamp']}] {row['Type']}"):
                        st.markdown(f"**Location:** {row['Location']}")
                        st.markdown(f"**Detected Location:** {row['Auto_Location']}")
                        st.markdown(f"**Description:** {row['Description']}")
                        if row['Image']:
                            if pd.notna(row['Image']) and isinstance(row['Image'], str):
                                img_path = os.path.join(IMAGE_FOLDER, row['Image'])
                            if os.path.exists(img_path):
                                st.image(img_path, caption="Attached Image", use_container_width=True)

                            if os.path.exists(img_path):
                                st.image(img_path, caption="Attached Image", use_container_width=True)

                        new_type = st.selectbox("Edit Type", ["Fire", "Injury", "Chemical Spill", "Other"], index=["Fire", "Injury", "Chemical Spill", "Other"].index(row['Type']), key=f"type_{i}")
                        new_loc = st.text_input("Edit Location", value=row['Location'], key=f"loc_{i}")
                        new_desc = st.text_area("Edit Description", value=row['Description'], key=f"desc_{i}")
                        if st.button("Update Report", key=f"update_{i}"):
                            update_user_incident(row['index'], new_type, new_loc, new_desc)
                            st.success("Report updated!")
                            st.rerun()
            else:
                st.info("You have not submitted any reports.")

        elif st.session_state.role == 'admin':
            st.subheader("📂 Incident Dashboard")
            df = load_incidents()
            users_df = load_users()

            st.subheader("🔍 Filter Reports")
            search_username = st.text_input("Filter by Username")
            search_type = st.selectbox("Filter by Type", ["All"] + sorted(df["Type"].unique()) if not df.empty else ["All"])

            if not df.empty:
                filtered_df = df.copy()
                if search_username:
                    filtered_df = filtered_df[filtered_df["Username"].str.contains(search_username, case=False)]
                if search_type != "All":
                    filtered_df = filtered_df[filtered_df["Type"] == search_type]

                for _, row in filtered_df.iterrows():
                    with st.expander(f"[{row['Timestamp']}] {row['Type']} by {row['Username']}"):
                        st.markdown(f"**Manual Location:** {row['Location']}")
                        st.markdown(f"**Detected Location:** {row['Auto_Location']}")
                        st.markdown(f"**Description:** {row['Description']}")
                        if row['Image']:
                            img_path = os.path.join(IMAGE_FOLDER, row['Image'])
                            if os.path.exists(img_path):
                                st.image(img_path, caption="Attached Image", use_container_width=True)

                st.download_button("⬇ Download Filtered Reports (CSV)", data=filtered_df.to_csv(index=False), file_name="filtered_reports.csv")
            else:
                st.info("No incidents have been reported yet.")

            st.subheader("👥 Registered Users")
            show_passwords = st.checkbox("Show passwords", value=False)

            if not users_df.empty:
                df_display = users_df.copy()
                if not show_passwords:
                    df_display["password"] = "🔒"

                selected_user = st.selectbox("Select user to manage", df_display["username"].tolist())
                new_pass = st.text_input("New password for selected user", key="reset_password")

                if st.button("Reset Password"):
                    if selected_user and new_pass:
                        reset_password(selected_user, new_pass)
                        st.success("Password reset successfully.")
                        st.rerun()

                if st.button("Delete User"):
                    if selected_user:
                        delete_user(selected_user)
                        st.success("User deleted successfully.")
                        st.rerun()

                st.dataframe(df_display)
            else:
                st.info("No registered users found.")

if __name__ == "__main__":
    main()
