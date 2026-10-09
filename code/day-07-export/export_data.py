import psycopg2
import pandas as pd
import os

DB_CONFIG = {
    "dbname": "data_engineering_db",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5432"
}

def export_analytics_data():
    os.makedirs("data/exports", exist_ok=True)
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = "SELECT * FROM analytics_weather;"
    df = pd.read_sql_query(query, conn)
    
    csv_path = "data/exports/analytics_weather.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Exported CSV: {csv_path}")
    
    try:
        parquet_path = "data/exports/analytics_weather.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"✅ Exported Parquet: {parquet_path}")
    except Exception as e:
        print(f"ℹ️ Parquet export skipped: {e}")
        
    conn.close()

if __name__ == "__main__":
    export_analytics_data()