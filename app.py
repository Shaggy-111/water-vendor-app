import pandas as pd
import streamlit as st
import sqlite3
from datetime import datetime, time, timedelta
import random
import re
import smtplib
from email.mime.text import MIMEText
from PIL import Image
import streamlit as st
import os
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file if available

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")  # fallback to empty string

import requests

def get_lat_lng_from_address(address):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}"
        response = requests.get(url)
        result = response.json()
        if result["status"] == "OK":
            location = result["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None


def status_badge(status):
    if status == "Pending":
        return "🟡 Pending"
    elif status == "Accepted":
        return "🟢 Accepted"
    elif status == "Rejected":
        return "🔴 Rejected"
    elif status == "Delivered":
        return "✅ Delivered"
    return status



def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# ------------------ CAPTCHA GENERATOR ------------------
def generate_captcha_code():
    return ''.join(random.choices(string.ascii_uppercase, k=3))

# ------------------ PASSWORD VALIDATION ------------------
def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password) and
        re.search(r"[!@#$%^&*]", password)
    )

# ------------------ USERNAME VALIDATION ------------------
def is_valid_username(username):
    return (
        len(username) >= 4 and
        re.match("^[a-zA-Z0-9_]+$", username)
    )

def send_verification_code(to_email, code):
    from_email = "shagunbhatia98@gmail.com"  # Replace with your Gmail
    from_password = "xjeu xsis wtqf pfgw"  # Use app password here

    msg = MIMEText(f"Your verification code is: {code}")
    msg["Subject"] = "Vendor Signup Verification Code"
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, from_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email send failed: {e}")
        return False
    
import requests

def get_lat_long_from_address(address, api_key):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": api_key}
        res = requests.get(url, params=params)
        data = res.json()
        if data["status"] == "OK":
            loc = data["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        return None, None
    except Exception as e:
        print("Geocoding error:", e)
        return None, None




# ------------------ SIGNUP FUNCTION ------------------
import random
import string

def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def signup_user():
    import requests
    st.subheader("📝 Sign-Up (Vendor / Delivery Partner)")

    role = st.radio("Select Role", ["vendor", "delivery"])

    # Common Fields
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Strong Password", type="password")
    email = st.text_input("Enter Your Email Address")
    mobile = st.text_input("Enter Your Mobile Number")

    # Address
    city_options = ["Delhi", "Mumbai", "Other"]
    selected_city = st.selectbox("Select Your City", city_options)
    if selected_city == "Other":
        location = st.text_area("Enter Full Address")
    else:
        address = st.text_area("Enter Full Address (Street, Building, etc.)")
        location = f"{selected_city} - {address}" if address else ""

    # Delivery Fields
    id_proof_path = ""
    if role == "delivery":
        upload_option = st.radio("Upload ID Proof Using:", ["📁 File Upload", "📷 Camera"])
        if upload_option == "📁 File Upload":
            id_proof_file = st.file_uploader("Choose Image/PDF", type=["jpg", "jpeg", "png", "pdf"])
        else:
            id_proof_file = st.camera_input("Capture ID Proof")

    # Captcha
    if "captcha_code" not in st.session_state:
        st.session_state.captcha_code = generate_captcha_code()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 🔐 Captcha: `{st.session_state.captcha_code}`")
    with col2:
        if st.button("🔄 Refresh Captcha"):
            st.session_state.captcha_code = generate_captcha_code()

    captcha_input = st.text_input("Enter Captcha Code (e.g., ABC)")

    # OTP Verification Flow
    for key in ["email_verified", "verification_sent", "account_created"]:
        st.session_state.setdefault(key, False)

    if not st.session_state.verification_sent and st.button("Send Email Verification Code"):
        if not all([username, password, email, location, mobile, captcha_input]):
            st.warning("⚠️ Please fill all fields.")
            return
        if not is_valid_username(username) or not is_strong_password(password) or not is_valid_email(email):
            st.warning("⚠️ Invalid Username / Email / Weak Password.")
            return
        if captcha_input.strip().upper() != st.session_state.captcha_code:
            st.error("❌ Captcha mismatch.")
            return
        if not mobile.isdigit() or len(mobile) != 10:
            st.error("❌ Mobile number must be 10 digits.")
            return

        # DB Duplicate Check
        with sqlite3.connect('data/orders.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                st.error("⚠️ Username already exists.")
                return
            cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                st.error("⚠️ Email already exists.")
                return

        # Send OTP
        otp_code = str(random.randint(100000, 999999))
        st.session_state.email_otp = otp_code
        st.session_state.email_to_verify = email
        if send_verification_code(email, otp_code):
            st.success("📩 OTP sent successfully.")
            st.session_state.verification_sent = True

    # OTP Verify
    if st.session_state.verification_sent and not st.session_state.email_verified:
        otp_input = st.text_input("Enter the 6-digit OTP sent to your email")
        if st.button("✅ Verify Email"):
            if otp_input == st.session_state.email_otp:
                st.success("✅ Email verified successfully.")
                st.session_state.email_verified = True
            else:
                st.error("❌ Incorrect OTP.")

    # Final Create Account
    if st.session_state.email_verified and st.button("Create Account", key="create_account_final"):
        if not all([username, password, email, location, mobile, captcha_input]):
            st.warning("⚠️ All fields required.")
            return
        if captcha_input.strip().upper() != st.session_state.captcha_code:
            st.error("❌ Invalid captcha.")
            return

        # Delivery image check
        if role == "delivery":
            if not id_proof_file:
                st.error("❌ Please upload or capture your ID proof.")
                return
            folder = "data/id_proofs"
            os.makedirs(folder, exist_ok=True)
            ext = "png" if upload_option == "📷 Camera" else id_proof_file.name.split(".")[-1]
            file_name = f"{username}_id_proof.{ext}"
            id_proof_path = os.path.join(folder, file_name)
            with open(id_proof_path, "wb") as f:
                f.write(id_proof_file.getbuffer())
        else:
            id_proof_path = ""

        # 🌍 Get Coordinates
        try:
            GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
            latitude, longitude = get_lat_long_from_address(location, GOOGLE_API_KEY)
            if not latitude or not longitude:
                st.warning("⚠️ Could not fetch location coordinates. Please check your address or API key.")
                return
        except Exception as e:
            st.error("🔐 Google API Error: Check your secrets.toml")
            return

        try:
            with sqlite3.connect('data/orders.db') as conn:
                cursor = conn.cursor()
                approval_flag = 1 if role == "vendor" else 0

                cursor.execute("""
                    INSERT INTO users (
                        username, password, location, email, mobile, verification_code,
                        is_verified, role, id_proof_path, is_approved, latitude, longitude
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
                """, (username, password, location, email, mobile, st.session_state.email_otp,
                      role, id_proof_path, approval_flag, latitude, longitude))
                conn.commit()

            st.success("✅ Account created successfully! Redirecting...")
            time.sleep(2)
            for key in ["show_signup", "captcha_code", "email_verified", "verification_sent", "account_created"]:
                st.session_state.pop(key, None)
            st.rerun()
        except sqlite3.IntegrityError as e:
            st.error(f"❌ Duplicate Entry: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    if st.button("❌ Cancel / Back to Login"):
        for key in ["show_signup", "email_verified", "verification_sent", "account_created", "captcha_code"]:
            st.session_state.pop(key, None)
        st.rerun()



# -------------------------- HELPER FUNCTION --------------------------
def get_user_role(username, password):
    import sqlite3

    with sqlite3.connect("data/orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result:
            db_role, db_password = result
            if db_password == password:
                return db_role
    return None


def status_badge(status):
    badges = {
        "Pending": "🟡 Pending",
        "Accepted": "🟢 Accepted",
        "Rejected": "🔴 Rejected",
        "Dispatched": "🚚 Dispatched",
        "On Vehicle": "📦 On Vehicle",
        "Delivered": "✅ Delivered"
    }
    return badges.get(status, status)


def admin_dashboard():
    import pandas as pd
    import matplotlib.pyplot as plt
    import io
    from datetime import datetime, timedelta
    import sqlite3
    import os

    st.title("👑 Admin Dashboard")
    st.success("Welcome, Admin! Manage vendor orders and delivery partners.")

    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    with col3:
        show_notifications = st.toggle("🔔", key="toggle_notify")
    with col4:
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()

    # ---------------- Notifications ----------------
    if "notifications" in st.session_state and st.session_state.notifications and show_notifications:
        st.markdown("### 🔔 Recent Notifications")
        for note in reversed(st.session_state.notifications[-5:]):
            st.info(f"{note['msg']} at {note['time']}")

    # ---------------- Load Orders ----------------
    conn = sqlite3.connect('data/orders.db')
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY created_at DESC", conn)
    conn.close()

    if df.empty:
        st.info("No orders found.")
        return

    df["created_at"] = pd.to_datetime(df["created_at"])

    # ---------------- Summary ----------------
    now = datetime.now()
    st.markdown("### 📆 Weekly & Monthly Order Summary")
    colW1, colW2 = st.columns(2)
    colW1.metric("🗓️ Last 7 Days", df[df["created_at"] >= now - timedelta(days=7)].shape[0])
    colW2.metric("📆 Last 30 Days", df[df["created_at"] >= now - timedelta(days=30)].shape[0])

    # ---------------- Delivery Partner Submissions ----------------
    st.markdown("## 🧾 Delivery Partner Submissions")
    conn = sqlite3.connect('data/orders.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, mobile, location, id_proof_path, is_approved FROM users WHERE role = 'delivery'")
    delivery_users = cursor.fetchall()
    conn.close()

    for uname, email, mobile, loc, proof_path, approved in delivery_users:
        with st.expander(f"👤 {uname}"):
            st.markdown(f"📧 **Email:** `{email}`")
            st.markdown(f"📱 **Mobile:** `{mobile}`")
            st.markdown(f"📍 **Location:** `{loc}`")
            if proof_path and os.path.exists(proof_path):
                ext = os.path.splitext(proof_path)[1].lower()
                if ext in [".jpg", ".jpeg", ".png"]:
                    st.image(proof_path, caption="ID Proof", width=300)
                elif ext == ".pdf":
                    with open(proof_path, "rb") as f:
                        st.download_button("📥 Download PDF", f.read(), file_name=os.path.basename(proof_path))
            else:
                st.warning("⚠️ No ID proof uploaded.")
            if not approved:
                if st.button(f"✅ Approve {uname}", key=f"approve_{uname}"):
                    conn = sqlite3.connect('data/orders.db')
                    cur = conn.cursor()
                    cur.execute("UPDATE users SET is_approved = 1 WHERE username = ?", (uname,))
                    conn.commit()
                    conn.close()
                    st.success(f"{uname} approved successfully.")
                    st.rerun()
            else:
                st.success("✅ Already Approved")
    

    st.markdown("## 🧪 Upload Water Test Report (Admin Only)")
    month = st.selectbox("Select Month", [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    year = st.selectbox("Select Year", [str(y) for y in range(2023, datetime.now().year + 1)])
    report_file = st.file_uploader("Upload Lab Report (PDF only)", type=["pdf"])

    if report_file and st.button("📤 Upload Report"):
        folder = "data/lab_reports"
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f"{month}_{year}.pdf")
        with open(file_path, "wb") as f:
            f.write(report_file.read())

        conn = sqlite3.connect("data/orders.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lab_reports (month, year, report_path, uploaded_at)
            VALUES (?, ?, ?, ?)
        """, (month, year, file_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        st.success("✅ Report uploaded successfully.")


    # ---------------- Filter Orders ----------------
    st.subheader("🔍 Filter Orders")
    f1, f2, f3 = st.columns(3)
    with f1:
        selected_status = st.selectbox("Status", ["All", "Pending", "Accepted", "Rejected", "Dispatched", "Delivered"])
    with f2:
        vendor_filter = st.text_input("Vendor Name").strip()
    with f3:
        date_filter = st.date_input("Order Date", value=None)

    filtered_df = df.copy()
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]
    if vendor_filter:
        filtered_df = filtered_df[filtered_df["vendor_name"].str.contains(vendor_filter, case=False)]
    if date_filter:
        filtered_df = filtered_df[filtered_df["created_at"].dt.date == date_filter]

    # ---------------- Export CSV ----------------
    if not filtered_df.empty:
        csv_buffer = io.StringIO()
        filtered_df.to_csv(csv_buffer, index=False)
        st.download_button("📥 Export CSV", csv_buffer.getvalue(), "orders.csv", "text/csv")

    # ---------------- Metrics & Chart ----------------
    st.markdown("### 📊 Order Status Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Accepted", df[df["status"] == "Accepted"].shape[0])
    c2.metric("❌ Rejected", df[df["status"] == "Rejected"].shape[0])
    c3.metric("⏳ Pending", df[df["status"] == "Pending"].shape[0])

    st.markdown("### 📈 Status Distribution")
    fig, ax = plt.subplots()
    ax.pie(df["status"].value_counts(), labels=df["status"].value_counts().index, autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # ---------------- Orders ----------------
    st.markdown("### 📦 Orders")
    if filtered_df.empty:
        st.info("No orders match the selected filters.")
        return

    items_per_page = 5
    total_pages = (len(filtered_df) - 1) // items_per_page + 1
    page = st.number_input("Page", 1, total_pages, 1)
    start, end = (page - 1) * items_per_page, page * items_per_page

    for _, row in filtered_df.iloc[start:end].iterrows():
        if f"expand_order_{row['id']}" not in st.session_state:
            st.session_state[f"expand_order_{row['id']}"] = False

        col_id, col_status, col_btn = st.columns([2, 3, 2])
        with col_id:
            st.markdown(f"🧾 **Order #{row['id']} - {row['vendor_name']}**")
        with col_status:
            overall = "✅ Delivered" if row["status"] == "Delivered" else "🟡 In Progress"
            st.markdown(f"📌 Status: **{overall}**")
        with col_btn:
            if st.button(f"🔍 Track Order #{row['id']}", key=f"track_{row['id']}"):
                st.session_state[f"expand_order_{row['id']}"] = not st.session_state[f"expand_order_{row['id']}"]

        if st.session_state.get(f"expand_order_{row['id']}", False):
            with st.expander(f"Order #{row['id']} - {row['vendor_name']}", expanded=True):
                st.write(f"📦 Items: `{row['order_type']}`")
                st.write(f"📦 Quantity: `{row['quantity']}`")
                st.write(f"📅 Placed At: `{row['created_at']}`")

                # 🚚 Delivery Progress (Only Delivery Statuses)
                delivery_steps = ["Dispatched", "On Vehicle", "Delivered"]
                current_step = row["status"] if row["status"] in delivery_steps else "Dispatched"
                current_index = delivery_steps.index(current_step)

                st.markdown("#### 🚚 Delivery Progress")
                cols = st.columns(len(delivery_steps))
                for i, step in enumerate(delivery_steps):
                    with cols[i]:
                        if i < current_index:
                            st.success(f"✅ {step}")
                        elif i == current_index:
                            st.info(f"🕒 {step}")
                        else:
                            st.write(f"🔜 {step}")

                # Order Details
                st.write(f"🏷️ Vehicle: `{row.get('vehicle_number') or 'None'}`")
                st.write(f"🚚 Delivered By: `{row.get('delivery_by') or 'Not Yet Assigned'}`")
                st.write(f"📍 Vendor Address: `{row.get('vendor_location', 'N/A')}`")

                # 📍 Vendor Location Map
                conn = sqlite3.connect("data/orders.db")
                cursor = conn.cursor()
                cursor.execute("SELECT latitude, longitude FROM users WHERE username = ?", (row["vendor_name"],))
                result = cursor.fetchone()
                conn.close()

                if result:
                    lat, lon = result
                    if lat and lon:
                        st.markdown("🌍 **Google Map Location of Vendor**")
                        st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                    else:
                        st.warning("⚠️ Vendor's coordinates not available.")
                else:
                    st.warning("⚠️ Vendor record not found.")

                # Delivery Photo
                if row.get("delivery_photo") and os.path.exists(row["delivery_photo"]):
                    st.image(row["delivery_photo"], caption="📷 Delivery Photo", width=300)

                # Assign Delivery Partner (only approved)
                conn = sqlite3.connect("data/orders.db")
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE role = 'delivery' AND is_approved = 1")
                approved_partners = [u[0] for u in cursor.fetchall()]
                conn.close()

                default = row.get("delivery_by") or "Select"
                assigned_to = st.selectbox(f"Assign Delivery Partner for Order #{row['id']}",
                                           ["Select"] + approved_partners,
                                           index=(["Select"] + approved_partners).index(default) if default in approved_partners else 0,
                                           key=f"assign_{row['id']}")

                if assigned_to != "Select" and assigned_to != row.get("delivery_by"):
                    conn = sqlite3.connect("data/orders.db")
                    cursor = conn.cursor()
                    cursor.execute("UPDATE orders SET delivery_by = ? WHERE id = ?", (assigned_to, row["id"]))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Assigned Order #{row['id']} to {assigned_to}")
                    st.rerun()

                # Accept / Reject Order
                if row["status"] == "Pending":
                    colA, colR = st.columns(2)
                    with colA:
                        if st.button(f"✅ Accept #{row['id']}", key=f"accept_{row['id']}"):
                            conn = sqlite3.connect("data/orders.db")
                            cursor = conn.cursor()
                            cursor.execute("UPDATE orders SET status = 'Accepted' WHERE id = ?", (row["id"],))
                            conn.commit()
                            conn.close()
                            st.rerun()
                    with colR:
                        if st.button(f"❌ Reject #{row['id']}", key=f"reject_{row['id']}"):
                            conn = sqlite3.connect("data/orders.db")
                            cursor = conn.cursor()
                            cursor.execute("UPDATE orders SET status = 'Rejected' WHERE id = ?", (row["id"],))
                            conn.commit()
                            conn.close()
                            st.rerun()


# -------------------------- VENDOR DASHBOARD --------------------------
def vendor_dashboard(username):
    import pandas as pd
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    import sqlite3

    # 🔓 Logout UI
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()

    st.title(f"🚚 Vendor Panel - AquaTrack - {username}")

    

    

    # 📍 Location
    conn = sqlite3.connect('data/orders.db')
    cursor = conn.cursor()
    cursor.execute("SELECT location FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    location = result[0] if result else "Unknown"
    st.markdown(f"📍 **Location:** {location}")

    # 📦 Bottle Info
    bottle_types = {
        "1L Bottle": {"bottles_per_case": 12, "min_cases": 10},
        "500ml Bottle": {"bottles_per_case": 20, "min_cases": 10},
        "250ml Bottle": {"bottles_per_case": 24, "min_cases": 10},
        "20L Bottle": {"bottles_per_case": 1, "min_cases": 10},
    }

    # 🧾 Place Order Section
    st.subheader("📦 Place a New Order (by Cases)")
    selected_types = st.multiselect("Select Bottle Types", list(bottle_types.keys()))
    case_inputs = {}

    for bottle in selected_types:
        case_inputs[bottle] = st.number_input(
            f"Enter number of cases for {bottle}",
            min_value=bottle_types[bottle]["min_cases"],
            step=1,
            key=f"case_input_{bottle}"
        )

    if st.button("🚲 Place Order"):
        if not selected_types:
            st.warning("⚠️ Please select at least one bottle type.")
        else:
            order_details = []
            total_bottles = 0
            for bottle in selected_types:
                cases = case_inputs[bottle]
                bottles = cases * bottle_types[bottle]["bottles_per_case"]
                order_details.append(f"{bottle}: {cases} cases")
                total_bottles += bottles

            summary = ", ".join(order_details)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("SELECT location FROM users WHERE username = ?", (username,))
            loc_data = cursor.fetchone()
            vendor_location = loc_data[0] if loc_data else "Unknown"

            cursor.execute("""
                INSERT INTO orders (vendor_name, order_type, quantity, status, created_at, vendor_location)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, summary, total_bottles, 'Pending', created_at, vendor_location))
            conn.commit()
            conn.close()

            st.success("✅ Order placed successfully!")
            st.balloons()
            st.rerun()

    # 🧾 Load Orders
    conn = sqlite3.connect('data/orders.db')
    df = pd.read_sql_query("SELECT * FROM orders WHERE vendor_name = ? ORDER BY created_at DESC", conn, params=(username,))
    conn.close()
    df["created_at"] = pd.to_datetime(df["created_at"])

    st.markdown("## 🧪 Monthly Water Test Reports")
    conn = sqlite3.connect("data/orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT month, year, report_path FROM lab_reports ORDER BY uploaded_at DESC")
    reports = cursor.fetchall()
    conn.close()

    if not reports:
        st.info("No reports uploaded yet.")
    else:
        for month, year, path in reports:
            report_title = f"📄 **{month} {year}**"
            st.markdown(report_title)
            if path and os.path.exists(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in [".jpg", ".jpeg", ".png"]:
                    st.image(path, caption=f"{month} {year} Report", use_column_width=True)
                elif ext == ".pdf":
                    with open(path, "rb") as file:
                        st.download_button("📥 Download PDF", file.read(), file_name=os.path.basename(path))
            else:
                st.warning("❌ Report file not found.")

    # 📊 Summary
    st.subheader("📊 Your Order Summary")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("✅ Accepted", df[df["status"] == "Accepted"].shape[0])
    with c2:
        st.metric("❌ Rejected", df[df["status"] == "Rejected"].shape[0])
    with c3:
        st.metric("⏳ Pending", df[df["status"] == "Pending"].shape[0])

    # 📈 Pie Chart
    if not df.empty:
        status_counts = df["status"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

    # 🔍 Filter by Date
    st.subheader("🔍 Order History")
    filter_date = st.date_input("Filter by Date", value=None)
    filtered_df = df.copy()
    if filter_date:
        filtered_df = df[df["created_at"].dt.date == filter_date]

    # 🧾 Display Orders
    st.subheader("🧾 Your Orders")
    display_df = filtered_df if filter_date else df.head(10)

    if display_df.empty:
        st.info("No orders to show.")
    else:
        for _, row in display_df.iterrows():
            with st.expander(f"Order #{row['id']} - Placed on {row['created_at']}"):
                st.write("📦 Items Ordered:")
                item_dict = {}
                for item in row["order_type"].split(","):
                    if ":" in item:
                        name, value = item.split(":")
                        value = value.strip().lower().replace("cases", "").strip()
                        try:
                            item_dict[name.strip()] = max(1, int(value))
                        except:
                            item_dict[name.strip()] = 1
                        st.markdown(f"• {name.strip()} — **{item_dict[name.strip()]} cases**")

                st.write(f"📍 Your Address: `{row.get('vendor_location', 'Not Available')}`")
                st.write(f"📌 Status: **{status_badge(row['status'])}**")

    # 📍 Order Status Progress
                status_list = ["Pending", "Accepted", "Dispatched", "On Vehicle", "Delivered"]
                current_index = status_list.index(row["status"]) if row["status"] in status_list else 0

                st.markdown("#### 🚚 Order Progress")
                for i, step in enumerate(status_list):
                    if i < current_index:
                        st.success(f"✅ {step}")
                    elif i == current_index:
                        st.info(f"🕒 In Progress: {step}")
                    else:
                        st.write(f"🔜 {step}")

                # --- Smart Order ID Controls ---
                col_copy, col_view = st.columns([1, 2])

            with col_copy:
                st.code(str(row['id']), language="text")
                st.button(f"📋 Copy ID #{row['id']}", key=f"copy_{row['id']}", disabled=True)

            with col_view:
                st.markdown(f"🔍 View More Details Below")


                # ⏱️ Editable/Cancellable within 30 mins if Pending
                order_time = row["created_at"]
                if isinstance(order_time, str):
                    order_time = pd.to_datetime(order_time)
                editable = row["status"] == "Pending" and (datetime.now() - order_time <= timedelta(minutes=30))

                if editable:
                    st.info("🛠️ You can edit or cancel this order within 30 minutes.")

                    # ✏️ Edit Specific Bottle Type
                    bottle_to_edit = st.selectbox(
                        f"Select bottle type to edit for Order #{row['id']}",
                        list(item_dict.keys()),
                        key=f"edit_bottle_{row['id']}"
                    )

                    new_qty = st.number_input(
                        f"New number of cases for {bottle_to_edit}",
                        min_value=1,
                        value=item_dict[bottle_to_edit],
                        step=1,
                        key=f"new_qty_{row['id']}_{bottle_to_edit}"
                    )

                    if st.button(f"💾 Update {bottle_to_edit} Quantity", key=f"update_{row['id']}_{bottle_to_edit}"):
                        item_dict[bottle_to_edit] = new_qty
                        updated_order_string = ", ".join([f"{b}: {q} cases" for b, q in item_dict.items()])
                        updated_total_bottles = sum(
                            q * bottle_types[b]["bottles_per_case"]
                            for b, q in item_dict.items()
                        )
                        conn = sqlite3.connect('data/orders.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE orders SET order_type = ?, quantity = ? WHERE id = ?",
                                       (updated_order_string, updated_total_bottles, row['id']))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Updated {bottle_to_edit} quantity.")
                        st.rerun()

                    # ❌ Cancel
                    if st.button(f"❌ Cancel Order #{row['id']}", key=f"cancel_{row['id']}"):
                        conn = sqlite3.connect('data/orders.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE orders SET status = 'Cancelled' WHERE id = ?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.warning(f"⚠️ Order #{row['id']} has been cancelled.")
                        st.rerun()
                else:
                    st.warning("⏳ Edit/Cancel disabled (after 30 minutes or status changed).")

def delivery_dashboard(username):
    import pandas as pd
    import sqlite3
    from datetime import datetime
    import os

    st.title(f"🚚 Delivery Dashboard - {username}")

    # 🔓 Logout Option
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    # 📦 Load All Pending/Assigned Orders
    conn = sqlite3.connect("data/orders.db")
    df = pd.read_sql_query("""
        SELECT * FROM orders
        WHERE status IN ('Accepted', 'Dispatched', 'On Vehicle')
        AND delivery_by = ?
        ORDER BY created_at DESC
    """, conn, params=(username,))
    conn.close()

    if df.empty:
        st.info("No orders to deliver yet.")
        return

    for _, row in df.iterrows():
        with st.expander(f"Order #{row['id']} - {row['vendor_name']}"):
            st.write(f"📦 Order Type: `{row['order_type']}`")
            st.write(f"🧮 Quantity: `{row['quantity']}`")
            st.write(f"📍 Address: `{row['vendor_location']}`")
            conn = sqlite3.connect("data/orders.db")
            cursor = conn.cursor()
            cursor.execute("SELECT latitude, longitude FROM users WHERE username = ?", (row["vendor_name"],))
            result = cursor.fetchone()
            conn.close()

            if result:
                lat, lon = result
                if lat and lon:
                    st.markdown("🌍 **Vendor Location Map**")
                    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                else:
                    st.warning("⚠️ Vendor coordinates not available.")
            else:
                st.warning("⚠️ Vendor record not found.")
            st.write(f"📅 Placed: `{row['created_at']}`")
            st.write(f"📌 Status: **{row['status']}**")

            # 🚛 Vehicle Number Input
            vehicle_number = st.text_input("Enter Vehicle Number", value=row['vehicle_number'] or "", key=f"vehicle_{row['id']}")

            # 📸 Upload Delivery Image
            uploaded_file = st.camera_input("📷 Capture Delivery Photo (Required)", key=f"cam_photo_{row['id']}")


            # 🔄 Status Dropdown
            new_status = st.selectbox("Update Order Status", ["Select", "Dispatched", "On Vehicle", "Delivered"], key=f"status_{row['id']}")

            if st.button(f"✅ Update Order #{row['id']}", key=f"update_{row['id']}"):
            # ⛔ Block if Delivered without photo
                if new_status == "Delivered" and not uploaded_file:
                    st.error("❌ You must capture a delivery photo before marking as Delivered.")
                    return

                photo_path = ""

                if uploaded_file and new_status == "Delivered":
                    folder = "data/delivery_images"
                    os.makedirs(folder, exist_ok=True)
                    photo_path = os.path.join(folder, f"{row['id']}_delivered.jpg")
                    with open(photo_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                conn = sqlite3.connect("data/orders.db")
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE orders SET status = ?, vehicle_number = ?, delivery_by = ?, delivery_image = ?
                    WHERE id = ?
                """, (new_status, vehicle_number, username, photo_path, row["id"]))
                conn.commit()
                conn.close()

                st.success(f"✅ Order #{row['id']} updated to {new_status}!")
                st.rerun()


def forgot_password():
    st.subheader("🔐 Forgot Password")

    email = st.text_input("Enter your registered Email")

    # Initialize state variables
    if "reset_otp_sent" not in st.session_state:
        st.session_state.reset_otp_sent = False
    if "reset_email_verified" not in st.session_state:
        st.session_state.reset_email_verified = False

    if st.button("📩 Send OTP"):
        if not is_valid_email(email):
            st.error("❌ Please enter a valid email address.")
            return

        # Check if email exists in the database
        conn = sqlite3.connect('data/orders.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            st.error("❌ Email not found in system.")
            return

        otp = str(random.randint(100000, 999999))
        st.session_state.reset_otp = otp
        st.session_state.reset_email = email
        st.session_state.reset_otp_sent = True

        # Send OTP (real implementation should email)
        send_verification_code(email, otp)
        st.success("✅ OTP has been sent to your email.")

    # OTP input
    if st.session_state.reset_otp_sent and not st.session_state.reset_email_verified:
        otp_input = st.text_input("Enter OTP sent to your email")

        if st.button("✅ Verify OTP"):
            if otp_input == st.session_state.reset_otp:
                st.success("🎉 Email verified successfully.")
                st.session_state.reset_email_verified = True
            else:
                st.error("❌ Incorrect OTP. Please try again.")

    # New password input
    if st.session_state.reset_email_verified:
        new_pass = st.text_input("Enter New Password", type="password")
        confirm_pass = st.text_input("Confirm New Password", type="password")

        if st.button("🔒 Reset Password"):
            if new_pass != confirm_pass:
                st.error("❌ Passwords do not match.")
                return

            if not is_strong_password(new_pass):
                st.error("❌ Password must be 8+ characters with upper/lowercase, digit, symbol.")
                return

            # Update password
            conn = sqlite3.connect('data/orders.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_pass, st.session_state.reset_email))
            conn.commit()
            conn.close()

            st.success("🔐 Password reset successfully! Please log in.")
            # Clear session and go back to login
            for key in ["show_forgot_password", "reset_otp_sent", "reset_email_verified", "reset_email", "reset_otp"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()





# -------------------------- MAIN FUNCTION --------------------------
import streamlit as st

def main():
    st.set_page_config(page_title="AquaTrack by VeeKay", layout="centered")
    st.markdown("<h1 style='color: #0066cc;'>AquaTrack by VeeKay</h1>", unsafe_allow_html=True)

    for key in ["logged_in", "username", "role", "show_signup", "show_forgot_password"]:
        if key not in st.session_state:
            st.session_state[key] = False if key in ["logged_in", "show_signup", "show_forgot_password"] else ""

    if st.session_state.logged_in:
        if st.session_state.role == "admin":
            admin_dashboard()
        elif st.session_state.role == "vendor":
            vendor_dashboard(st.session_state.username)
        elif st.session_state.role == "delivery":
            delivery_dashboard(st.session_state.username)
        return

    if st.session_state.show_signup:
        signup_user()
        return

    if st.session_state.show_forgot_password:
        forgot_password()
        return

    # -------------------- LOGIN BLOCK --------------------
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.radio("Login as", ["admin", "vendor", "delivery"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if not username or not password:
                st.warning("⚠️ Please enter both username and password.")
            else:
                try:
                    with sqlite3.connect('data/orders.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT username, password, role, is_verified, is_approved 
                            FROM users 
                            WHERE username = ? OR email = ?
                        """, (username, username))
                        user = cursor.fetchone()
                        print("🔍 Login Debug (fetched from DB):", user)

                        if user:
                            uname, db_pass, user_role, verified, approved = user

                            if password != db_pass:
                                st.error("❌ Invalid password.")
                                return

                            if user_role != role:
                                st.error("❌ You selected the wrong role.")
                                return

                            if not verified:
                                st.warning("⚠️ Your email is not verified.")
                                return

                            if user_role == "delivery" and not approved:
                                st.warning("⚠️ Your delivery partner request is pending admin approval.")
                                return

                            # ✅ Login success
                            st.session_state.logged_in = True
                            st.session_state.username = uname
                            st.session_state.role = user_role
                            st.success(f"✅ Logged in as {user_role.capitalize()}")
                            st.rerun()
                        else:
                            st.error("❌ User not found or not registered properly.")
                except Exception as e:
                    st.error(f"⚠️ Database error: {e}")

    with col2:
        if st.button("🔐 Forgot Password?"):
            st.session_state.show_forgot_password = True
            st.rerun()

    st.markdown("---")
    if st.button("New vendor? Sign up here"):
        st.session_state.show_signup = True
        st.rerun()

    st.markdown("<hr><p style='text-align:center; color:grey;'>© 2025 AquaTrack by VeeKay</p>", unsafe_allow_html=True)

# ------------------- ENTRY POINT -------------------
if __name__ == '__main__':
    main()