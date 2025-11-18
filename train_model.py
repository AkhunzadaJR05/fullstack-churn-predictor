import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle

# --- 1. Connect to Database & Load Data ---
print("Connecting to database...")
DB_USER = 'postgres'
DB_PASS = 'admin'  
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'postgres'

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

print("Reading data from 'customers' table...")
# We only select the columns we need for prediction
query = """
SELECT 
    seniorcitizen, partner, dependents, tenure, 
    internetservice, onlinesecurity, onlinebackup, 
    deviceprotection, techsupport, contract, 
    paperlessbilling, paymentmethod, monthlycharges, totalcharges, churn
FROM customers
"""
df = pd.read_sql(query, engine)

# Quick cleanup: 'TotalCharges' sometimes has empty spaces in this specific dataset
# We force them to numbers and turn errors into 0
df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce').fillna(0)

# Define our Features (X) and Target (y)
X = df.drop('churn', axis=1)
y = df['churn'].apply(lambda x: 1 if x == 'Yes' else 0) # Convert Yes/No to 1/0

print(f"   Loaded {len(df)} rows. Features defined.")

# --- 2. Feature Engineering (The "Professional" Part) ---
# We need to turn text columns into numbers using "One-Hot Encoding"
categorical_features = [
    'partner', 'dependents', 'internetservice', 'onlinesecurity', 
    'onlinebackup', 'deviceprotection', 'techsupport', 'contract', 
    'paperlessbilling', 'paymentmethod'
]

# We create a "Transformer" that automatically handles this conversion
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough' # Keep the numeric columns (tenure, monthlycharges) as they are
)

# --- 3. Build the Pipeline ---
# A Pipeline bundles the preprocessor and the model into one object.
# This is crucial because we can save the WHOLE thing.
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# --- 4. Train the Model ---
print("Training the Random Forest model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"Model trained! Accuracy on test data: {score:.2f}")

# --- 5. Save the Model ---
print("Saving model to 'churn_model.pkl'...")
with open('churn_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Done! You can now use this model to make predictions.")