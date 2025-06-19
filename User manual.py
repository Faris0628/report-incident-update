import streamlit as st

st.set_page_config(page_title="UMPSA Incident Reporting Manual", layout="wide")

st.title("📘 UMPSA Incident Reporting System - User Manual")

# Sidebar Navigation
section = st.sidebar.radio("📚 Navigate Manual", [
    "1. Introduction",
    "2. Installation (For Developers)",
    "3. Accessing the Application",
    "4. Creating an Account (Register)",
    "5. Logging In",
    "6. Submit a New Incident Report",
    "7. View and Edit Your Reports",
    "8. Admin Dashboard",
    "9. Managing Users",
    "10. Logging Out",
    "11. Notes",
    "📞 Contact"
])

# Content Display
if section == "1. Introduction":
    st.header("1. Introduction")
    st.write("""
    This manual provides guidance on using the UMPSA Campus Incident Reporting Web Application.
    The system enables users to submit, edit, and review campus-related incident reports,
    while administrators can manage all reports and user accounts.
    """)

elif section == "2. Installation (For Developers)":
    st.header("2. Installation Manual (For Developers or Hosting Admins)")
    st.subheader("Requirements")
    st.write("""
    - Python 3.8 or newer  
    - pip (Python package manager)  
    - Git (optional)  
    - Internet connection
    """)

    st.subheader("Installation Steps")
    st.markdown("""
    **1. Download or Clone the Project**
    - Option 1: Download ZIP from the repository and extract.
    - Option 2: Use Git:
    ```bash
    git clone https://github.com/your-username/incident-report-app.git
    cd incident-report-app
    ```

    **2. Create a Virtual Environment (optional):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate
    ```

    **3. Install Required Libraries:**
    ```bash
    pip install -r requirements.txt
    ```
    *If `requirements.txt` is not available:*
    ```bash
    pip install streamlit pandas streamlit-js-eval geopy
    ```

    **4. Add Required Files and Folders:**
    Ensure the following exist:
    - `users.csv` (headers: `username,password,role`)
    - `incident_reports.csv` (optional, auto-created)
    - `incident_images/` folder (auto-created)
    - `background.jpg`

    **5. Run the Application:**
    ```bash
    streamlit run your_script.py
    ```
    Replace `your_script.py` with the actual filename.

    **6. Access the App:**
    Open your browser and go to: [http://localhost:8501](http://localhost:8501)
    """)

elif section == "3. Accessing the Application":
    st.header("3. Accessing the Application")
    st.write("""
    - Open your web browser.
    - Go to the app link provided by the admin (e.g., `https://your-streamlit-app-link`).
    """)

elif section == "4. Creating an Account (Register)":
    st.header("4. Creating an Account (Register)")
    st.markdown("""
    1. Click the **🖍 Register** tab on the homepage.  
    2. Enter a unique **Username** and a **Password**.  
    3. Click **Register**.  
    4. If the username is not taken, your account will be created.
    """)

elif section == "5. Logging In":
    st.header("5. Logging In")
    st.markdown("""
    1. Click the **🔐 Login** tab.  
    2. Enter your **Username** and **Password**.  
    3. Click **Login**.  
    4. If correct, you will be taken to your dashboard.
    """)

elif section == "6. Submit a New Incident Report":
    st.header("6. Submit a New Incident Report (For Users)")
    st.markdown("""
    1. Log in and select **Submit Report** in the sidebar.  
    2. Choose an **Incident Type** (e.g., Fire, Injury).  
    3. Enter your **Manual Location** (e.g., Block B).  
    4. Fill in the **Description**.  
    5. Optionally upload an **image** (JPG, JPEG, PNG).  
    6. Click **Submit Incident** to send your report.
    """)

elif section == "7. View and Edit Your Reports":
    st.header("7. View and Edit Your Reports (For Users)")
    st.markdown("""
    1. Click **My Reports** in the sidebar.  
    2. Your previous submissions will be listed.  
    3. Expand a report to see its full details.  
    4. Edit **Type**, **Location**, or **Description** as needed.  
    5. Click **Update Report** to save changes.
    """)

elif section == "8. Admin Dashboard":
    st.header("8. Admin Dashboard (For Admins Only)")
    st.markdown("""
    1. Log in as an admin and click **Dashboard**.  
    2. View all reports submitted by users.  
    3. Filter by **Username** or **Incident Type**.  
    4. Expand any report to review its content.  
    5. Use **Download Filtered Reports** to save CSV.
    """)

elif section == "9. Managing Users":
    st.header("9. Managing Users (Admins Only)")
    st.markdown("""
    1. Scroll down in the **Dashboard**.  
    2. See a table of all registered users.  
    3. Use the checkbox to **show/hide passwords**.  
    4. Select a user to **reset their password** or **delete** them.
    """)

elif section == "10. Logging Out":
    st.header("10. Logging Out")
    st.write("Click **Logout** in the sidebar to securely exit your session.")

elif section == "11. Notes":
    st.header("11. Notes")
    st.markdown("""
    - Ensure all required fields are filled before submitting a report.  
    - Only image types JPG, JPEG, and PNG are allowed.  
    - All data is stored locally on the server.
    """)

elif section == "📞 Contact":
    st.header("📞 Contact")
    st.write("For any issues or inquiries, please contact the system administrator or project owner.")

