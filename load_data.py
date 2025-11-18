import pandas as pd
from sqlalchemy import create_engine

# --- Configuration ---
DB_USER = 'postgres'
DB_PASS = 'admin'  
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'postgres'

# --- Connect to the Database ---
print("Connecting to database...")
try:
    engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    
    # --- Read the Data ---
    print("Reading CSV file...")
    csv_file = 'WA_Fn-UseC_-Telco-Customer-Churn.csv'
    
    # Read the CSV into a Pandas DataFrame
    df = pd.read_csv(csv_file)
    print(f"   Found {len(df)} rows of data.")

    # --- Clean the Column Names ---
    # Databases hate spaces and capitals. Let's make them lower_snake_case
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    print("   Columns cleaned.")

    # --- Load into Database ---
    print("Loading data into PostgreSQL (this might take 10-20 seconds)...")
    
    # 'to_sql' does all the magic: creates the table and inserts rows
    df.to_sql('customers', engine, if_exists='replace', index=False)
    
    print("Success! Data loaded into table 'customers'.")

except FileNotFoundError:
    print(f"Error: Could not find file '{csv_file}'. Make sure it's in this folder!")
except Exception as e:
    print(f"An error occurred: {e}")