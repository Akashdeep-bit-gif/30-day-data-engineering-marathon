import glob
import json
import psycopg2

DB_CONFIG = {
    "dbname": "data_engineering_db",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5432"
}

def load_raw_to_staging():
    json_files = glob.glob("data/raw/*.json")
    if not json_files:
        print("ℹ️ No JSON files found in data/raw/")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO staging_weather (latitude, longitude, temperature, windspeed, winddirection, weathercode, observation_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    loaded_count = 0
    for file_path in json_files:
        with open(file_path, "r") as f:
            payload = json.load(f)
            cw = payload.get("current_weather", {})
            
            cursor.execute(insert_query, (
                payload.get("latitude"),
                payload.get("longitude"),
                cw.get("temperature"),
                cw.get("windspeed"),
                cw.get("winddirection"),
                cw.get("weathercode"),
                cw.get("time")
            ))
            loaded_count += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Loaded {loaded_count} payload(s) into staging_weather!")

if __name__ == "__main__":
    load_raw_to_staging()