from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import pickle

# --- 1. Load the Trained Model ---
print("Loading the model...")
with open('churn_model.pkl', 'rb') as f:
    model = pickle.load(f)

# --- 2. Define the API App ---
app = FastAPI(title="Churn Prediction API")

# --- 3. Define the Data Structure (The Contract) ---
# This ensures the user sends exactly the right data types
class CustomerData(BaseModel):
    seniorcitizen: int
    partner: str
    dependents: str
    tenure: int
    internetservice: str
    onlinesecurity: str
    onlinebackup: str
    deviceprotection: str
    techsupport: str
    contract: str
    paperlessbilling: str
    paymentmethod: str
    monthlycharges: float
    totalcharges: float

# --- 4. Define the Prediction Endpoint ---
@app.post("/predict")
def predict_churn(data: CustomerData):
    # Convert the incoming JSON data into a Pandas DataFrame
    # The model expects a DataFrame, just like when we trained it
    input_data = pd.DataFrame([data.dict()])
    
    # Make the prediction
    prediction = model.predict(input_data)[0] # 0 or 1
    probability = model.predict_proba(input_data)[0][1] # Probability of Churn (0.0 to 1.0)
    
    # Return the result as JSON
    return {
        "prediction": "Churn" if prediction == 1 else "No Churn",
        "churn_probability": float(probability),
        "risk_level": "High" if probability > 0.7 else "Low"
    }

# To run this: uvicorn main_api:app --reload