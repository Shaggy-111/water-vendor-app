import pandas as pd
import streamlit as st
import sqlite3
from datetime import datetime
import random
import re

# ------------------ CAPTCHA GENERATOR ------------------
def generate_captcha():
    a, b = random.randint(1, 9), random.randint(1, 9)
    st.session_state["captcha_question"] = f"{a} + {b}"
    st.session_state["captcha_answer"] = a + b

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

# ------------------ SIGNUP FUNCTION ------------------
import random
import string

def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def signup_vendor():
    st.subheader("📝 Vendor Sign-Up")

    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Strong Password", type="password")
    email = st.text_input("Enter Your Email Address")
    location = st.text_input("Enter Your Location (City)")

    # Generate captcha if not set
    if "captcha_answer" not in st.session_state or "captcha_question" not in st.session_state:
        generate_captcha()

    st.write("🔐 Solve the Captcha below to create your account:")
    st.markdown(f"**{st.session_state['captcha_question']} = ?**")
    captcha_input = st.text_input("Your Answer", key="captcha_input")

    # Track whether account was created
    if "account_created" not in st.session_state:
        st.session_state.account_created = False

    # If account is already created, show success + button to go back
    if st.session_state.account_created:
        st.success("✅ Account created successfully! Please click below to return to login.")
        if st.button("🔙 Go back to Login"):
            st.session_state.show_signup = False
            st.session_state.account_created = False
            st.rerun()
        return  # Stop further signup rendering

    # Handle account creation
    if st.button("Create Account"):
        if not (username and password and email and location and captcha_input):
            st.warning("⚠️ Please fill all fields.")
            return

        if not is_valid_username(username):
            st.error("❌ Username must be at least 4 characters, only letters/numbers/underscore.")
            return

        if not is_strong_password(password):
            st.error("❌ Password must be 8+ chars, with upper/lowercase, number, and symbol.")
            return

        if not captcha_input.strip().isdigit():
            st.error("❌ Captcha must be a number.")
            return

        if int(captcha_input.strip()) != st.session_state["captcha_answer"]:
            st.error("❌ Incorrect captcha. Try again.")
            generate_captcha()
            st.rerun()
            return

        # Check if username exists
        conn = sqlite3.connect('data/orders.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            st.error("⚠️ Username already exists. Please choose another.")
            conn.close()
            return

        # Generate a verification code for email
        verification_code = generate_verification_code()

        # Insert new vendor with verification_code
        cursor.execute("""
            INSERT INTO users (username, password, location, email, verification_code, is_verified, role)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (username, password, location, email, verification_code, 'vendor'))
        conn.commit()
        conn.close()

        # For now, display the verification code (you can send via email later)
        st.info(f"📧 Your verification code is: {verification_code} (Send via email in production)")

        st.session_state.account_created = True
        st.session_state.pop("captcha_question", None)
        st.session_state.pop("captcha_answer", None)
        st.rerun()

    # Cancel button at bottom
    if st.button("❌ Cancel / Back to Login"):
        st.session_state.show_signup = False
        st.session_state.pop("captcha_question", None)
        st.session_state.pop("captcha_answer", None)
        st.rerun()



# -------------------------- HELPER FUNCTION --------------------------
def get_user_role(username, password):
    conn = sqlite3.connect('data/orders.db')
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# -------------------------- ADMIN DASHBOARD --------------------------
def admin_dashboard():
    st.title("👑 Admin Dashboard")
    st.success("Welcome, Admin!")
    st.info("This is where you’ll manage all vendor orders and see analytics.")

    conn = sqlite3.connect('data/orders.db')
    cursor = conn.cursor()

    if 'action_id' in st.session_state and 'action_type' in st.session_state:
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?",
                       (st.session_state.action_type, st.session_state.action_id))
        conn.commit()
        st.success(f"Order #{st.session_state.action_id} marked as {st.session_state.action_type}")
        del st.session_state.action_id
        del st.session_state.action_type

    df = pd.read_sql_query("SELECT * FROM orders ORDER BY created_at DESC", conn)
    conn.close()

    if df.empty:
        st.info("No orders found yet.")
    else:
        st.subheader("📦 All Orders")
        for _, row in df.iterrows():
            with st.expander(f"Order #{row['id']} - {row['vendor_name']}"):
                st.write(f"Order Type: {row['order_type']}")
                st.write(f"Quantity: {row['quantity']}")
                st.write(f"Status: {row['status']}")
                st.write(f"Placed At: {row['created_at']}")
                if row['status'] == "Pending":
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Accept #{row['id']}"):
                            st.session_state.action_id = row['id']
                            st.session_state.action_type = "Accepted"
                            st.rerun()
                    with col2:
                        if st.button(f"❌ Reject #{row['id']}"):
                            st.session_state.action_id = row['id']
                            st.session_state.action_type = "Rejected"
                            st.rerun()

# -------------------------- VENDOR DASHBOARD --------------------------
def vendor_dashboard(username):
    conn = sqlite3.connect('data/orders.db')
    cursor = conn.cursor()
    cursor.execute("SELECT location FROM users WHERE username = ?", (username,))
    location = cursor.fetchone()[0]
    conn.close()

    st.markdown(f"📍 **Location:** {location}")
    st.title(f"🚚 Vendor Dashboard - {username}")
    st.subheader("📦 Place a New Order")

    order_type = st.selectbox("Select Bottle Type", ["1L Bottle", "500ml Bottle", "2L Bottle"])
    quantity = st.number_input("Enter Quantity", min_value=1, value=10, step=1)

    if st.button("🚲 Place Order"):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect('data/orders.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (vendor_name, order_type, quantity, status, created_at) VALUES (?, ?, ?, ?, ?)",
                       (username, order_type, quantity, 'Pending', created_at))
        conn.commit()
        conn.close()
        st.success("✅ Order placed successfully!")
        st.rerun()

    st.subheader("📋 Your Last 3 Orders")
    conn = sqlite3.connect('data/orders.db')
    df = pd.read_sql_query("SELECT * FROM orders WHERE vendor_name = ? ORDER BY created_at DESC LIMIT 3",
                           conn, params=(username,))
    conn.close()

    if df.empty:
        st.info("No orders placed yet.")
    else:
        for _, row in df.iterrows():
            with st.expander(f"Order #{row['id']} - {row['order_type']}"):
                st.write(f"Quantity: {row['quantity']}")
                st.write(f"Status: {row['status']}")
                st.write(f"Placed At: {row['created_at']}")

# -------------------------- MAIN FUNCTION --------------------------
def main():
    st.set_page_config(page_title="Water Vendor App", layout="centered")
    st.title("💧 Water Vendor Management Login")

    for key in ["logged_in", "username", "role", "show_signup"]:
        if key not in st.session_state:
            st.session_state[key] = False if key in ["logged_in", "show_signup"] else ""

    if st.session_state.logged_in:
        if st.session_state.role == "admin":
            admin_dashboard()
        else:
            vendor_dashboard(st.session_state.username)
        return

    if st.session_state.show_signup:
        signup_vendor()
        return

    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.radio("Login as", ["admin", "vendor"])

    if st.button("Login"):
        user_role = get_user_role(username, password)
        if user_role == role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.success(f"Logged in as {role}")
            st.rerun()
        else:
            st.error("Invalid username, password or role!")

    st.markdown("---")
    if st.button("New vendor? Sign up here"):
        st.session_state.show_signup = True
        st.rerun()

# -------------------------- RUN APP --------------------------
if __name__ == '__main__':
    main()
