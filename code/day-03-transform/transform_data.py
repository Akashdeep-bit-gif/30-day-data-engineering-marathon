import psycopg2

DB_CONFIG = {
    "dbname": "data_engineering_db",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5432"
}

def decode_weather_code(code):
    """Maps WMO Weather Interpretation Codes to human-readable text strings."""
    wmo_map = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing Rime Fog",
        51: "Light Drizzle",
        61: "Slight Rain",
        80: "Slight Rain Showers",
        95: "Thunderstorm"
    }
    return wmo_map.get(code, "Unknown Condition")

def transform_and_load():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Incremental Extraction (Anti-Join to fetch un-transformed records)
        fetch_query = """
            SELECT s.id, s.latitude, s.longitude, s.temperature, s.windspeed, s.weathercode, s.observation_time
            FROM staging_weather s
            LEFT JOIN analytics_weather a ON s.id = a.staging_id
            WHERE a.staging_id IS NULL;
        """
        cursor.execute(fetch_query)
        unprocessed_records = cursor.fetchall()

        if not unprocessed_records:
            print("ℹ️ Analytics Mart is already up to date. No new records to transform.")
            cursor.close()
            conn.close()
            return

        insert_query = """
            INSERT INTO analytics_weather (
                staging_id, latitude, longitude, 
                temperature_celsius, temperature_fahrenheit, 
                windspeed_kmh, windspeed_mph, 
                weather_condition, observation_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        transformed_count = 0
        for record in unprocessed_records:
            staging_id, lat, lon, temp_c, wind_kmh, wmo_code, obs_time = record

            # Metric Conversions & Business Transformations
            temp_f = round((float(temp_c) * 9 / 5) + 32, 2) if temp_c is not None else None
            wind_mph = round(float(wind_kmh) * 0.621371, 2) if wind_kmh is not None else None
            condition = decode_weather_code(wmo_code)

            cursor.execute(insert_query, (
                staging_id, lat, lon,
                temp_c, temp_f,
                wind_kmh, wind_mph,
                condition, obs_time
            ))
            transformed_count += 1

        conn.commit()
        print(f"✅ Success: Transformed and loaded {transformed_count} record(s) into analytics_weather!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Transformation failed: {e}")

if __name__ == "__main__":
    transform_and_load()