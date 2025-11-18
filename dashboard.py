import streamlit as st
import pandas as pd
import requests
import psycopg2

# --- Configuration ---
st.set_page_config(page_title="Telco Churn Manager", layout="wide")
API_URL = "http://127.0.0.1:8000/predict"

# --- Database Connection Config ---
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "admin"

# --- Helper Function: Get Data from DB ---
def get_db_data():
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        # Get 50 customers just to show the connection works
        query = "SELECT * FROM customers LIMIT 50"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return pd.DataFrame()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Live Prediction", "Database Monitor"])

# ===========================================
# PAGE 1: LIVE PREDICTION (Talks to API)
# ===========================================
if page == "Live Prediction":
    st.title("Real-Time Customer Churn Predictor")
    st.markdown("Enter customer details below to get a live AI prediction from the **FastAPI** backend.")

    # Create columns for a nicer layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tenure = st.slider("Tenure (Months)", 0, 72, 12)
        monthly_charges = st.number_input("Monthly Charges ($)", 0.0, 200.0, 70.0)
        total_charges = st.number_input("Total Charges ($)", 0.0, 10000.0, 1500.0)
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])

    with col2:
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
        partner = st.selectbox("Has Partner?", ["Yes", "No"])
        dependents = st.selectbox("Has Dependents?", ["Yes", "No"])

    with col3:
        tech_support = st.selectbox("Tech Support?", ["Yes", "No", "No internet service"])
        online_security = st.selectbox("Online Security?", ["Yes", "No", "No internet service"])
        paperless = st.selectbox("Paperless Billing?", ["Yes", "No"])
        senior = st.selectbox("Senior Citizen?", [0, 1])

    # Hidden defaults for fields we didn't make inputs for (to keep UI clean)
    # In a real app, we'd add inputs for all of them
    
    if st.button("Predict Churn Risk 🚀"):
        # 1. Prepare the JSON payload
        payload = {
            "seniorcitizen": senior,
            "partner": partner,
            "dependents": dependents,
            "tenure": tenure,
            "internetservice": internet_service,
            "onlinesecurity": online_security,
            "onlinebackup": "No", # Defaulting for simplicity
            "deviceprotection": "No", # Defaulting for simplicity
            "techsupport": tech_support,
            "contract": contract,
            "paperlessbilling": paperless,
            "paymentmethod": payment_method,
            "monthlycharges": monthly_charges,
            "totalcharges": total_charges
        }

        # 2. Send to API
        try:
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # 3. Display Result
                prob = result['churn_probability']
                if result['prediction'] == "Churn":
                    st.error(f"⚠️ HIGH RISK! Churn Probability: {prob:.2%}")
                else:
                    st.success(f"✅ LOW RISK. Churn Probability: {prob:.2%}")
            else:
                st.error("Error from API. Check inputs.")
                
        except Exception as e:
            st.error(f"Could not connect to API. Is it running? Error: {e}")

# ===========================================
# PAGE 2: DATABASE MONITOR (Talks to PostgreSQL)
# ===========================================
elif page == "Database Monitor":
    st.title("🗄️ Customer Database View")
    st.markdown("This page connects directly to the **PostgreSQL** database to view live customer records.")
    
    if st.button("Refresh Data"):
        with st.spinner("Fetching data from PostgreSQL..."):
            df = get_db_data()
            st.dataframe(df)
            st.success(f"Loaded {len(df)} rows successfully.")